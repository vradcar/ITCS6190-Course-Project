"""
Spark Structured Streaming Job
Processes job postings in real-time as they arrive in the streaming_input directory.
Demonstrates streaming analytics with windowed aggregations.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, window, desc, avg, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import os

def run_streaming_job():
    """
    Run Spark Structured Streaming job to process job postings in real-time.
    """
    print("="*60)
    print("SPARK STRUCTURED STREAMING JOB")
    print("="*60)
    
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("Job Postings Stream Analytics") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    print(f"\n✅ Spark Session Created")
    print(f"   Version: {spark.version}")
    
    # Define schema for incoming job postings
    # Adjust this schema based on your cleaned postings columns
    job_schema = StructType([
        StructField("job_id", StringType(), True),
        StructField("company_id", StringType(), True),
        StructField("title", StringType(), True),
        StructField("description", StringType(), True),
        StructField("location", StringType(), True),
        StructField("company_name", StringType(), True),
        StructField("formatted_experience_level", StringType(), True),
        StructField("ingestion_time", StringType(), True)
    ])
    
    streaming_dir = "streaming_input"
    
    print(f"\n📂 Reading from: {streaming_dir}/")
    print(f"📊 Schema defined with {len(job_schema.fields)} fields")
    
    # Read streaming data
    streaming_df = spark.readStream \
        .schema(job_schema) \
        .option("maxFilesPerTrigger", 1) \
        .option("header", True) \
        .csv(streaming_dir)
    
    print("\n🔥 Streaming DataFrame created")
    
    # Streaming Query 1: Job postings by location (real-time counts)
    print("\n" + "="*60)
    print("STREAMING QUERY 1: Job Postings by Location")
    print("="*60)
    
    location_trends = streaming_df \
        .groupBy("location") \
        .agg(count("job_id").alias("job_count")) \
        .orderBy(desc("job_count"))
    
    # Write to console
    query1 = location_trends.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", False) \
        .option("numRows", 20) \
        .queryName("location_trends") \
        .start()
    
    print("✅ Query 1 started: Tracking job counts by location")
    
    # Streaming Query 2: Job postings by experience level
    print("\n" + "="*60)
    print("STREAMING QUERY 2: Job Postings by Experience Level")
    print("="*60)
    
    experience_trends = streaming_df \
        .filter(col("formatted_experience_level").isNotNull()) \
        .groupBy("formatted_experience_level") \
        .agg(count("job_id").alias("job_count")) \
        .orderBy(desc("job_count"))
    
    query2 = experience_trends.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", False) \
        .option("numRows", 10) \
        .queryName("experience_trends") \
        .start()
    
    print("✅ Query 2 started: Tracking job counts by experience level")
    
    # Streaming Query 3: Top companies posting jobs
    print("\n" + "="*60)
    print("STREAMING QUERY 3: Top Companies Posting Jobs")
    print("="*60)
    
    company_trends = streaming_df \
        .filter(col("company_name").isNotNull()) \
        .groupBy("company_name") \
        .agg(count("job_id").alias("job_count")) \
        .orderBy(desc("job_count"))
    
    query3 = company_trends.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", False) \
        .option("numRows", 15) \
        .queryName("company_trends") \
        .start()
    
    print("✅ Query 3 started: Tracking top companies by job postings")
    
    print("\n" + "="*60)
    print("🎯 STREAMING JOBS RUNNING...")
    print("="*60)
    print("\n⚡ Processing incoming data in real-time...")
    print("💡 Start the streaming_data_simulator.py in another terminal")
    print("🛑 Press Ctrl+C to stop all queries")
    print("\n")
    
    # Wait for all queries
    try:
        query1.awaitTermination()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all streaming queries...")
        query1.stop()
        query2.stop()
        query3.stop()
        spark.stop()
        print("✅ All queries stopped successfully!")

if __name__ == "__main__":
    run_streaming_job()
