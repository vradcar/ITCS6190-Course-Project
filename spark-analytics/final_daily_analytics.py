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
    Main function to initialize Spark, connect to R2, and read data.
    """
    # --- 1. Load Cloudflare R2 Credentials from Environment Variables ---
    # Best practice: Do NOT hardcode credentials in your script.
    # Load them from the environment for better security.
    try:
        account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
        access_key_id = os.environ["CLOUDFLARE_R2_ACCESS_KEY_ID"]
        secret_access_key = os.environ["CLOUDFLARE_R2_SECRET_ACCESS_KEY"]
    except KeyError as e:
        print(f"Error: Environment variable {e} not set.")
        print("Please set CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, and CLOUDFLARE_R2_SECRET_ACCESS_KEY.")
        return
    WAREHOUSE = "70ccae44f9c2610c4c703c97025a163c_job-data-bucket"
    TOKEN = "7vfZ8GAe1AHrWhkao58q0z1OMA1xk7hwWiVB-sTh"
    CATALOG_URI = "https://catalog.cloudflarestorage.com/70ccae44f9c2610c4c703c97025a163c/job-data-bucket"   

    spark = SparkSession.builder \
    .appName("R2DataCatalogExample") \
    .config('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.iceberg:iceberg-aws-bundle:1.6.1') \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.my_catalog.type", "rest") \
    .config("spark.sql.catalog.my_catalog.uri", CATALOG_URI) \
    .config("spark.sql.catalog.my_catalog.warehouse", WAREHOUSE) \
    .config("spark.sql.catalog.my_catalog.token", TOKEN) \
    .config("spark.sql.catalog.my_catalog.header.X-Iceberg-Access-Delegation", "vended-credentials") \
    .config("spark.sql.catalog.my_catalog.s3.remote-signing-enabled", "false") \
    .config("spark.sql.defaultCatalog", "my_catalog") \
    .getOrCreate()

    print("SparkSession created successfully.")

    table_name = "my_catalog.default.my_table"  # <-- IMPORTANT: CHANGE THIS

    print(f"Attempting to read data from Iceberg table: {table_name}")

    df = spark.table(table_name)


if __name__ == "__main__":
    main()
