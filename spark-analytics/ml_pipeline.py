#!/usr/bin/env python3
"""
ML Pipeline Integration
Integrates all MLlib features: Job Classification, Salary Prediction, 
Skill Extraction, Recommendation System, and Trend Forecasting
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import argparse
import os
import shutil
from datetime import datetime, timedelta

# Import ML modules
from ml_job_classifier import JobClassifier
from ml_skill_extractor import SkillExtractor
from ml_recommender import JobRecommender
from ml_salary_predictor import SalaryPredictor

# Import data loader
from data_loader import DataLoader


class MLPipeline:
    """Complete ML pipeline integrating all MLlib features"""
    
    def __init__(self):
        """Initialize ML pipeline with Spark session"""
        # Initialize data loader
        self.data_loader = DataLoader()
        self.spark = self.data_loader.spark
        
        # Add ML modules to Spark context for workers to resolve ModuleNotFoundError
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.spark.sparkContext.addPyFile(os.path.join(current_dir, "ml_job_classifier.py"))
        self.spark.sparkContext.addPyFile(os.path.join(current_dir, "ml_skill_extractor.py"))
        self.spark.sparkContext.addPyFile(os.path.join(current_dir, "ml_recommender.py"))
        self.spark.sparkContext.addPyFile(os.path.join(current_dir, "ml_salary_predictor.py"))

        # Initialize ML components
        self.job_classifier = JobClassifier(self.spark)
        self.skill_extractor = SkillExtractor(self.spark)
        self.job_recommender = JobRecommender(self.spark)
        self.salary_predictor = SalaryPredictor(self.spark)
        
        print("✅ ML Pipeline initialized")
    
    def load_data(self, date_str=None, days_back=7):
        """Load job data from CSV files"""
        print("\n📥 Loading job data from CSV files...")
        
        # Load postings data
        df = self.data_loader.load_postings()
        
        # Sample for stability in local mode
        if df:
            sample_limit = 10000
            print(f"⚠️  Sampling data to {sample_limit} rows for stability...")
            df = df.limit(sample_limit)
        
        if df and df.count() > 0:
            print(f"✅ Loaded {df.count()} job postings (sampled)")
            return df
        
        print("⚠️  No data loaded")
        return None
    
    def run_job_classification(self, df):
        """Run job classification using multiple models"""
        print("\n" + "="*60)
        print("🎯 Job Classification (Model Comparison)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for classification")
            return None, None
        
        # This now runs the comparison logic
        model, predictions = self.job_classifier.train_classifier(df)
        
        if model:
            # Classify all jobs
            classified_df = self.job_classifier.classify_jobs(model, df)
            return model, classified_df
        
        return None, None

    def run_salary_prediction(self, df):
        """Run salary prediction"""
        print("\n" + "="*60)
        print("💰 Salary Prediction (Linear Regression)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for salary prediction")
            return None, None
            
        model, feature_pipeline, predictions = self.salary_predictor.train_predictor(df)
        return model, predictions, feature_pipeline
    
    def run_skill_extraction(self, df):
        """Run skill extraction using NLP"""
        print("\n" + "="*60)
        print("🛠️  Skill Extraction (NLP)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for skill extraction")
            return None, None, None
        
        # Extract top skills
        top_skills = self.skill_extractor.extract_top_skills(df, top_n=20)
        
        # Analyze skill combinations
        combinations = self.skill_extractor.analyze_skill_combinations(df)
        
        # Cluster jobs by skills
        clustered_df, cluster_model, tfidf_model = self.skill_extractor.cluster_jobs_by_skills(
            df, n_clusters=5
        )
        
        return clustered_df, cluster_model, tfidf_model
    
    def run_recommendation_system(self, df):
        """Run recommendation system using Collaborative Filtering"""
        print("\n" + "="*60)
        print("🔮 Job Recommendation (Collaborative Filtering - ALS)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for recommendations")
            return None, None, None
        
        model, job_indexer, predictions = self.job_recommender.train_recommender(
            df, num_users=100, implicit_prefs=True
        )
        
        if model:
            # Generate recommendations for all users
            recommendations = self.job_recommender.recommend_top_jobs_for_all_users(
                model, num_users=100, num_recommendations=10
            )
            return model, job_indexer, recommendations
        
        return None, None, None
    
    def run_full_pipeline(self, date_str=None, days_back=7, components=None):
        """Run complete ML pipeline with all components"""
        print("\n" + "="*70)
        print("🚀 ML Pipeline - Complete Analysis")
        print("="*70)
        
        # Load data
        df = self.load_data(date_str, days_back)
        
        if df is None or df.count() == 0:
            print("\n❌ No data available. Exiting pipeline.")
            return
        
        print(f"\n📊 Starting ML analysis on {df.count()} jobs")
        
        results = {}
        
        # Determine which components to run
        if components is None:
            components = ['classification', 'skills', 'recommendation', 'salary']
        
        # 1. Job Classification
        if 'classification' in components:
            try:
                class_model, classified_df = self.run_job_classification(df)
                results['classification'] = {
                    'model': class_model,
                    'predictions': classified_df
                }
            except Exception as e:
                print(f"❌ Error in job classification: {e}")
        
        # 2. Salary Prediction
        if 'salary' in components:
            try:
                # Updated to unpack 3 values (model, predictions, pipeline)
                salary_model, salary_preds, salary_pipeline = self.run_salary_prediction(df)
                results['salary'] = {
                    'model': salary_model,
                    'predictions': salary_preds,
                    'feature_pipeline': salary_pipeline
                }
            except Exception as e:
                print(f"❌ Error in salary prediction: {e}")

        # 3. Skill Extraction
        if 'skills' in components:
            try:
                clustered_df, cluster_model, tfidf_model = self.run_skill_extraction(df)
                results['skills'] = {
                    'clustered_data': clustered_df,
                    'cluster_model': cluster_model,
                    'tfidf_model': tfidf_model
                }
            except Exception as e:
                print(f"❌ Error in skill extraction: {e}")
        
        # 3. Recommendation System
        if 'recommendation' in components:
            try:
                rec_model, job_indexer, recommendations = self.run_recommendation_system(df)
                results['recommendation'] = {
                    'model': rec_model,
                    'job_indexer': job_indexer,
                    'recommendations': recommendations
                }
            except Exception as e:
                print(f"❌ Error in recommendation system: {e}")
        
        print("\n" + "="*70)
        print("✅ ML Pipeline Complete!")
        print("="*70)
        
        return results

    def run_streaming_inference(self, trained_results, input_dir="./streaming_input", output_dir="streaming-output"):
        """
        Run inference on a stream of data in streaming-dir using trained models.
        """
        print("\n" + "=" * 70)
        print("🌊 Starting Streaming Inference")
        print("=" * 70)

        # 1. Define Schema
        # Streaming requires a user-defined schema, it cannot infer from CSV automatically
        job_schema = StructType([
            StructField("job_id", StringType(), True),
            StructField("title", StringType(), True),
            StructField("company", StringType(), True),
            StructField("location", StringType(), True),
            StructField("salary", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("job_type", StringType(), True),
            StructField("experience_level", StringType(), True),
            StructField("posted_date", StringType(), True),
            StructField("url", StringType(), True)
        ])

        # 2. Read Stream
        print(f"👀 Monitoring directory: {input_dir}")
        stream_df = self.spark.readStream \
            .option("header", "true") \
            .option("maxFilesPerTrigger", 1) \
            .schema(job_schema) \
            .csv(input_dir)

        # 3. Apply Transformations
        # We process the stream DF. Note: We cannot call 'count()' or 'show()' here.
        processed_df = stream_df

        # --- A. Classification ---
        if 'classification' in trained_results:
            print("   • Attaching Classification Model...")
            class_model = trained_results['classification']['model']
            
            # Use the helper's prepare_features (safe for streaming as it uses UDFs)
            processed_df = self.job_classifier.prepare_features(processed_df)
            
            # Apply model
            predictions = class_model.transform(processed_df)
            
            # Keep relevant columns and rename prediction
            processed_df = predictions.withColumnRenamed("prediction", "category_index")
            
            # Note: We skip the helper's classify_jobs() because it calls .count() which breaks streaming

        # --- B. Skill Extraction ---
        print("   • Attaching Skill Extraction Logic...")
        # Use helper's prepare_text_features (safe for streaming)
        # Note: We check if columns exist to avoid duplication if Classification already ran prepare_features
        if "combined_text" not in processed_df.columns:
            processed_df = self.skill_extractor.prepare_text_features(processed_df)
        
        # --- C. Salary Prediction ---
        if 'salary' in trained_results:
            print("   • Attaching Salary Prediction Model...")
            salary_model = trained_results['salary']['model']
            salary_pipeline = trained_results['salary']['feature_pipeline']
            
            # CRITICAL: We cannot use SalaryPredictor.prepare_features() because it checks .count()
            # We must manually replicate the UDF logic here for the stream.
            
            # 1. Extract Numeric Salary
            extract_salary_udf = udf(SalaryPredictor.extract_salary_from_text, IntegerType())
            processed_df = processed_df.withColumn("salary_numeric", extract_salary_udf(col("salary")))
            
            # 2. Extract Experience Years
            extract_exp_udf = udf(SalaryPredictor.extract_experience_years, IntegerType())
            processed_df = processed_df.withColumn(
                "experience_years", 
                extract_exp_udf(col("experience_level"), col("description_text"))
            )
            
            # 3. Remote Check
            processed_df = processed_df.withColumn(
                "is_remote",
                when(
                    col("location").rlike("(?i)remote") | col("description_text").rlike("(?i)remote"), 
                    1.0
                ).otherwise(0.0)
            )
            
            # 4. High Value Skills Flags
            for skill in self.salary_predictor.high_value_skills:
                processed_df = processed_df.withColumn(
                    f"has_{skill.replace(' ', '_').replace('.', '_')}",
                    when(
                        lower(col("description_text")).rlike(f"(?i)\\b{skill}\\b") |
                        lower(col("title")).rlike(f"(?i)\\b{skill}\\b"),
                        1.0
                    ).otherwise(0.0)
                )

            # 5. Clean Description
            processed_df = processed_df.withColumn(
                "description_clean",
                regexp_replace(
                    regexp_replace(lower(coalesce(col("description_text"), lit(""))), "[^a-zA-Z0-9\\s]", " "),
                    "\\s+", " "
                )
            )

            # Apply Feature Pipeline (VectorAssembler, etc)
            # This is safe because PipelineModels are serializable
            if salary_pipeline:
                processed_df = salary_pipeline.transform(processed_df)
                
                # Apply Regression Model
                processed_df = salary_model.transform(processed_df)
                processed_df = processed_df.withColumnRenamed("prediction", "predicted_salary")

        # 4. Final Selection for Output
        # Select readable columns for output
        output_cols = [
            col("job_id"), col("title"), col("company"), 
            col("job_category"), # Added by classifier
            col("extracted_skills"), # Added by skill extractor
            col("predicted_salary") # Added by salary predictor
        ]
        
        # Filter only columns that actually exist in the dataframe
        final_select_cols = [c for c in output_cols if c._jc.toString() in processed_df.columns]
        
        # If we lost columns or have none, just dump everything except vectors
        if not final_select_cols:
             final_output = processed_df.drop("features", "text_features_vec", "raw_features", "bigram_features", "description_vec")
        else:
             final_output = processed_df.select(*output_cols)

        # 5. Write Stream
        # Ensure output directory exists
        chk_point_dir = os.path.join(output_dir, "_checkpoint")
        if os.path.exists(chk_point_dir):
            shutil.rmtree(chk_point_dir) # Clear checkpoint for fresh restart

        print(f"💾 Streaming output to: {output_dir}")
        
        query = final_output.writeStream \
            .outputMode("append") \
            .format("json") \
            .option("path", output_dir) \
            .option("checkpointLocation", chk_point_dir) \
            .trigger(processingTime="10 seconds") \
            .start()

        print("⏳ Stream is running... Press Ctrl+C to stop.")
        try:
            query.awaitTermination()
        except KeyboardInterrupt:
            print("\n🛑 Stopping stream...")
            query.stop()
    
    def save_results(self, results, output_dir="./ml_results"):
        """Save ML results to disk"""
        try:
            # Ensure results are saved inside spark-analytics/ml_results
            spark_dir = os.path.dirname(os.path.abspath(__file__))
            resolved_output_dir = os.path.join(spark_dir, "ml_results") if output_dir == "./ml_results" else output_dir
            os.makedirs(resolved_output_dir, exist_ok=True)
            print(f"\n💾 Saving results to {resolved_output_dir}...")
            
            # Save summary
            summary = {
                'timestamp': datetime.now().isoformat(),
                'components_run': list(results.keys()),
                'status': 'completed'
            }
            
            import json
            with open(os.path.join(resolved_output_dir, "ml_summary.json"), "w") as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Results saved to {resolved_output_dir}")

            # ---------------------------------------
            # Persist detailed DataFrame outputs for downstream analytics
            # ---------------------------------------
            analytics_out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics_output", "ml_outputs")
            os.makedirs(analytics_out_dir, exist_ok=True)

            # Helper to safely persist a Spark DataFrame
            import pandas as _pd

            def _persist_df(df, name: str, sample_rows: int = 5000):
                """Persist a DataFrame defensively without triggering large actions."""
                if df is None:
                    print(f"   ↳ Skipped {name} (None)")
                    return
                try:
                    # Fast emptiness check
                    if len(df.take(1)) == 0:
                        print(f"   ↳ Skipped {name} (empty)")
                        return
                    parquet_path = os.path.join(analytics_out_dir, name)
                    csv_path = os.path.join(analytics_out_dir, f"{name}.csv")
                    # Sample for CSV to prevent huge driver collection
                    sample_df = df.limit(sample_rows)
                    pdf = sample_df.toPandas()
                    pdf.to_csv(csv_path, index=False)
                    more_flag = " (truncated sample)" if df.rdd.getNumPartitions() > 1 and pdf.shape[0] == sample_rows else ""
                    print(f"   ↳ Saved {name} sampled CSV [{pdf.shape[0]} rows]{more_flag}")
                except Exception as e:
                    print(f"   ⚠️  Failed to persist {name}: {e}")

            # Classification predictions
            if "classification" in results:
                pred_df = results["classification"].get("predictions")
                if pred_df:
                    # Select safe columns to avoid Vector serialization issues
                    safe_cols = ["job_id", "title", "company", "location", "job_category", "prediction", "predicted_category_index"]
                    existing_cols = [c for c in safe_cols if c in pred_df.columns]
                    _persist_df(pred_df.select(*existing_cols), "classification_predictions")

            # Skill clustering results
            if "skills" in results:
                cluster_df = results["skills"].get("clustered_data")
                if cluster_df:
                    # Select safe columns
                    safe_cols = ["job_id", "title", "extracted_skills", "skill_count", "prediction"]
                    existing_cols = [c for c in safe_cols if c in cluster_df.columns]
                    # Rename prediction to cluster_id for clarity
                    to_save = cluster_df.select(*existing_cols).withColumnRenamed("prediction", "cluster_id")
                    # Convert array to string for CSV safety (Pandas handles lists, but string is safer for Spark->Pandas)
                    from pyspark.sql.functions import col, concat_ws
                    if "extracted_skills" in to_save.columns:
                        to_save = to_save.withColumn("extracted_skills", concat_ws(",", col("extracted_skills")))
                    _persist_df(to_save, "skill_clusters")

            # Recommendations
            if "recommendation" in results:
                recs_df = results["recommendation"].get("recommendations")
                if recs_df:
                    # Explode recommendations to make it flat and CSV friendly
                    # Schema: user_id, recommendations: Array[Struct(job_index, rating)]
                    from pyspark.sql.functions import explode, col
                    flat_recs = recs_df.select(
                        col("user_id"), 
                        explode(col("recommendations")).alias("rec")
                    ).select(
                        col("user_id"),
                        col("rec.job_index").alias("job_index"),
                        col("rec.rating").alias("score")
                    )
                    _persist_df(flat_recs, "job_recommendations")

            print(f"✅ Detailed ML outputs stored under: {analytics_out_dir}")
        
        except Exception as e:
            print(f"⚠️  Error saving results: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.data_loader.cleanup()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="ML Pipeline for YC Job Analytics")
    parser.add_argument("--date", type=str, help="Date to analyze (YYYY-MM-DD)")
    parser.add_argument("--days-back", type=int, default=7, help="Number of days to load for training")
    parser.add_argument("--components", type=str, nargs="+",
                       choices=['classification', 'skills', 'recommendation', 'salary'],
                       help="ML components to run (default: all)")
    parser.add_argument("--save", action="store_true", help="Save results to disk")
    parser.add_argument("--streaming", action="store_true", help="Run in streaming mode after training")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = MLPipeline()
    
    try:
        # Run pipeline (Training phase)
        results = pipeline.run_full_pipeline(
            date_str=args.date,
            days_back=args.days_back,
            components=args.components
        )
        
        # Save if requested
        if args.save and results:
            pipeline.save_results(results)

        # Run Streaming if requested
        if args.streaming and results:
             # Ensure the streaming directory exists
            stream_in = "streaming_input"
            stream_out = "streaming-output"
            os.makedirs(stream_in, exist_ok=True)
            
            pipeline.run_streaming_inference(
                results, 
                input_dir=stream_in,
                output_dir=stream_out
            )
    
    finally:
        pipeline.cleanup()


if __name__ == "__main__":
    main()