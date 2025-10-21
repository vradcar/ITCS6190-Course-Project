"""
Streaming Data Simulator
Simulates real-time job posting data by reading from the cleaned dataset
and writing small batches to a streaming input directory.
"""

import pandas as pd
import time
import os
from datetime import datetime
import random

def simulate_streaming_data(batch_size=50, delay_seconds=5, total_batches=10):
    """
    Simulate streaming job postings data.
    
    Args:
        batch_size: Number of records per batch
        delay_seconds: Delay between batches (simulates real-time arrival)
        total_batches: Total number of batches to generate
    """
    print("="*60)
    print("STREAMING DATA SIMULATOR")
    print("="*60)
    
    # Load cleaned postings
    data_path = r"../data/postings_cleaned.csv"
    print(f"\n📂 Loading data from: {data_path}")
    
    try:
        postings = pd.read_csv(data_path)
        print(f"✅ Loaded {len(postings)} job postings")
    except FileNotFoundError:
        print(f"❌ Error: Could not find {data_path}")
        print("Please run the data cleaning notebook first!")
        return
    
    # Create streaming input directory
    streaming_dir = "streaming_input"
    os.makedirs(streaming_dir, exist_ok=True)
    print(f"✅ Created streaming directory: {streaming_dir}")
    
    # Shuffle data to simulate randomness
    postings = postings.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\n🚀 Starting simulation...")
    print(f"   Batch size: {batch_size} records")
    print(f"   Delay: {delay_seconds} seconds")
    print(f"   Total batches: {total_batches}")
    print("\n" + "-"*60)
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = start_idx + batch_size
        
        # Check if we have enough data
        if start_idx >= len(postings):
            print("\n⚠️  Reached end of dataset")
            break
        
        # Get batch
        batch = postings.iloc[start_idx:end_idx].copy()
        
        # Add timestamp to simulate real-time data
        batch['ingestion_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Write batch to CSV
        batch_filename = f"{streaming_dir}/batch_{batch_num:04d}.csv"
        batch.to_csv(batch_filename, index=False)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] Batch {batch_num + 1}/{total_batches} written → {batch_filename} ({len(batch)} records)")
        
        # Wait before next batch (except for last batch)
        if batch_num < total_batches - 1:
            time.sleep(delay_seconds)
    
    print("-"*60)
    print(f"\n✅ Simulation complete!")
    print(f"📊 Total records generated: {min(total_batches * batch_size, len(postings))}")
    print(f"📁 Files written to: {streaming_dir}/")
    print("="*60)

if __name__ == "__main__":
    # Run simulation with default parameters
    # Adjust these values as needed for your demo
    simulate_streaming_data(
        batch_size=50,        # 50 records per batch
        delay_seconds=5,      # 5 seconds between batches
        total_batches=10      # 10 batches total
    )
