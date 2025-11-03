#!/usr/bin/env python3
"""
ML Pipeline Integration
Integrates all MLlib features: Job Classification, Salary Prediction, 
Skill Extraction, Recommendation System, and Trend Forecasting
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import argparse
import os
from datetime import datetime, timedelta

# Import ML modules
from ml_job_classifier import JobClassifier
from ml_salary_predictor import SalaryPredictor
from ml_skill_extractor import SkillExtractor
from ml_recommender import JobRecommender
from ml_trend_forecaster import TrendForecaster

# Import data loader
from data_loader import DataLoader


class MLPipeline:
    """Complete ML pipeline integrating all MLlib features"""
    
    def __init__(self):
        """Initialize ML pipeline with Spark session"""
        # Initialize data loader
        self.data_loader = DataLoader()
        self.spark = self.data_loader.spark
        
        # Initialize ML components
        self.job_classifier = JobClassifier(self.spark)
        self.salary_predictor = SalaryPredictor(self.spark)
        self.skill_extractor = SkillExtractor(self.spark)
        self.job_recommender = JobRecommender(self.spark)
        self.trend_forecaster = TrendForecaster(self.spark)
        
        print("✅ ML Pipeline initialized")
    
    def load_data(self, date_str=None, days_back=7):
        """Load job data from CSV files"""
        print("\n📥 Loading job data from CSV files...")
        
        # Load postings data
        df = self.data_loader.load_postings()
        
        if df and df.count() > 0:
            print(f"✅ Loaded {df.count()} job postings")
            return df
        
        print("⚠️  No data loaded")
        return None
    
    def run_job_classification(self, df):
        """Run job classification using Random Forest"""
        print("\n" + "="*60)
        print("🎯 Job Classification (Random Forest)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for classification")
            return None, None
        
        model, predictions = self.job_classifier.train_classifier(df)
        
        if model:
            # Classify all jobs
            classified_df = self.job_classifier.classify_jobs(model, df)
            return model, classified_df
        
        return None, None
    
    def run_salary_prediction(self, df):
        """Run salary prediction using Linear Regression"""
        print("\n" + "="*60)
        print("💰 Salary Prediction (Linear Regression)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for salary prediction")
            return None, None, None
        
        model, feature_pipeline, predictions = self.salary_predictor.train_predictor(df)
        
        if model:
            # Predict salaries for all jobs
            predicted_df = self.salary_predictor.predict_salaries(
                model, feature_pipeline, df
            )
            return model, feature_pipeline, predicted_df
        
        return None, None, None
    
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
    
    def run_trend_forecasting(self, df):
        """Run trend forecasting using Time-series Analysis"""
        print("\n" + "="*60)
        print("📈 Trend Forecasting (Time-series Analysis)")
        print("="*60)
        
        if df is None or df.count() == 0:
            print("❌ No data available for trend forecasting")
            return None, None, None
        
        model, assembler, historical_df = self.trend_forecaster.train_forecasting_model(
            df, forecast_days=7
        )
        
        if model:
            # Forecast future trends
            forecasts = self.trend_forecaster.forecast_future_trends(
                model, assembler, historical_df, forecast_days=7
            )
            
            # Analyze trends by category
            trends = self.trend_forecaster.analyze_trends_by_category(df)
            
            return model, assembler, forecasts
        
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
            components = ['classification', 'salary', 'skills', 'recommendation', 'forecasting']
        
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
                salary_model, feature_pipeline, predicted_df = self.run_salary_prediction(df)
                results['salary'] = {
                    'model': salary_model,
                    'feature_pipeline': feature_pipeline,
                    'predictions': predicted_df
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
        
        # 4. Recommendation System
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
        
        # 5. Trend Forecasting
        if 'forecasting' in components:
            try:
                forecast_model, assembler, forecasts = self.run_trend_forecasting(df)
                results['forecasting'] = {
                    'model': forecast_model,
                    'assembler': assembler,
                    'forecasts': forecasts
                }
            except Exception as e:
                print(f"❌ Error in trend forecasting: {e}")
        
        print("\n" + "="*70)
        print("✅ ML Pipeline Complete!")
        print("="*70)
        
        return results
    
    def save_results(self, results, output_dir="./ml_results"):
        """Save ML results to disk"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"\n💾 Saving results to {output_dir}...")
            
            # Save summary
            summary = {
                'timestamp': datetime.now().isoformat(),
                'components_run': list(results.keys()),
                'status': 'completed'
            }
            
            import json
            with open(f"{output_dir}/ml_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Results saved to {output_dir}")
        
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
                       choices=['classification', 'salary', 'skills', 'recommendation', 'forecasting'],
                       help="ML components to run (default: all)")
    parser.add_argument("--save", action="store_true", help="Save results to disk")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = MLPipeline()
    
    try:
        # Run pipeline
        results = pipeline.run_full_pipeline(
            date_str=args.date,
            days_back=args.days_back,
            components=args.components
        )
        
        # Save if requested
        if args.save and results:
            pipeline.save_results(results)
    
    finally:
        pipeline.cleanup()


if __name__ == "__main__":
    main()

