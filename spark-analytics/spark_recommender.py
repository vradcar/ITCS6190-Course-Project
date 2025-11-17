#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, concat_ws, lit, row_number
from pyspark.ml.feature import RegexTokenizer, CountVectorizer, IDF
from sklearn.preprocessing import normalize

# ---------------------------------------------------------
# Import postings loader from the SAME folder
# ---------------------------------------------------------
from data_loader import DataLoader

# ---------------------------------------------------------
# Paths for Codespaces repo layout
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))

USERS_FILE = os.path.join(DATA_DIR, "users.csv")

TRAIN_ROWS = 1000
TEST_ROWS = 1000

TEXT_COLS = [
    "title",
    "description_text",
    "location",
    "job_type",
    "application_type",
    "experience_level"
]

HIGH_RATING_THRESHOLD = 3.0
TOP_K_PER_TRAIN = 10
TOP_N_RECOMMENDATIONS = 5


def main():

    # -----------------------------
    # Start Spark
    # -----------------------------
    spark = SparkSession.builder \
        .appName("SparkTFIDFRecommender") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

    # --------------------------------------------------------
    # Use your DataLoader (automatically finds postings_cleaned.csv)
    # --------------------------------------------------------
    loader = DataLoader(spark_session=spark)
    postings = loader.load_postings()

    print("✔ Loaded postings from data_loader.py")

    # --------------------------------------------------------
    # Add row indices (0-based)
    # --------------------------------------------------------
    window = Window.orderBy(lit(1))
    postings = postings.withColumn("row_temp", row_number().over(window))
    postings = postings.withColumn("row_idx", col("row_temp") - 1).drop("row_temp")

    # --------------------------------------------------------
    # Train/test split
    # --------------------------------------------------------
    train = postings.filter((col("row_idx") >= 0) & (col("row_idx") < TRAIN_ROWS))
    test  = postings.filter((col("row_idx") >= TRAIN_ROWS) & (col("row_idx") < TRAIN_ROWS + TEST_ROWS))

    print(f"Train count = {train.count()}, Test count = {test.count()}")

    # --------------------------------------------------------
    # Build text column
    # --------------------------------------------------------
    for c in TEXT_COLS:
        if c not in postings.columns:
            postings = postings.withColumn(c, lit(""))

    train = train.withColumn("text", concat_ws(" ", *[col(c) for c in TEXT_COLS]))
    test  = test.withColumn("text", concat_ws(" ", *[col(c) for c in TEXT_COLS]))

    # --------------------------------------------------------
    # TF–IDF Pipeline (Spark)
    # --------------------------------------------------------
    tokenizer = RegexTokenizer(inputCol="text", outputCol="tokens", pattern="\\W+")
    train_tok = tokenizer.transform(train)
    test_tok = tokenizer.transform(test)

    combined_tokens = train_tok.select("tokens").union(test_tok.select("tokens"))

    cv = CountVectorizer(inputCol="tokens", outputCol="raw_features", vocabSize=5000)
    cv_model = cv.fit(combined_tokens)

    train_cv = cv_model.transform(train_tok)
    test_cv  = cv_model.transform(test_tok)

    combined_cv = train_cv.select("raw_features").union(test_cv.select("raw_features"))

    idf = IDF(inputCol="raw_features", outputCol="features")
    idf_model = idf.fit(combined_cv)

    train_tfidf = idf_model.transform(train_cv).select("job_id", "row_idx", "features")
    test_tfidf  = idf_model.transform(test_cv).select("job_id", "row_idx", "features")

    # --------------------------------------------------------
    # Collect to numpy for similarity computation
    # --------------------------------------------------------
    train_vecs = train_tfidf.orderBy("row_idx").rdd.map(lambda r: (int(r["job_id"]), r["features"].toArray())).collect()
    test_vecs  = test_tfidf.orderBy("row_idx").rdd.map(lambda r: (int(r["job_id"]), r["features"].toArray())).collect()

    train_job_ids = [jid for jid, vec in train_vecs]
    test_job_ids  = [jid for jid, vec in test_vecs]

    train_matrix = np.vstack([vec for _, vec in train_vecs])
    test_matrix  = np.vstack([vec for _, vec in test_vecs])

    train_norm = normalize(train_matrix)
    test_norm  = normalize(test_matrix)

    sim_matrix = np.dot(train_norm, test_norm.T)

    # --------------------------------------------------------
    # Load users.csv (only file loaded here)
    # --------------------------------------------------------
    users = pd.read_csv(USERS_FILE)
    print("✔ Loaded users.csv")

    # --------------------------------------------------------
    # Recommendation Logic
    # --------------------------------------------------------
    recommendations = []

    for user_id, group in users.groupby("user_id"):

        liked_train_indices = []

        for _, r in group.iterrows():

            if r["rating"] >= HIGH_RATING_THRESHOLD:

                job_idx = int(r["job_index"])  # this is a 0-based row index

                if 0 <= job_idx < TRAIN_ROWS:
                    liked_train_indices.append((job_idx, r["rating"]))

        # If no training likes, give empty list
        if not liked_train_indices:
            recommendations.append({
                "user_id": user_id,
                "recommended_jobs": []
            })
            continue

        scores = {}

        # Score each test job based on similarity to liked train jobs
        for train_idx, rating in liked_train_indices:

            similar_test_indices = np.argsort(sim_matrix[train_idx])[-TOP_K_PER_TRAIN:][::-1]

            for test_i in similar_test_indices:
                weight = sim_matrix[train_idx][test_i] * (rating / 5.0)
                scores[test_i] = max(scores.get(test_i, 0), weight)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        topN = ranked[:TOP_N_RECOMMENDATIONS]

        recommended_ids = [test_job_ids[idx] for idx, _ in topN]

        recommendations.append({
            "user_id": user_id,
            "recommended_jobs": recommended_ids
        })

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------
    out_path = os.path.join(DATA_DIR, "recommendations.csv")
    pd.DataFrame(recommendations).to_csv(out_path, index=False)

    print(f"✔ Saved recommendations to: {out_path}")

    spark.stop()


if __name__ == "__main__":
    main()