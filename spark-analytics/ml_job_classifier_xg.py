#!/usr/bin/env python3
"""
Job Classification using XGBoost (XGBoost4J-Spark)
Categorizes jobs into role categories (Engineer, Designer, PM, etc.)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Tokenizer, StopWordsRemover, CountVectorizer,
    StringIndexer, VectorAssembler
)
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# NEW IMPORT FOR XGBOOST
from xgboost.spark import SparkXGBClassifier

import re


class JobClassifier:
    """Classify jobs into categories using XGBoost"""

    def __init__(self, spark_session):
        self.spark = spark_session

    @staticmethod
    def categorize_job_title(title):
        """Map job title to category based on keywords"""
        if not title:
            return 'Other'

        title_lower = title.lower()

        job_categories = {
            'Software Engineer': ['engineer', 'developer', 'programmer', 'software',
                                  'fullstack', 'full-stack', 'backend', 'frontend', 'devops'],
            'Data Scientist': ['data scientist', 'data engineer', 'data analyst',
                               'ml engineer', 'ai engineer', 'machine learning'],
            'Product Manager': ['product manager', 'product', 'pm', 'product owner'],
            'Designer': ['designer', 'design', 'ui/ux', 'ux', 'ui'],
            'Marketing': ['marketing', 'growth', 'marketer', 'content', 'seo'],
            'Sales': ['sales', 'account executive', 'account manager', 'business development'],
            'Operations': ['operations', 'ops', 'operations manager', 'coo'],
            'Other': []
        }

        for category, keywords in job_categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in title_lower:
                    return category

        return 'Other'

    def prepare_features(self, df):
        """Prepare features from job title and description"""
        categorize_udf = udf(JobClassifier.categorize_job_title, StringType())
        df = df.withColumn("job_category", categorize_udf(col("title")))

        df = df.withColumn(
            "text_features",
            concat_ws(" ",
                coalesce(col("title"), lit("")),
                coalesce(col("description_text"), lit(""))
            )
        )

        df = df.withColumn(
            "text_features",
            regexp_replace(regexp_replace(col("text_features"),
                                          "[^a-zA-Z0-9\\s]", " "), "\\s+", " ")
        )

        return df

    def train_classifier(self, df, test_size=0.2):
        """Train XGBoost classifier"""
        print("\n🎯 Training Job Classifier (XGBoost)...")

        df_prepared = self.prepare_features(df)
        df_prepared = df_prepared.filter(
            col("text_features").isNotNull() &
            (length(col("text_features")) > 10)
        )

        if df_prepared.count() == 0:
            print("❌ No valid data for classification")
            return None, None

        print(f"📊 Prepared {df_prepared.count()} jobs for classification")

        category_dist = df_prepared.groupBy("job_category").count().orderBy(desc("count"))
        print("\n📈 Category Distribution:")
        for row in category_dist.collect():
            print(f"   • {row['job_category']}: {row['count']} jobs")

        label_indexer = StringIndexer(
            inputCol="job_category",
            outputCol="label",
            handleInvalid="skip"
        )

        tokenizer = Tokenizer(inputCol="text_features", outputCol="words")
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")

        cv = CountVectorizer(
            inputCol="filtered_words",
            outputCol="text_features_vec",
            vocabSize=5000,
            minDF=2.0
        )

        location_indexer = StringIndexer(
            inputCol="location",
            outputCol="location_index",
            handleInvalid="keep"
        )

        experience_indexer = StringIndexer(
            inputCol="experience_level",
            outputCol="experience_index",
            handleInvalid="keep"
        )

        assembler = VectorAssembler(
            inputCols=["text_features_vec", "experience_index"],
            outputCol="features"
        )

        # ----------------------------------------------------------------------
        # ⭐ NEW XGBOOST MODEL ⭐
        # ----------------------------------------------------------------------
        xgb = SparkXGBClassifier(
            label_col="label",
            features_col="features",
            num_class=8,             # number of job categories
            eta=0.1,
            max_depth=6,
            n_estimators=50,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            seed=42
        )
        # ----------------------------------------------------------------------

        pipeline = Pipeline(stages=[
            label_indexer,
            tokenizer,
            remover,
            cv,
            location_indexer,
            experience_indexer,
            assembler,
            xgb
        ])

        train_df, test_df = df_prepared.randomSplit([1 - test_size, test_size], seed=42)

        print(f"\n📚 Training on {train_df.count()} samples, testing on {test_df.count()} samples")

        model = pipeline.fit(train_df)
        predictions = model.transform(test_df)

        evaluator = MulticlassClassificationEvaluator(
            labelCol="label",
            predictionCol="prediction",
            metricName="accuracy"
        )

        accuracy = evaluator.evaluate(predictions)
        print(f"\n✅ Model Accuracy: {accuracy:.2%}")

        print("\n📊 Sample Predictions:")
        sample = predictions.select("prediction", "job_category").limit(10).collect()
        for row in sample:
            print(f"   Prediction {int(row['prediction'])} -> Category: {row['job_category']}")

        return model, predictions

    def classify_jobs(self, model, df):
        """Classify jobs using trained XGBoost model"""
        if model is None:
            print("❌ No trained model available")
            return df

        print("\n🔮 Classifying jobs...")

        df_prepared = self.prepare_features(df)
        predictions = model.transform(df_prepared)

        predictions = predictions.withColumn(
            "predicted_category_index",
            col("prediction").cast(IntegerType())
        )

        if predictions.count() > 0:
            print(f"\n📊 Classification Results:")
            category_counts = predictions.groupBy("job_category").count().orderBy(desc("count"))
            for row in category_counts.collect():
                print(f"   • {row['job_category']}: {row['count']} jobs")

        return predictions


def main():
        """Standalone testing"""
        from data_loader import DataLoader

        loader = DataLoader()

        try:
            df = loader.load_postings()

            if df and df.count() > 0:
                classifier = JobClassifier(loader.spark)
                model, predictions = classifier.train_classifier(df)

                if model:
                    print("\n✅ Job classification via XGBoost completed successfully!")
            else:
                print("📭 No data available for classification")

        finally:
            loader.cleanup()


if __name__ == "__main__":
    main()