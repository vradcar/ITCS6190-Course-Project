import pandas as pd
import os
import time
import random
from datetime import datetime
import csv

BATCH_SIZE = 100           # Number of records per batch
DELAY_SECONDS = 2          # Delay between batches (seconds)
TOTAL_BATCHES = 10         # Total number of batches to generate

# CSV template header (order enforced in output). If a postings template
# exists at ../data/postings_cleaned.csv, we'll read its header dynamically.
CSV_COLUMNS = None

def load_template_header():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, "data", "postings_cleaned.csv")
    if os.path.exists(template_path):
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                return header
        except Exception:
            pass
    # Fallback to previously used streaming schema if template not available
    return [
        "job_id",
        "company_id",
        "title",
        "description",
        "location",
        "company_name",
        "formatted_experience_level",
        "ingestion_time",
    ]

# Randomization ranges/settings
JOB_ID_START = 100000
COMPANY_ID_START = 5000
NUM_COMPANIES = 20
LOCATIONS = [
    "New York", "San Francisco", "Chicago", "Austin", "Seattle",
    "Boston", "Los Angeles", "Denver", "Atlanta", "Miami"
]
TITLES = [
    "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer",
    "Business Analyst", "QA Tester", "UX Designer", "Cloud Architect"
]
EXPERIENCE_LEVELS = [
    "Entry Level", "Mid Level", "Senior Level", "Director", "Internship"
]
COMPANY_NAMES = [
    f"Company_{i}" for i in range(1, NUM_COMPANIES+1)
]

# Additional template-driven fields
WORK_TYPES = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
APPLICATION_TYPES = ["Easy Apply", "External", "Referral"]
POSTING_DOMAINS = ["linkedin.com", "indeed.com", "company.careers"]

# DATA GENERATION
def generate_job_posting(idx):
    job_id = str(JOB_ID_START + idx)
    company_idx = random.randint(0, NUM_COMPANIES-1)
    company_id = str(COMPANY_ID_START + company_idx)
    title = random.choice(TITLES)
    description = f"{title} position at {COMPANY_NAMES[company_idx]}"
    location = random.choice(LOCATIONS)
    company_name = COMPANY_NAMES[company_idx]
    experience_level = random.choice(EXPERIENCE_LEVELS)
    # Enforce timestamp format per template
    ingestion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Additional generated fields (may be unused if template doesn't include them)
    views = random.randint(0, 5000)
    formatted_work_type = random.choice(WORK_TYPES)
    application_type = random.choice(APPLICATION_TYPES)
    posting_domain = random.choice(POSTING_DOMAINS)
    sponsored = random.choice([True, False])
    # Minimal zip code mapping by city, fallback to 00000
    city_zip_map = {
        "New York": "10001",
        "San Francisco": "94103",
        "Chicago": "60601",
        "Austin": "73301",
        "Seattle": "98101",
        "Boston": "02108",
        "Los Angeles": "90001",
        "Denver": "80202",
        "Atlanta": "30303",
        "Miami": "33101",
    }
    zip_code = city_zip_map.get(location, "00000")
    return {
        "job_id": job_id,
        "company_id": company_id,
        "title": title,
        "description": description,
        "location": location,
        "company_name": company_name,
        "formatted_experience_level": experience_level,
        "ingestion_time": ingestion_time,
        # Extra fields to align with postings_cleaned.csv when present
        "views": views,
        "formatted_work_type": formatted_work_type,
        "application_type": application_type,
        "posting_domain": posting_domain,
        "sponsored": sponsored,
        "zip_code": zip_code,
    }


def simulate_test_streaming_data():
    print("="*60)
    print("STREAMING TEST DATA GENERATOR")
    print("="*60)
    # Write streaming batches inside the spark-analytics folder
    spark_dir = os.path.dirname(os.path.abspath(__file__))
    streaming_dir = os.path.join(spark_dir, "streaming_input")
    os.makedirs(streaming_dir, exist_ok=True)
    print(f"✅ Streaming directory: {streaming_dir}")
    print(f"🚀 Generating {TOTAL_BATCHES} batches of {BATCH_SIZE} records each...")
    print("-"*60)
    # Resolve CSV column template once
    global CSV_COLUMNS
    if CSV_COLUMNS is None:
        CSV_COLUMNS = load_template_header()
        print(f"📄 Using template columns ({len(CSV_COLUMNS)}): {', '.join(CSV_COLUMNS)}")
    record_idx = 0
    for batch_num in range(TOTAL_BATCHES):
        batch = [generate_job_posting(record_idx + i) for i in range(BATCH_SIZE)]
        record_idx += BATCH_SIZE
        df = pd.DataFrame(batch)
        # Ensure column order and presence matches CSV template
        # Add any missing columns with empty string defaults
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        # Include only the template columns in the specified order
        df = df[[c for c in CSV_COLUMNS]]
        batch_filename = f"{streaming_dir}/test_batch_{batch_num:04d}.csv"
        df.to_csv(batch_filename, index=False)
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] Batch {batch_num+1}/{TOTAL_BATCHES} written → {batch_filename} ({len(df)} records)")
        if batch_num < TOTAL_BATCHES - 1:
            time.sleep(DELAY_SECONDS)
    print("-"*60)
    print(f"✅ Test data generation complete!")
    print(f"📊 Total records generated: {TOTAL_BATCHES * BATCH_SIZE}")
    print(f"📁 Files written to: {streaming_dir}/")
    print("="*60)

if __name__ == "__main__":
    simulate_test_streaming_data()
