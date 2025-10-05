#!/usr/bin/env python3
"""
Enhanced Y Combinator Job Market Analytics Pipeline
Processes job data using Apache Spark for insights and reporting
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import requests
import os
import json
from datetime import datetime, timedelta
import argparse
import re

class YCJobAnalytics:
    def __init__(self):
        """Initialize Spark session and configuration"""
        self.spark = SparkSession.builder \
            .appName("YCJobMarketAnalytics") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        # Configure R2 access if available
        r2_endpoint = os.getenv("R2_ENDPOINT")
        if r2_endpoint:
            self.spark.sparkContext._jsc.hadoopConfiguration().set(
                "fs.s3a.endpoint", r2_endpoint
            )
            self.spark.sparkContext._jsc.hadoopConfiguration().set(
                "fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID")
            )
            self.spark.sparkContext._jsc.hadoopConfiguration().set(
                "fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            self.spark.sparkContext._jsc.hadoopConfiguration().set(
                "fs.s3a.path.style.access", "true"
            )
        
        self.bucket = os.getenv("R2_BUCKET", "job-data-bucket")
        self.worker_endpoint = os.getenv("WORKER_ENDPOINT", "https://job-scraper-worker.job-scraper-unhinged.workers.dev")
    
    def load_data_from_worker(self, date_str=None):
        """Load job data from Cloudflare Worker API"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Get data from Worker API
            url = f"{self.worker_endpoint}/api/export/{date_str}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert to Spark DataFrame
                if 'jobs' in data and data['jobs']:
                    jobs_data = data['jobs']
                    df = self.spark.createDataFrame(jobs_data)
                    print(f"✅ Loaded {df.count()} jobs from Worker API for {date_str}")
                    return df
                else:
                    print(f"📭 No jobs found for {date_str}")
                    return None
            else:
                print(f"❌ Failed to fetch data: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error loading data from Worker: {e}")
            return None
    
    def load_data_from_r2(self, date_str):
        """Load job data from R2 storage (alternative method)"""
        path = f"s3a://{self.bucket}/exports/{date_str}.json"
        
        try:
            df = self.spark.read.option("multiline", "true").json(path)
            
            # If data is wrapped in jobs array, unwrap it
            if "jobs" in df.columns:
                df = df.select(explode(col("jobs")).alias("job")).select("job.*")
            
            print(f"✅ Loaded {df.count()} jobs from R2 for {date_str}")
            return df
            
        except Exception as e:
            print(f"❌ Failed to load data from R2 for {date_str}: {e}")
            return None
    
    def analyze_daily_jobs(self, df, date_str):
        """Generate comprehensive daily job analysis"""
        if df is None or df.count() == 0:
            print(f"📭 No data to analyze for {date_str}")
            return
        
        print(f"\n📊 Y Combinator Job Analysis for {date_str}")
        print("=" * 60)
        
        # Basic metrics
        total_jobs = df.count()
        unique_companies = df.filter(col("company").isNotNull()).select("company").distinct().count()
        
        print(f"📈 Total Jobs: {total_jobs}")
        print(f"🏢 Unique Companies: {unique_companies}")
        
        # Company analysis
        print(f"\n🏆 Top 10 Companies by Job Count:")
        top_companies = df.filter(col("company").isNotNull()) \
            .groupBy("company") \
            .count() \
            .orderBy(desc("count")) \
            .limit(10)
        
        for row in top_companies.collect():
            print(f"   • {row['company']}: {row['count']} jobs")
        
        # Location analysis
        print(f"\n🌍 Top 10 Locations:")
        top_locations = df.filter(col("location").isNotNull()) \
            .groupBy("location") \
            .count() \
            .orderBy(desc("count")) \
            .limit(10)
        
        for row in top_locations.collect():
            print(f"   • {row['location']}: {row['count']} jobs")
        
        # Salary analysis (if available)
        salary_jobs = df.filter(col("salary").isNotNull() & (col("salary") != ""))
        if salary_jobs.count() > 0:
            print(f"\n💰 Salary Information Available: {salary_jobs.count()} jobs")
            self.analyze_salaries(salary_jobs)
        
        # Job type analysis
        job_type_jobs = df.filter(col("job_type").isNotNull() & (col("job_type") != ""))
        if job_type_jobs.count() > 0:
            print(f"\n⚡ Job Types:")
            job_types = job_type_jobs.groupBy("job_type").count().orderBy(desc("count"))
            for row in job_types.collect():
                print(f"   • {row['job_type']}: {row['count']} jobs")
        
        # Experience level analysis
        exp_level_jobs = df.filter(col("experience_level").isNotNull() & (col("experience_level") != ""))
        if exp_level_jobs.count() > 0:
            print(f"\n🎯 Experience Levels:")
            exp_levels = exp_level_jobs.groupBy("experience_level").count().orderBy(desc("count"))
            for row in exp_levels.collect():
                print(f"   • {row['experience_level']}: {row['count']} jobs")
        
        # Skill analysis
        self.analyze_skills(df)
        
        # Remote work analysis
        self.analyze_remote_work(df)
    
    def analyze_salaries(self, df):
        """Analyze salary information from job postings"""
        print(f"\n💰 Salary Analysis:")
        
        # Extract salary ranges from salary field (JSON or text)
        salary_df = df.withColumn("salary_text", 
            when(col("salary").startswith("{"), 
                 regexp_extract(col("salary"), r'"minValue":\s*(\d+)', 1).cast("int"))
            .otherwise(regexp_extract(col("salary"), r'\$(\d{1,3}(?:,?\d{3})*)', 1))
        ).filter(col("salary_text").isNotNull() & (col("salary_text") > 0))
        
        if salary_df.count() > 0:
            stats = salary_df.agg(
                avg("salary_text").alias("avg_salary"),
                min("salary_text").alias("min_salary"),
                max("salary_text").alias("max_salary")
            ).collect()[0]
            
            print(f"   • Average Salary: ${stats['avg_salary']:,.0f}")
            print(f"   • Salary Range: ${stats['min_salary']:,.0f} - ${stats['max_salary']:,.0f}")
    
    def analyze_skills(self, df):
        """Analyze in-demand skills from job descriptions"""
        print(f"\n🛠️ Top Skills Mentioned:")
        
        # Common tech skills to look for
        skills = [
            "Python", "JavaScript", "React", "Node.js", "TypeScript", "Java", "Go",
            "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis",
            "Machine Learning", "AI", "Data Science", "API", "REST", "GraphQL",
            "Full Stack", "Frontend", "Backend", "DevOps", "Microservices"
        ]
        
        skill_counts = []
        for skill in skills:
            count = df.filter(
                col("description_text").rlike(f"(?i)\\b{skill}\\b") |
                col("title").rlike(f"(?i)\\b{skill}\\b")
            ).count()
            if count > 0:
                skill_counts.append((skill, count))
        
        # Sort by count and show top 10
        skill_counts.sort(key=lambda x: x[1], reverse=True)
        for skill, count in skill_counts[:10]:
            print(f"   • {skill}: {count} jobs")
    
    def analyze_remote_work(self, df):
        """Analyze remote work opportunities"""
        print(f"\n🏠 Remote Work Analysis:")
        
        remote_jobs = df.filter(
            col("location").rlike("(?i)remote") |
            col("description_text").rlike("(?i)remote") |
            col("title").rlike("(?i)remote")
        ).count()
        
        total_jobs = df.count()
        remote_percentage = (remote_jobs / total_jobs) * 100 if total_jobs > 0 else 0
        
        print(f"   • Remote Jobs: {remote_jobs} ({remote_percentage:.1f}%)")
        print(f"   • On-site Jobs: {total_jobs - remote_jobs} ({100 - remote_percentage:.1f}%)")
    
    def generate_weekly_report(self, start_date, end_date):
        """Generate a comprehensive weekly report"""
        print(f"\n📅 Weekly Report: {start_date} to {end_date}")
        print("=" * 60)
        
        # Load data for each day in the range
        all_data = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date <= end_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            df = self.load_data_from_worker(date_str)
            if df and df.count() > 0:
                all_data.append(df)
            current_date += timedelta(days=1)
        
        if not all_data:
            print("📭 No data found for the specified date range")
            return
        
        # Combine all data
        combined_df = all_data[0]
        for df in all_data[1:]:
            combined_df = combined_df.union(df)
        
        print(f"📊 Total jobs analyzed: {combined_df.count()}")
        
        # Run analysis on combined data
        self.analyze_daily_jobs(combined_df, f"{start_date} to {end_date}")
        
        # Daily trends
        print(f"\n📈 Daily Job Posting Trends:")
        daily_counts = combined_df.groupBy(
            date_format(col("created_at"), "yyyy-MM-dd").alias("date")
        ).count().orderBy("date")
        
        for row in daily_counts.collect():
            print(f"   • {row['date']}: {row['count']} jobs")
    
    def save_analysis_results(self, df, date_str, output_path="./analytics_output"):
        """Save analysis results to files"""
        try:
            os.makedirs(output_path, exist_ok=True)
            
            # Save summary statistics
            summary = {
                "date": date_str,
                "total_jobs": df.count(),
                "unique_companies": df.filter(col("company").isNotNull()).select("company").distinct().count(),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            with open(f"{output_path}/summary_{date_str}.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            # Save detailed data as Parquet for efficient storage
            df.write.mode("overwrite").parquet(f"{output_path}/jobs_{date_str}.parquet")
            
            print(f"✅ Analysis results saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def cleanup(self):
        """Clean up Spark session"""
        self.spark.stop()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Y Combinator Job Market Analytics")
    parser.add_argument("--date", type=str, help="Date to analyze (YYYY-MM-DD)", 
                       default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--start-date", type=str, help="Start date for weekly report")
    parser.add_argument("--end-date", type=str, help="End date for weekly report")
    parser.add_argument("--save", action="store_true", help="Save analysis results")
    
    args = parser.parse_args()
    
    # Initialize analytics
    analytics = YCJobAnalytics()
    
    try:
        if args.weekly:
            if not args.start_date or not args.end_date:
                print("❌ Weekly report requires --start-date and --end-date")
                return
            analytics.generate_weekly_report(args.start_date, args.end_date)
        else:
            # Load and analyze daily data
            df = analytics.load_data_from_worker(args.date)
            if df:
                analytics.analyze_daily_jobs(df, args.date)
                
                if args.save:
                    analytics.save_analysis_results(df, args.date)
            else:
                print(f"📭 No data available for {args.date}")
    
    finally:
        analytics.cleanup()

if __name__ == "__main__":
    main()