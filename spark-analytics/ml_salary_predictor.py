#!/usr/bin/env python3
"""
Salary Prediction using MLlib Linear Regression
Predicts salary based on skills, experience level, location, and job type
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, StringIndexer, VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
import re


class SalaryPredictor:
    """Predict salary using Linear Regression"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        
        # Common high-value skills for feature engineering
        self.high_value_skills = [
            "python", "javascript", "react", "node.js", "typescript", "java", "go", "rust",
            "aws", "kubernetes", "docker", "postgresql", "mongodb", "redis",
            "machine learning", "ai", "data science", "blockchain", "security",
            "leadership", "management", "architecture"
        ]
    
    def extract_salary_from_text(self, salary_text):
        """Extract numeric salary from text field"""
        if not salary_text:
            return None
        
        # Try to extract from JSON-like structure
        json_match = re.search(r'"minValue":\s*(\d+)', salary_text)
        if json_match:
            return int(json_match.group(1))
        
        # Try to extract dollar amounts
        dollar_match = re.search(r'\$(\d{1,3}(?:,?\d{3})*)', salary_text)
        if dollar_match:
            return int(dollar_match.group(1).replace(',', ''))
        
        # Try to extract numeric ranges
        range_match = re.search(r'(\d{1,3}(?:,?\d{3})*)\s*-\s*(\d{1,3}(?:,?\d{3})*)', salary_text)
        if range_match:
            min_val = int(range_match.group(1).replace(',', ''))
            max_val = int(range_match.group(2).replace(',', ''))
            return (min_val + max_val) // 2
        
        return None
    
    def extract_experience_years(self, experience_level, description):
        """Extract years of experience from experience level and description"""
        if not experience_level and not description:
            return 0
        
        text = f"{experience_level or ''} {description or ''}".lower()
        
        # Pattern matching for years
        year_patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'(\d+)\+?\s*yr\.?'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                return min(int(match.group(1)), 15)  # Cap at 15 years
        
        # Level-based estimation
        if experience_level:
            level_lower = experience_level.lower()
            if 'senior' in level_lower or 'lead' in level_lower or 'principal' in level_lower:
                return 8
            elif 'mid' in level_lower or 'intermediate' in level_lower:
                return 5
            elif 'junior' in level_lower or 'entry' in level_lower or 'associate' in level_lower:
                return 2
        
        return 3  # Default
    
    def prepare_features(self, df):
        """Prepare features for salary prediction"""
        print("\n💰 Preparing salary prediction features...")
        
        # Extract salary as target variable
        extract_salary_udf = udf(self.extract_salary_from_text, IntegerType())
        df = df.withColumn("salary_numeric", extract_salary_udf(col("salary")))
        
        # Filter jobs with valid salary
        df_with_salary = df.filter(
            col("salary_numeric").isNotNull() & 
            (col("salary_numeric") > 30000) & 
            (col("salary_numeric") < 500000)  # Reasonable range
        )
        
        if df_with_salary.count() == 0:
            print("⚠️  No jobs with valid salary data found")
            return None
        
        print(f"📊 Found {df_with_salary.count()} jobs with salary information")
        
        # Extract experience years
        extract_exp_udf = udf(
            lambda exp, desc: self.extract_experience_years(exp, desc),
            IntegerType()
        )
        df_with_salary = df_with_salary.withColumn(
            "experience_years",
            extract_exp_udf(col("experience_level"), col("description_text"))
        )
        
        # Check for remote work
        df_with_salary = df_with_salary.withColumn(
            "is_remote",
            when(
                col("location").rlike("(?i)remote") |
                col("description_text").rlike("(?i)remote"),
                1.0
            ).otherwise(0.0)
        )
        
        # Extract skill features (count high-value skills mentioned)
        skill_counts = []
        for skill in self.high_value_skills:
            df_with_salary = df_with_salary.withColumn(
                f"has_{skill.replace(' ', '_').replace('.', '_')}",
                when(
                    lower(col("description_text")).rlike(f"(?i)\\b{skill}\\b") |
                    lower(col("title")).rlike(f"(?i)\\b{skill}\\b"),
                    1.0
                ).otherwise(0.0)
            )
            skill_counts.append(f"has_{skill.replace(' ', '_').replace('.', '_')}")
        
        # Location encoding (top locations)
        location_indexer = StringIndexer(
            inputCol="location",
            outputCol="location_index",
            handleInvalid="keep"
        )
        
        # Job type encoding
        job_type_indexer = StringIndexer(
            inputCol="job_type",
            outputCol="job_type_index",
            handleInvalid="keep"
        )
        
        # Experience level encoding
        experience_indexer = StringIndexer(
            inputCol="experience_level",
            outputCol="experience_level_index",
            handleInvalid="keep"
        )
        
        # Text features from description
        df_with_salary = df_with_salary.withColumn(
            "description_clean",
            regexp_replace(
                regexp_replace(lower(coalesce(col("description_text"), lit(""))), "[^a-zA-Z0-9\\s]", " "),
                "\\s+", " "
            )
        )
        
        tokenizer = Tokenizer(inputCol="description_clean", outputCol="words")
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
        cv = CountVectorizer(
            inputCol="filtered_words",
            outputCol="description_vec",
            vocabSize=1000,
            minDF=2.0
        )
        
        # Combine all features
        feature_cols = [
            "location_index", "job_type_index", "experience_level_index",
            "experience_years", "is_remote", "description_vec"
        ] + skill_counts
        
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features"
        )
        
        # Build pipeline
        pipeline = Pipeline(stages=[
            location_indexer,
            job_type_indexer,
            experience_indexer,
            tokenizer,
            remover,
            cv,
            assembler
        ])
        
        # Fit pipeline to get transformed data
        pipeline_model = pipeline.fit(df_with_salary)
        df_transformed = pipeline_model.transform(df_with_salary)
        
        return df_transformed, pipeline_model
    
    def train_predictor(self, df, test_size=0.2):
        """Train Linear Regression model for salary prediction"""
        print("\n🎯 Training Salary Predictor (Linear Regression)...")
        
        # Prepare features
        df_prepared, feature_pipeline = self.prepare_features(df)
        
        if df_prepared is None:
            return None, None, None
        
        # Split data
        train_df, test_df = df_prepared.randomSplit([1.0 - test_size, test_size], seed=42)
        
        print(f"\n📚 Training on {train_df.count()} samples, testing on {test_df.count()} samples")
        
        # Show salary statistics
        salary_stats = train_df.agg(
            avg("salary_numeric").alias("avg_salary"),
            min("salary_numeric").alias("min_salary"),
            max("salary_numeric").alias("max_salary"),
            stddev("salary_numeric").alias("std_salary")
        ).collect()[0]
        
        print(f"\n💰 Salary Statistics (Training Set):")
        print(f"   • Average: ${salary_stats['avg_salary']:,.0f}")
        print(f"   • Range: ${salary_stats['min_salary']:,.0f} - ${salary_stats['max_salary']:,.0f}")
        print(f"   • Std Dev: ${salary_stats['std_salary']:,.0f}")
        
        # Train Linear Regression
        lr = LinearRegression(
            featuresCol="features",
            labelCol="salary_numeric",
            maxIter=100,
            regParam=0.01,
            elasticNetParam=0.5
        )
        
        print("\n🔄 Training model...")
        lr_model = lr.fit(train_df)
        
        # Make predictions
        predictions = lr_model.transform(test_df)
        
        # Evaluate
        evaluator = RegressionEvaluator(
            labelCol="salary_numeric",
            predictionCol="prediction",
            metricName="rmse"
        )
        
        rmse = evaluator.evaluate(predictions)
        r2 = evaluator.setMetricName("r2").evaluate(predictions)
        
        print(f"\n✅ Model Performance:")
        print(f"   • RMSE: ${rmse:,.0f}")
        print(f"   • R² Score: {r2:.2%}")
        
        # Show sample predictions
        print(f"\n📊 Sample Predictions:")
        sample_predictions = predictions.select(
            "title", "salary_numeric", "prediction"
        ).limit(10).collect()
        
        for row in sample_predictions:
            actual = row['salary_numeric']
            predicted = row['prediction']
            error = abs(actual - predicted)
            error_pct = (error / actual * 100) if actual > 0 else 0
            print(f"   • Actual: ${actual:,.0f}, Predicted: ${predicted:,.0f} (Error: {error_pct:.1f}%)")
        
        return lr_model, feature_pipeline, predictions
    
    def predict_salaries(self, model, feature_pipeline, df):
        """Predict salaries for new jobs"""
        if model is None or feature_pipeline is None:
            print("❌ No trained model available")
            return df
        
        print("\n🔮 Predicting salaries...")
        
        # Prepare features using the same pipeline
        df_prepared = self.prepare_features(df)[0] if df.filter(col("salary").isNotNull()).count() > 0 else None
        
        if df_prepared is None:
            # Apply feature pipeline even without salary data
            df_prepared = feature_pipeline.transform(df)
        
        # Make predictions
        predictions = model.transform(df_prepared)
        
        # Add predicted salary column
        predictions = predictions.withColumn(
            "predicted_salary",
            col("prediction")
        )
        
        # Show prediction statistics
        if predictions.filter(col("predicted_salary").isNotNull()).count() > 0:
            pred_stats = predictions.agg(
                avg("predicted_salary").alias("avg_predicted"),
                min("predicted_salary").alias("min_predicted"),
                max("predicted_salary").alias("max_predicted")
            ).collect()[0]
            
            print(f"\n💰 Predicted Salary Statistics:")
            print(f"   • Average: ${pred_stats['avg_predicted']:,.0f}")
            print(f"   • Range: ${pred_stats['min_predicted']:,.0f} - ${pred_stats['max_predicted']:,.0f}")
        
        return predictions


def main():
    """Standalone testing"""
    from data_loader import DataLoader
    
    loader = DataLoader()
    
    try:
        # Load data
        df = loader.load_postings()
        
        if df and df.count() > 0:
            predictor = SalaryPredictor(loader.spark)
            model, feature_pipeline, predictions = predictor.train_predictor(df)
            
            if model:
                print("\n✅ Salary prediction completed successfully!")
        else:
            print("📭 No data available for salary prediction")
    
    finally:
        loader.cleanup()


if __name__ == "__main__":
    main()

