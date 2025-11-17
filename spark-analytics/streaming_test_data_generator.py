import pandas as pd
import os
import time
import random
from datetime import datetime

BATCH_SIZE = 100           # Number of records per batch
DELAY_SECONDS = 2         # Delay between batches (seconds)
TOTAL_BATCHES = 10        # Total number of batches to generate

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
    ingestion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "job_id": job_id,
        "company_id": company_id,
        "title": title,
        "description": description,
        "location": location,
        "company_name": company_name,
        "formatted_experience_level": experience_level,
        "ingestion_time": ingestion_time
    }


def simulate_test_streaming_data():
    print("="*60)
    print("STREAMING TEST DATA GENERATOR")
    print("="*60)
    streaming_dir = "streaming_input"
    os.makedirs(streaming_dir, exist_ok=True)
    print(f"✅ Streaming directory: {streaming_dir}")
    print(f"🚀 Generating {TOTAL_BATCHES} batches of {BATCH_SIZE} records each...")
    print("-"*60)
    record_idx = 0
    for batch_num in range(TOTAL_BATCHES):
        batch = [generate_job_posting(record_idx + i) for i in range(BATCH_SIZE)]
        record_idx += BATCH_SIZE
        df = pd.DataFrame(batch)
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
