#!/usr/bin/env python3
"""
Trend Forecasting using Time-series Analysis
Forecasts job market trends over time using historical data
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from datetime import datetime, timedelta
import numpy as np


class TrendForecaster:
    """Forecast job market trends using time-series analysis"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
    
    def prepare_time_series_data(self, df):
        """Prepare time-series data from job postings"""
        print("\n📅 Preparing time-series data...")
        
        # Extract date from created_at
        df_with_date = df.withColumn(
            "date",
            to_date(
                col("created_at"),
                "yyyy-MM-dd"
            )
        )
        
        # Filter out null dates
        df_with_date = df_with_date.filter(col("date").isNotNull())
        
        if df_with_date.count() == 0:
            print("⚠️  No valid date information found")
            return None
        
        # Aggregate daily job counts
        daily_counts = df_with_date.groupBy("date").agg(
            count("*").alias("job_count"),
            countDistinct("company").alias("company_count"),
            countDistinct("location").alias("location_count")
        ).orderBy("date")
        
        print(f"📊 Prepared {daily_counts.count()} days of data")
        
        return daily_counts
    
    def create_temporal_features(self, df):
        """Create temporal features for time-series analysis"""
        print("\n🔧 Creating temporal features...")
        
        # Add time-based features
        df = df.withColumn("day_of_week", dayofweek(col("date")))
        df = df.withColumn("day_of_month", dayofmonth(col("date")))
        df = df.withColumn("month", month(col("date")))
        df = df.withColumn("year", year(col("date")))
        
        # Create a sequential day index
        window_spec = Window.orderBy("date")
        df = df.withColumn("day_index", row_number().over(window_spec) - 1)
        
        # Add lag features (previous day's job count)
        lag_window = Window.orderBy("date")
        df = df.withColumn("job_count_lag1", lag("job_count", 1).over(lag_window))
        df = df.withColumn("job_count_lag7", lag("job_count", 7).over(lag_window))  # Weekly lag
        
        # Add rolling averages
        rolling_window_7 = Window.orderBy("date").rowsBetween(-6, 0)
        rolling_window_30 = Window.orderBy("date").rowsBetween(-29, 0)
        
        df = df.withColumn("rolling_avg_7d", avg("job_count").over(rolling_window_7))
        df = df.withColumn("rolling_avg_30d", avg("job_count").over(rolling_window_30))
        
        # Remove rows with null lag features (first few days)
        df = df.filter(col("job_count_lag1").isNotNull())
        
        return df
    
    def train_forecasting_model(self, df, forecast_days=7):
        """Train model to forecast future job posting trends"""
        print(f"\n🎯 Training Trend Forecasting Model (Linear Regression)...")
        
        # Prepare time-series data
        time_series_df = self.prepare_time_series_data(df)
        
        if time_series_df is None:
            return None, None, None
        
        # Create temporal features
        df_with_features = self.create_temporal_features(time_series_df)
        
        if df_with_features.count() < 14:  # Need at least 2 weeks of data
            print("⚠️  Insufficient data for time-series forecasting (need at least 14 days)")
            return None, None, None
        
        print(f"📚 Training on {df_with_features.count()} days of historical data")
        
        # Show time-series statistics
        stats = df_with_features.agg(
            avg("job_count").alias("avg_daily_jobs"),
            min("job_count").alias("min_jobs"),
            max("job_count").alias("max_jobs"),
            stddev("job_count").alias("std_jobs")
        ).collect()[0]
        
        print(f"\n📊 Historical Statistics:")
        print(f"   • Average Daily Jobs: {stats['avg_daily_jobs']:.1f}")
        print(f"   • Range: {stats['min_jobs']:.0f} - {stats['max_jobs']:.0f}")
        print(f"   • Std Dev: {stats['std_jobs']:.1f}")
        
        # Prepare features for regression
        feature_cols = [
            "day_index", "day_of_week", "day_of_month", "month",
            "job_count_lag1", "job_count_lag7",
            "rolling_avg_7d", "rolling_avg_30d"
        ]
        
        # Fill nulls in rolling averages
        for col_name in ["rolling_avg_7d", "rolling_avg_30d"]:
            df_with_features = df_with_features.withColumn(
                col_name,
                coalesce(col(col_name), col("job_count"))
            )
        
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features"
        )
        
        df_features = assembler.transform(df_with_features)
        
        # Split into train/test (use last 20% for testing)
        total_days = df_features.count()
        test_size = max(7, total_days // 5)  # At least 1 week
        
        train_df = df_features.orderBy("date").limit(total_days - test_size)
        test_df = df_features.orderBy(desc("date")).limit(test_size)
        
        print(f"📚 Training on {train_df.count()} days, testing on {test_df.count()} days")
        
        # Train Linear Regression
        lr = LinearRegression(
            featuresCol="features",
            labelCol="job_count",
            maxIter=100,
            regParam=0.01,
            elasticNetParam=0.5
        )
        
        print("\n🔄 Training forecasting model...")
        model = lr.fit(train_df)
        
        # Evaluate on test set
        predictions = model.transform(test_df)
        
        evaluator = RegressionEvaluator(
            labelCol="job_count",
            predictionCol="prediction",
            metricName="rmse"
        )
        
        rmse = evaluator.evaluate(predictions)
        r2 = evaluator.setMetricName("r2").evaluate(predictions)
        
        print(f"\n✅ Model Performance:")
        print(f"   • RMSE: {rmse:.2f} jobs/day")
        print(f"   • R² Score: {r2:.2%}")
        
        # Show sample predictions
        print(f"\n📊 Sample Forecasts vs Actual:")
        sample_preds = predictions.select(
            "date", "job_count", "prediction"
        ).orderBy("date").collect()
        
        for row in sample_preds[:7]:
            actual = row['job_count']
            predicted = row['prediction']
            error = abs(actual - predicted)
            print(f"   {row['date']}: Actual={actual:.0f}, Forecast={predicted:.1f}, Error={error:.1f}")
        
        return model, assembler, df_features
    
    def forecast_future_trends(self, model, assembler, historical_df, forecast_days=7):
        """Forecast job posting trends for future days"""
        if model is None or assembler is None:
            print("❌ No trained model available")
            return None
        
        print(f"\n🔮 Forecasting trends for next {forecast_days} days...")
        
        # Get the last date in historical data
        last_date_row = historical_df.orderBy(desc("date")).first()
        if not last_date_row:
            print("❌ No historical data available")
            return None
        
        last_date = last_date_row['date']
        last_job_count = last_date_row['job_count']
        last_day_index = last_date_row['day_index']
        
        # Prepare forecast dates
        forecast_data = []
        for i in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=i)
            
            # Create features for this forecast day
            day_index = last_day_index + i
            day_of_week = forecast_date.weekday() + 1  # Monday = 1
            day_of_month = forecast_date.day
            month = forecast_date.month
            
            # Use last known values for lags (simplified approach)
            job_count_lag1 = last_job_count  # Previous day (predicted)
            job_count_lag7 = last_job_count  # Previous week (simplified)
            rolling_avg_7d = last_job_count
            rolling_avg_30d = last_job_count
            
            forecast_data.append({
                'date': forecast_date,
                'day_index': day_index,
                'day_of_week': day_of_week,
                'day_of_month': day_of_month,
                'month': month,
                'job_count_lag1': job_count_lag1,
                'job_count_lag7': job_count_lag7,
                'rolling_avg_7d': rolling_avg_7d,
                'rolling_avg_30d': rolling_avg_30d
            })
        
        # Create DataFrame
        forecast_df = self.spark.createDataFrame(forecast_data)
        
        # Prepare features
        feature_cols = [
            "day_index", "day_of_week", "day_of_month", "month",
            "job_count_lag1", "job_count_lag7",
            "rolling_avg_7d", "rolling_avg_30d"
        ]
        
        forecast_features = assembler.transform(forecast_df)
        
        # Make predictions
        forecasts = model.transform(forecast_features)
        
        # Show forecasts
        print(f"\n📅 Forecasted Job Postings:")
        forecast_results = forecasts.select(
            "date", "prediction"
        ).orderBy("date").collect()
        
        total_forecast = 0
        for row in forecast_results:
            date_str = row['date'].strftime("%Y-%m-%d")
            predicted = max(0, row['prediction'])  # Ensure non-negative
            total_forecast += predicted
            print(f"   • {date_str}: {predicted:.1f} jobs")
        
        print(f"\n📊 Total Forecast: {total_forecast:.1f} jobs over {forecast_days} days")
        print(f"   Average: {total_forecast/forecast_days:.1f} jobs/day")
        
        return forecasts
    
    def analyze_trends_by_category(self, df):
        """Analyze trends by job category, location, etc."""
        print("\n📈 Analyzing trends by category...")
        
        # Prepare time-series data with categories
        df_with_date = df.withColumn(
            "date",
            to_date(col("created_at"), "yyyy-MM-dd")
        ).filter(col("date").isNotNull())
        
        # Trends by location
        print("\n🌍 Location Trends:")
        location_trends = df_with_date.groupBy("location", "date").count().groupBy("location").agg(
            avg("count").alias("avg_daily"),
            sum("count").alias("total")
        ).orderBy(desc("total")).limit(10)
        
        for row in location_trends.collect():
            print(f"   • {row['location']}: {row['avg_daily']:.1f} jobs/day, {row['total']:.0f} total")
        
        # Trends by job type
        if "job_type" in df.columns:
            print("\n⚡ Job Type Trends:")
            type_trends = df_with_date.groupBy("job_type", "date").count().groupBy("job_type").agg(
                avg("count").alias("avg_daily"),
                sum("count").alias("total")
            ).orderBy(desc("total"))
            
            for row in type_trends.collect():
                print(f"   • {row['job_type']}: {row['avg_daily']:.1f} jobs/day, {row['total']:.0f} total")
        
        return location_trends


def main():
    """Standalone testing"""
    from daily_analytics import YCJobAnalytics
    
    analytics = YCJobAnalytics()
    
    try:
        # Load data for multiple days
        from datetime import datetime, timedelta
        
        all_data = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            df = analytics.load_data_from_worker(date)
            if df and df.count() > 0:
                all_data.append(df)
        
        if all_data:
            combined_df = all_data[0]
            for df in all_data[1:]:
                combined_df = combined_df.union(df)
            
            forecaster = TrendForecaster(analytics.spark)
            
            # Train model
            model, assembler, historical_df = forecaster.train_forecasting_model(combined_df)
            
            if model:
                # Forecast future
                forecasts = forecaster.forecast_future_trends(
                    model, assembler, historical_df, forecast_days=7
                )
                
                # Analyze trends
                trends = forecaster.analyze_trends_by_category(combined_df)
                
                print("\n✅ Trend forecasting completed successfully!")
        else:
            print("📭 No data available for trend forecasting")
    
    finally:
        analytics.cleanup()


if __name__ == "__main__":
    main()

