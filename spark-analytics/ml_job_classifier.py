#!/usr/bin/env python3
"""
Job Classification using MLlib Random Forest
Categorizes jobs into role categories (e.g., Engineer, Designer, Product Manager, etc.)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import re


class JobClassifier:
    """Classify jobs into categories using Random Forest"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        
        # Define job categories based on title keywords
        self.job_categories = {
            'Software Engineer': ['engineer', 'developer', 'programmer', 'software', 'fullstack', 'full-stack', 'backend', 'frontend', 'devops'],
            'Data Scientist': ['data scientist', 'data engineer', 'data analyst', 'ml engineer', 'ai engineer', 'machine learning'],
            'Product Manager': ['product manager', 'product', 'pm', 'product owner'],
            'Designer': ['designer', 'design', 'ui/ux', 'ux', 'ui'],
            'Marketing': ['marketing', 'growth', 'marketer', 'content', 'seo'],
            'Sales': ['sales', 'account executive', 'account manager', 'business development'],
            'Operations': ['operations', 'ops', 'operations manager', 'coo'],
            'Other': []  # Default category
        }
        
    def categorize_job_title(self, title):
        """Map job title to category based on keywords"""
        if not title:
            return 'Other'
        
        title_lower = title.lower()
        
        # Check each category (ordered by specificity)
        for category, keywords in self.job_categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in title_lower:
                    return category
        
        return 'Other'
    
    def prepare_features(self, df):
        """Prepare features from job title and description"""
        # Add category label
        categorize_udf = udf(self.categorize_job_title, StringType())
        df = df.withColumn("job_category", categorize_udf(col("title")))
        
        # Combine title and description for feature extraction
        df = df.withColumn(
            "text_features",
            concat_ws(" ", 
                coalesce(col("title"), lit("")),
                coalesce(col("description_text"), lit(""))
            )
        )
        
        # Clean text
        df = df.withColumn(
            "text_features",
            regexp_replace(regexp_replace(col("text_features"), "[^a-zA-Z0-9\\s]", " "), "\\s+", " ")
        )
        
        return df
    
    def train_classifier(self, df, test_size=0.2):
        """Train Random Forest classifier"""
        print("\n🎯 Training Job Classifier (Random Forest)...")
        
        # Prepare data
        df_prepared = self.prepare_features(df)
        
        # Filter out rows with missing text
        df_prepared = df_prepared.filter(
            col("text_features").isNotNull() & 
            (length(col("text_features")) > 10)
        )
        
        if df_prepared.count() == 0:
            print("❌ No valid data for classification")
            return None, None
        
        print(f"📊 Prepared {df_prepared.count()} jobs for classification")
        
        # Show category distribution
        category_dist = df_prepared.groupBy("job_category").count().orderBy(desc("count"))
        print("\n📈 Category Distribution:")
        for row in category_dist.collect():
            print(f"   • {row['job_category']}: {row['count']} jobs")
        
        # Create label indexer
        label_indexer = StringIndexer(
            inputCol="job_category",
            outputCol="label",
            handleInvalid="skip"
        )
        
        # Text processing pipeline
        tokenizer = Tokenizer(inputCol="text_features", outputCol="words")
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
        cv = CountVectorizer(
            inputCol="filtered_words",
            outputCol="text_features_vec",
            vocabSize=5000,
            minDF=2.0
        )
        
        # Create additional features from job metadata
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
        
        # Combine features
        assembler = VectorAssembler(
            inputCols=["text_features_vec", "location_index", "experience_index"],
            outputCol="features"
        )
        
        # Random Forest classifier
        rf = RandomForestClassifier(
            labelCol="label",
            featuresCol="features",
            numTrees=100,
            maxDepth=10,
            seed=42
        )
        
        # Build pipeline
        pipeline = Pipeline(stages=[
            label_indexer,
            tokenizer,
            remover,
            cv,
            location_indexer,
            experience_indexer,
            assembler,
            rf
        ])
        
        # Split data
        train_df, test_df = df_prepared.randomSplit([1.0 - test_size, test_size], seed=42)
        
        print(f"\n📚 Training on {train_df.count()} samples, testing on {test_df.count()} samples")
        
        # Train model
        model = pipeline.fit(train_df)
        
        # Make predictions
        predictions = model.transform(test_df)
        
        # Evaluate
        evaluator = MulticlassClassificationEvaluator(
            labelCol="label",
            predictionCol="prediction",
            metricName="accuracy"
        )
        
        accuracy = evaluator.evaluate(predictions)
        print(f"\n✅ Model Accuracy: {accuracy:.2%}")
        
        # Show prediction distribution
        prediction_labels = predictions.select("prediction", "job_category").collect()
        print(f"\n📊 Sample Predictions:")
        for i, row in enumerate(prediction_labels[:10]):
            print(f"   Prediction {row['prediction']:.0f} -> Category: {row['job_category']}")
        
        return model, predictions
    
    def classify_jobs(self, model, df):
        """Classify jobs using trained model"""
        if model is None:
            print("❌ No trained model available")
            return df
        
        print("\n🔮 Classifying jobs...")
        
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        # Make predictions
        predictions = model.transform(df_prepared)
        
        # Map predictions back to category names
        # Get category to index mapping
        label_indexer = model.stages[0]
        
        # Add readable predictions
        predictions = predictions.withColumn(
            "predicted_category_index",
            col("prediction").cast(IntegerType())
        )
        
        # Count classifications
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
        # Load data
        df = loader.load_postings()
        
        if df and df.count() > 0:
            classifier = JobClassifier(loader.spark)
            model, predictions = classifier.train_classifier(df)
            
            if model:
                print("\n✅ Job classification completed successfully!")
        else:
            print("📭 No data available for classification")
    
    finally:
        loader.cleanup()


if __name__ == "__main__":
    main()

