#!/usr/bin/env python3
"""
Recommendation System using Collaborative Filtering (ALS - Alternating Least Squares)
Recommends jobs to users/candidates based on implicit feedback and job similarity
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
import random


class JobRecommender:
    """Recommend jobs using Collaborative Filtering"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
    
    def create_user_job_interactions(self, df, num_users=100):
        """Create synthetic user-job interaction data for collaborative filtering"""
        print(f"\n👥 Creating user-job interactions for {num_users} users...")
        
        # Get all jobs with row numbers for indexing
        df_with_index = df.withColumn("row_id", monotonically_increasing_id())
        jobs_list = df_with_index.select("row_id", "title", "company", "location", "job_type", "experience_level").collect()
        num_jobs = len(jobs_list)
        
        if num_jobs == 0:
            print("❌ No jobs available for recommendations")
            return None, None
        
        print(f"📊 Working with {num_jobs} jobs")
        
        # Create job_id to row_id mapping
        job_id_map = {i: row['row_id'] for i, row in enumerate(jobs_list)}
        
        # Create synthetic interactions
        # Simulate user preferences based on job features
        interactions = []
        
        # Get distinct values for preferences
        locations = [row[0] for row in df.select("location").distinct().collect() if row[0] is not None][:10]
        job_types = [row[0] for row in df.select("job_type").distinct().collect() if row[0] is not None][:5]
        
        if not locations:
            locations = ["Remote", "San Francisco", "New York"]
        if not job_types:
            job_types = ["Full-time"]
        
        # Generate user profiles with preferences
        user_preferences = {}
        for user_id in range(num_users):
            # Random preferences for location, job type
            preferred_locations = random.sample(locations, min(3, len(locations)))
            preferred_job_types = random.sample(job_types, min(2, len(job_types)))
            
            user_preferences[user_id] = {
                'locations': preferred_locations,
                'job_types': preferred_job_types
            }
        
        # Generate interactions based on preferences
        for user_id in range(num_users):
            prefs = user_preferences[user_id]
            
            # Select jobs that match preferences
            matching_jobs_df = df_with_index.filter(
                col("location").isin(prefs['locations']) |
                col("job_type").isin(prefs['job_types'])
            )
            matching_jobs = matching_jobs_df.select("row_id").collect()
            
            # Each user interacts with 10-30% of matching jobs
            num_interactions = random.randint(
                max(1, len(matching_jobs) // 10),
                min(len(matching_jobs), max(5, len(matching_jobs) // 3)) if len(matching_jobs) > 0 else 1
            )
            
            selected_jobs = random.sample(matching_jobs, min(num_interactions, len(matching_jobs))) if matching_jobs else []
            
            for job_row in selected_jobs:
                # Find job index in jobs_list
                row_id = job_row['row_id']
                job_index = None
                for idx, job in enumerate(jobs_list):
                    if job['row_id'] == row_id:
                        job_index = idx
                        break
                
                if job_index is not None:
                    # Create rating (implicit feedback: view = 1, apply = 2-4, interview = 5)
                    rating = random.choices(
                        [1, 2, 3, 4, 5],
                        weights=[40, 25, 15, 10, 10]
                    )[0]
                    
                    interactions.append({
                        'user_id': user_id,
                        'job_index': job_index,
                        'rating': rating
                    })
            
            # Also add some random interactions (exploration)
            random_job_indices = random.sample(range(num_jobs), min(5, num_jobs))
            for job_index in random_job_indices:
                if random.random() < 0.3:  # 30% chance
                    rating = random.randint(1, 3)
                    interactions.append({
                        'user_id': user_id,
                        'job_index': job_index,
                        'rating': rating
                    })
        
        # Create DataFrame
        if interactions:
            interactions_df = self.spark.createDataFrame(interactions)
            print(f"✅ Created {interactions_df.count()} user-job interactions")
        else:
            print("⚠️  No interactions created")
            return None, None
        
        return interactions_df, jobs_list
    
    def prepare_recommendation_data(self, df, num_users=100):
        """Prepare data for collaborative filtering"""
        print("\n🎯 Preparing data for collaborative filtering...")
        
        # Create indices for jobs
        job_indexer = StringIndexer(
            inputCol="title",
            outputCol="job_index",
            handleInvalid="keep"
        )
        
        df_indexed = job_indexer.fit(df).transform(df)
        
        # Create user-job interactions
        interactions_df, job_list = self.create_user_job_interactions(df, num_users)
        
        if interactions_df is None:
            return None, None, None
        
        return df_indexed, interactions_df, job_indexer
    
    def train_recommender(self, df, num_users=100, implicit_prefs=True):
        """Train ALS recommendation model"""
        print("\n🎯 Training Job Recommender (Collaborative Filtering - ALS)...")
        
        # Prepare data
        df_indexed, interactions_df, job_indexer = self.prepare_recommendation_data(df, num_users)
        
        if interactions_df is None:
            print("❌ Failed to prepare recommendation data")
            return None, None, None
        
        # Split data
        train_df, test_df = interactions_df.randomSplit([0.8, 0.2], seed=42)
        
        print(f"📚 Training on {train_df.count()} interactions, testing on {test_df.count()} interactions")
        
        # Train ALS model
        als = ALS(
            maxIter=10,
            regParam=0.1,
            userCol="user_id",
            itemCol="job_index",
            ratingCol="rating",
            implicitPrefs=implicit_prefs,
            coldStartStrategy="drop",
            nonnegative=True
        )
        
        print("\n🔄 Training ALS model...")
        model = als.fit(train_df)
        
        # Evaluate model
        predictions = model.transform(test_df)
        
        # Filter out NaN predictions (cold start items)
        predictions_filtered = predictions.filter(col("prediction").isNotNull())
        
        if predictions_filtered.count() > 0:
            evaluator = RegressionEvaluator(
                metricName="rmse",
                labelCol="rating",
                predictionCol="prediction"
            )
            
            rmse = evaluator.evaluate(predictions_filtered)
            print(f"\n✅ Model RMSE: {rmse:.3f}")
            
            # Show sample predictions
            print(f"\n📊 Sample Recommendations:")
            sample_recs = predictions_filtered.select(
                "user_id", "job_index", "rating", "prediction"
            ).limit(10).collect()
            
            for row in sample_recs:
                print(f"   User {row['user_id']}, Job {row['job_index']}: "
                      f"Actual={row['rating']:.1f}, Predicted={row['prediction']:.2f}")
        
        return model, job_indexer, predictions
    
    def recommend_jobs_for_user(self, model, user_id, job_indexer, df, num_recommendations=10):
        """Get job recommendations for a specific user"""
        if model is None:
            print("❌ No trained model available")
            return None
        
        print(f"\n🔮 Getting recommendations for user {user_id}...")
        
        # Use ALS recommendForUserSubset method
        user_df = self.spark.createDataFrame([(user_id,)], ["user_id"])
        recommendations = model.recommendForUserSubset(user_df, num_recommendations)
        
        # Extract recommendations
        user_recs = recommendations.filter(col("user_id") == user_id).first()
        
        if user_recs and user_recs['recommendations']:
            print(f"\n📋 Top {num_recommendations} Job Recommendations for User {user_id}:")
            
            # Note: In production, you'd maintain a proper job_id to job details mapping
            for i, rec in enumerate(user_recs['recommendations'][:num_recommendations], 1):
                job_idx = rec['job_index']
                score = rec['rating']
                print(f"   {i}. Job Index {job_idx} (Score: {score:.3f})")
            
            return recommendations
        else:
            print(f"⚠️  No recommendations found for user {user_id}")
            return None
    
    def find_similar_jobs(self, model, job_index, df, num_similar=10):
        """Find similar jobs based on collaborative filtering"""
        if model is None:
            print("❌ No trained model available")
            return None
        
        print(f"\n🔍 Finding jobs similar to job {job_index}...")
        
        # Get item factors for the target job
        item_factors = model.itemFactors.filter(col("id") == job_index)
        
        if item_factors.count() == 0:
            print(f"❌ Job {job_index} not found in model")
            return None
        
        # Compute similarity with all other jobs
        # This would involve computing cosine similarity between item vectors
        # Simplified version: recommend jobs that users who liked this job also liked
        
        similar_jobs = model.recommendForItemSubset(
            self.spark.createDataFrame([(job_index,)], ["job_index"]),
            num_similar
        )
        
        return similar_jobs
    
    def recommend_top_jobs_for_all_users(self, model, num_users=100, num_recommendations=10):
        """Get top job recommendations for all users"""
        if model is None:
            print("❌ No trained model available")
            return None
        
        print(f"\n🔮 Generating recommendations for all {num_users} users...")
        
        # Create user list
        users_df = self.spark.range(num_users).select(col("id").alias("user_id"))
        
        # Get recommendations
        recommendations = model.recommendForUserSubset(users_df, num_recommendations)
        
        print(f"✅ Generated recommendations for {recommendations.count()} users")
        
        # Show sample for first user
        first_user_recs = recommendations.filter(col("user_id") == 0).first()
        if first_user_recs:
            print(f"\n📊 Sample Recommendations for User 0:")
            for i, rec in enumerate(first_user_recs['recommendations'][:5], 1):
                print(f"   {i}. Job {rec['job_index']}: Score {rec['rating']:.3f}")
        
        return recommendations


def main():
    """Standalone testing"""
    from data_loader import DataLoader
    
    loader = DataLoader()
    
    try:
        # Load data
        df = loader.load_postings()
        
        if df and df.count() > 0:
            recommender = JobRecommender(loader.spark)
            
            # Train model
            model, job_indexer, predictions = recommender.train_recommender(df, num_users=50)
            
            if model:
                # Get recommendations for a user
                recommendations = recommender.recommend_jobs_for_user(
                    model, user_id=0, job_indexer=job_indexer, df=df
                )
                
                print("\n✅ Job recommendation completed successfully!")
        else:
            print("📭 No data available for recommendations")
    
    finally:
        loader.cleanup()


if __name__ == "__main__":
    main()

