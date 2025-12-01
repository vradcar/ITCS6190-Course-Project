#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, lit, monotonically_increasing_id
from pyspark.ml.feature import RegexTokenizer, CountVectorizer, IDF
from sklearn.preprocessing import normalize

from data_loader import DataLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
USERS_FILE = os.path.join(DATA_DIR, "users.csv")

TRAIN_FRACTION = 0.5

TEXT_COLS = [
    "title",
    "description_text",
    "location",
    "formatted_work_type",
    "application_type",
    "formatted_experience_level"
]

HIGH_RATING_THRESHOLD = 3.0
TOP_K_PER_TRAIN = 10
TOP_N_RECOMMENDATIONS = 5


def main():
    spark = SparkSession.builder \
        .appName("SparkTFIDFRecommender") \
        .config("spark.driver.memory", "6g") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()

    loader = DataLoader(spark_session=spark)
    postings = loader.load_postings()
    print("✔ Loaded postings from data_loader.py")

    postings = postings.orderBy("job_id").withColumn(
        "row_idx",
        monotonically_increasing_id()
    )

    total_rows = postings.count()
    train_rows = int(total_rows * TRAIN_FRACTION)

    train = postings.filter(col("row_idx") < train_rows)
    test = postings.filter(col("row_idx") >= train_rows)

    print(f"Train count = {train.count()}, Test count = {test.count()}")

    for c in TEXT_COLS:
        if c not in train.columns:
            train = train.withColumn(c, lit(""))
        if c not in test.columns:
            test = test.withColumn(c, lit(""))

    train = train.withColumn("text", concat_ws(" ", *[col(c) for c in TEXT_COLS]))
    test = test.withColumn("text", concat_ws(" ", *[col(c) for c in TEXT_COLS]))

    tokenizer = RegexTokenizer(inputCol="text", outputCol="tokens", pattern="\\W+")
    train_tok = tokenizer.transform(train)
    test_tok = tokenizer.transform(test)

    print("Fitting CountVectorizer...")
    combined_tokens = train_tok.select("tokens").union(test_tok.select("tokens"))
    cv = CountVectorizer(inputCol="tokens", outputCol="raw_features", vocabSize=2000)
    cv_model = cv.fit(combined_tokens)

    train_cv = cv_model.transform(train_tok)
    test_cv = cv_model.transform(test_tok)

    combined_cv = train_cv.select("raw_features").union(test_cv.select("raw_features"))

    print("Fitting IDF...")
    idf = IDF(inputCol="raw_features", outputCol="features")
    idf_model = idf.fit(combined_cv)

    train_tfidf = idf_model.transform(train_cv).select("job_id", "row_idx", "features")
    test_tfidf = idf_model.transform(test_cv).select("job_id", "row_idx", "features")

    print("Collecting train vectors...")
    train_collected = train_tfidf.orderBy("row_idx").select("job_id", "features").collect()
    train_vecs = [(int(r["job_id"]), r["features"].toArray()) for r in train_collected]
    del train_collected

    print("Collecting test vectors...")
    test_collected = test_tfidf.orderBy("row_idx").select("job_id", "features").collect()
    test_vecs = [(int(r["job_id"]), r["features"].toArray()) for r in test_collected]
    del test_collected

    if len(train_vecs) == 0:
        raise RuntimeError("❌ ERROR: train_vecs is EMPTY.")

    if len(test_vecs) == 0:
        raise RuntimeError("❌ ERROR: test_vecs is EMPTY.")

    print(f"Train vectors: {len(train_vecs)}, Test vectors: {len(test_vecs)}")

    print("Building normalized matrices...")
    train_job_ids = [jid for jid, _ in train_vecs]
    test_job_ids = [jid for jid, _ in test_vecs]

    train_matrix = np.vstack([vec for _, vec in train_vecs])
    del train_vecs
    
    test_matrix = np.vstack([vec for _, vec in test_vecs])
    del test_vecs

    print("Normalizing matrices...")
    train_norm = normalize(train_matrix)
    del train_matrix
    
    test_norm = normalize(test_matrix)
    del test_matrix

    print("Loading users and metadata...")
    users = pd.read_csv(USERS_FILE)
    print("✔ Loaded users.csv")

    print("Building job description map...")
    all_desc_map = {}
    for row in postings.select("job_id", "description_text").collect():
        job_id = int(row["job_id"])
        desc = row["description_text"]
        if desc and isinstance(desc, str) and desc.strip():
            all_desc_map[job_id] = desc.strip()
        else:
            all_desc_map[job_id] = "No description available"

    train_jobid_to_rowidx = {
        int(r["job_id"]): int(r["row_idx"])
        for r in train_tfidf.select("job_id", "row_idx").collect()
    }

    recommendations = []
    all_recommended_jobs = set()

    print(f"Generating recommendations for {len(users['user_id'].unique())} users...")
    for idx, (user_id, group) in enumerate(users.groupby("user_id")):
        if idx % 100 == 0:
            print(f"Processing user {idx}...")
            
        liked_train_indices = []

        for _, r in group.iterrows():
            if r["rating"] >= HIGH_RATING_THRESHOLD:
                raw_idx = int(r["job_index"])
                train_idx = None

                if 0 <= raw_idx < len(train_job_ids):
                    train_idx = raw_idx
                else:
                    train_idx = train_jobid_to_rowidx.get(raw_idx)

                if train_idx is not None:
                    liked_train_indices.append((train_idx, r["rating"]))
        
        if not liked_train_indices:
            recommendations.append({
                "user_id": user_id, 
                "recommended_jobs": "No recommendations available",
                "num_recommendations": 0
            })
            continue

        scores = {}
        for train_idx, rating in liked_train_indices:
            similarities = np.dot(train_norm[train_idx:train_idx+1], test_norm.T).flatten()
            similar_test_indices = np.argsort(similarities)[-TOP_K_PER_TRAIN:][::-1]
            
            for test_i in similar_test_indices:
                weight = similarities[test_i] * (rating / 5.0)
                scores[test_i] = scores.get(test_i, 0.0) + weight

        for test_i in scores:
            if test_job_ids[test_i] in all_recommended_jobs:
                scores[test_i] *= 0.95

        ranked = sorted(scores.items(), key=lambda x: (x[1], np.random.random()), reverse=True)
        topN = ranked[:TOP_N_RECOMMENDATIONS]

        recommended_ids = [test_job_ids[idx] for idx, _ in topN]
        recommended_jobs = []
        
        for job_id in recommended_ids:
            desc = all_desc_map.get(job_id, "No description available")
            recommended_jobs.append(f"{job_id}: {desc}")
            all_recommended_jobs.add(job_id)

        recommendations.append({
            "user_id": user_id, 
            "recommended_jobs": " | ".join(recommended_jobs)
        })

    out_path = os.path.join(DATA_DIR, "recommendations.csv")
    pd.DataFrame(recommendations).to_csv(out_path, index=False)
    print(f"✔ Saved recommendations to: {out_path}")

    spark.stop()


if __name__ == "__main__":
    main()