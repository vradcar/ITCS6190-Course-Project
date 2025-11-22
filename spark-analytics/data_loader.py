#!/usr/bin/env python3
"""
Data Loader for LinkedIn Job Postings
Loads data from CSV files in the data folder for training and analysis
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, regexp_replace, lower, coalesce, lit
from pyspark.sql.types import StringType
import os


class DataLoader:
    """Load and prepare job posting data from CSV files"""
    
    def __init__(self, spark_session=None):
        """Initialize data loader with Spark session"""
        if spark_session is None:
            self.spark = SparkSession.builder \
                .appName("Job Postings Data Loader") \
                .config("spark.driver.memory", "4g") \
                .config("spark.sql.shuffle.partitions", "4") \
                .getOrCreate()
            self.spark.sparkContext.setLogLevel("WARN")
            self._created_spark = True
        else:
            self.spark = spark_session
            self._created_spark = False
        
        # Get base directory (parent of spark-analytics)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(current_dir)
        self.data_dir = os.path.join(self.base_dir, "data")
        
        print(f"📂 Data directory: {self.data_dir}")
    
    def load_postings(self):
        """Load postings_cleaned.csv file"""
        postings_path = os.path.join(self.data_dir, "postings_cleaned.csv")
        
        if not os.path.exists(postings_path):
            raise FileNotFoundError(f"Postings file not found: {postings_path}")
        
        print(f"📥 Loading postings from: {postings_path}")
        
        df = self.spark.read.csv(
            postings_path,
            header=True,
            inferSchema=True,
            multiLine=True,
            escape='"'
        )
        
        # Clean and standardize column names
        df = self._standardize_columns(df)
        
        print(f"✅ Loaded {df.count()} job postings")
        return df
    
    def load_companies(self):
        """Load company data"""
        companies_path = os.path.join(self.data_dir, "companies", "companies.csv")
        
        if not os.path.exists(companies_path):
            print(f"⚠️  Companies file not found: {companies_path}")
            return None
        
        df = self.spark.read.csv(companies_path, header=True, inferSchema=True)
        print(f"✅ Loaded {df.count()} companies")
        return df
    
    def load_job_skills(self):
        """Load job skills mapping"""
        skills_path = os.path.join(self.data_dir, "jobs", "job_skills.csv")
        
        if not os.path.exists(skills_path):
            print(f"⚠️  Job skills file not found: {skills_path}")
            return None
        
        df = self.spark.read.csv(skills_path, header=True, inferSchema=True)
        print(f"✅ Loaded {df.count()} job-skill mappings")
        return df
    
    def load_job_industries(self):
        """Load job industries mapping"""
        industries_path = os.path.join(self.data_dir, "jobs", "job_industries.csv")
        
        if not os.path.exists(industries_path):
            print(f"⚠️  Job industries file not found: {industries_path}")
            return None
        
        df = self.spark.read.csv(industries_path, header=True, inferSchema=True)
        print(f"✅ Loaded {df.count()} job-industry mappings")
        return df
    
    def load_salaries(self):
        """Load salary data"""
        salaries_path = os.path.join(self.data_dir, "jobs", "salaries.csv")
        
        if not os.path.exists(salaries_path):
            print(f"⚠️  Salaries file not found: {salaries_path}")
            return None
        
        df = self.spark.read.csv(salaries_path, header=True, inferSchema=True)
        print(f"✅ Loaded {df.count()} salary records")
        return df
    
    def load_all_data(self):
        """Load all available data"""
        print("\n" + "="*60)
        print("📥 Loading All Data")
        print("="*60)
        
        postings = self.load_postings()
        companies = self.load_companies()
        job_skills = self.load_job_skills()
        job_industries = self.load_job_industries()
        salaries = self.load_salaries()
        
        return {
            'postings': postings,
            'companies': companies,
            'job_skills': job_skills,
            'job_industries': job_industries,
            'salaries': salaries
        }
    
    def _standardize_columns(self, df):
        """Standardize column names and add common aliases"""
        # Map common column name variations
        column_mapping = {
            'formatted_experience_level': 'experience_level',
            'formatted_work_type': 'job_type',
            'description': 'description_text'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df = df.withColumnRenamed(old_name, new_name)
        
        # Ensure common columns exist with defaults
        if 'description_text' not in df.columns:
            df = df.withColumn('description_text', coalesce(col('description'), lit('')))
        
        if 'experience_level' not in df.columns:
            df = df.withColumn('experience_level', lit('Not Specified'))
        
        if 'job_type' not in df.columns:
            df = df.withColumn('job_type', lit('Full-time'))
        
        if 'location' not in df.columns:
            df = df.withColumn('location', lit('Not Specified'))
        
        if 'company' not in df.columns and 'company_name' in df.columns:
            df = df.withColumnRenamed('company_name', 'company')
        
        if 'created_at' not in df.columns:
            # Try to infer from other date columns or use current timestamp
            df = df.withColumn('created_at', lit('2024-01-01'))
        
        if 'salary' not in df.columns:
            df = df.withColumn('salary', lit(None).cast(StringType()))
        
        return df
    
    def get_enriched_postings(self):
        """Get postings data enriched with related data"""
        data = self.load_all_data()
        postings = data['postings']
        
        # Join with companies if available
        if data['companies'] is not None:
            postings = postings.join(
                data['companies'].select('company_id', 'company_name'),
                on='company_id',
                how='left'
            )
        
        # Join with job skills if available
        if data['job_skills'] is not None:
            postings = postings.join(
                data['job_skills'],
                on='job_id',
                how='left'
            )
        
        # Join with salaries if available
        if data['salaries'] is not None:
            postings = postings.join(
                data['salaries'],
                on='job_id',
                how='left'
            )
        
        return postings
    
    def cleanup(self):
        """Clean up Spark session if we created it"""
        if self._created_spark:
            self.spark.stop()
            print("✅ Spark session stopped")


def main():
    """Test data loader"""
    loader = DataLoader()
    
    try:
        # Load postings
        postings = loader.load_postings()
        postings.printSchema()
        postings.show(5, truncate=False)
        
        # Load all data
        all_data = loader.load_all_data()
        print(f"\n✅ Loaded {len(all_data)} data sources")
        
    finally:
        loader.cleanup()


if __name__ == "__main__":
    main()

