import requests
import json
import os
import argparse
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
from pyspark.sql import SparkSession
from dotenv import load_dotenv


class SimpleJobAnalytics:
    def __init__(self):
        self.worker_endpoint = os.getenv("WORKER_ENDPOINT", "https://job-scraper-worker.job-scraper-unhinged.workers.dev")
        self.output_dir = "analytics_output"
        self.reports_dir = "reports"
        
        # Create output directories
        #os.makedirs(self.output_dir, exist_ok=True)
        #os.makedirs(self.reports_dir, exist_ok=True)


def main():

    days_back = 7
    load_dotenv()
    """
    Main function to initialize Spark, connect to R2, and read data from a JSON file in the bucket.
    """
    # --- 1. Load Cloudflare R2 Credentials from Environment Variables ---
    try:
        account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
        access_key_id = os.environ["CLOUDFLARE_R2_ACCESS_KEY_ID"]
        secret_access_key = os.environ["CLOUDFLARE_R2_SECRET_ACCESS_KEY"]
    except KeyError as e:
        print(f"Error: Environment variable {e} not set.")
        print("Please set CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, and CLOUDFLARE_R2_SECRET_ACCESS_KEY.")
        return

    # Cloudflare R2 S3 endpoint
    r2_endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    bucket = "job-data-bucket"
    key = "exports/2025-10-03.json"
    s3a_path = f"s3a://{bucket}/{key}"

    spark = SparkSession.builder \
        .appName("R2DirectJsonRead") \
        .config("spark.hadoop.fs.s3a.access.key", access_key_id) \
        .config("spark.hadoop.fs.s3a.secret.key", secret_access_key) \
        .config("spark.hadoop.fs.s3a.endpoint", r2_endpoint) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.connection.request.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.socket.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.connection.maximum", "100") \
        .getOrCreate()

    # Print all S3A configs for debugging
    print("--- S3A Hadoop Configurations ---")
    hadoop_conf = spark._jsc.hadoopConfiguration()
    for k in hadoop_conf:
        if 's3a' in k:
            print(f'{k}: {hadoop_conf.get(k)}')
    print("-------------------------------")

    print("SparkSession created successfully.")
    print(f"Attempting to read JSON from: {s3a_path}")

    try:
        df = spark.read.json(s3a_path)
        print(f"Read {df.count()} records from {s3a_path}")
        df.show(5)
    except Exception as e:
        print(f"Failed to read JSON from R2: {e}")


if __name__ == "__main__":
    main()
