from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, rank, hour, sum, round, when, desc, percentile_approx
from pyspark.sql.window import Window
import os

# Get base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")

spark = SparkSession.builder.appName("LinkedInJobAnalysis").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Load datasets
def load_comp_data():
    try:    
        comp = spark.read.csv(os.path.join(data_dir, "companies", "companies.csv"), header=True, inferSchema=True)
        comp_ind = spark.read.csv(os.path.join(data_dir, "companies", "company_industries.csv"), header=True, inferSchema=True)
        comp_spel = spark.read.csv(os.path.join(data_dir, "companies", "company_specialities.csv"), header=True, inferSchema=True)
        employee_counts = spark.read.csv(os.path.join(data_dir, "companies", "employee_counts.csv"), header=True, inferSchema=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Please ensure csv files are present in the data directory.")
        exit()
    # Join the company-related dataframes to create a single, enriched view (left joins to keep all companies).
    comp_df = comp.join(comp_ind, "company_id", "left") \
              .join(comp_spel, "company_id", "left") \
              .join(employee_counts, "company_id", "left")
    print("--- DataFrames Loaded and Enriched Successfully ---")
    comp_df.printSchema()
    
    return comp_df

def load_job_data():
    try:
        job_ind = spark.read.csv(os.path.join(data_dir, "jobs", "job_industries.csv"), header=True, inferSchema=True)
        job_skill = spark.read.csv(os.path.join(data_dir, "jobs", "job_skills.csv"), header=True, inferSchema=True)
        job_sal = spark.read.csv(os.path.join(data_dir, "jobs", "salaries.csv"), header=True, inferSchema=True)
    except Exception as e:
        print(f"Error loading job data: {e}")
        print("Please ensure job csv files are present in the data directory.")
        exit()
    job_df = job_ind.join(job_skill, "job_id", "left") \
                    .join(job_sal, "job_id", "left")
    print("--- Job DataFrames Loaded and Enriched Successfully ---")
    job_df.printSchema()
    # Return both the enriched job_df and the raw components for analysis functions
    return job_df, job_skill, job_sal

def company_with_most_postings(postings_df, comp_df=None, top_n=10):
    """Return the top companies by number of postings.

    If comp_df is provided, attempt to map company_id to official company name.
    """
    keyed = postings_df.filter(col('company_id').isNotNull())
    counts = keyed.groupBy('company_id').agg(count('*').alias('postings')).orderBy(desc('postings'))
    counts.printSchema()
    counts.show(5, truncate=False)
    if comp_df is not None:
        # Try to join counts with comp_df to get a nicer company name when comp_key is a company_id
        print("we found the companies")
        comp_names = comp_df.select('company_id', 'company_name')
        joined = counts.join(comp_names, counts.company_id == comp_names.company_id, 'left') 
        print(f"Top {top_n} companies by number of postings:")
        joined.select('company_name', 'postings').show(top_n, truncate=False)
        return joined
    else:
        print(f"Top {top_n} companies by number of postings (by comp_key):")
        counts.show(top_n, truncate=False)
        return counts

def most_desirable_skills(job_skill_df, top_n=20):
    """Return skills ranked by how often they appear on job postings/jobs."""
    skill_counts = job_skill_df.groupBy('skill_abr').agg(count('*').alias('count')).orderBy(desc('count'))
    print(f"Top {top_n} most desirable skills:")
    skill_counts.show(top_n, truncate=False)
    return skill_counts

def top_locations(postings_df, top_n=10):
    """Return the top N locations with the most postings."""
    loc_counts = postings_df.groupBy('location').agg(count('*').alias('postings')).orderBy(desc('postings'))
    print(f"Top {top_n} locations by postings:")
    loc_counts.show(top_n, truncate=False)
    return loc_counts

def median_salary_by_skill(job_skill_df, salaries_df, top_n=20):
    """Compute median (50th percentile) yearly salary per skill.

    This function filters salaries to YEARLY pay_period and USD currency to keep units comparable.
    """
    sal_filtered = salaries_df.filter((col('pay_period') == 'YEARLY') & (col('currency') == 'USD') & (col('med_salary').isNotNull())) \
                              .select(col('job_id'), col('med_salary').cast('double').alias('med_salary'))
    # join skills to salaries
    skill_sal = job_skill_df.join(sal_filtered, 'job_id', 'inner')
    # compute median per skill
    median_by_skill = skill_sal.groupBy('skill_abr') \
                        .agg(percentile_approx(col('med_salary'), 0.5).alias('median_salary'), count('*').alias('num_jobs')) \
                        .orderBy(desc('median_salary'))
    print(f"Top {top_n} skills by median yearly salary (YEARLY, USD):")
    median_by_skill.show(top_n, truncate=False)
    return median_by_skill

def load_posting_data():
    try:
        postings = spark.read.csv(os.path.join(data_dir, "postings_cleaned.csv"), header=True, inferSchema=True, multiLine=True, escape='"')
    except Exception as e:
        print(f"Error loading posting data: {e}")
        print("Please ensure postings csv file is present in the data directory.")
        exit()
    print("--- Posting DataFrame Loaded Successfully ---")
    postings.printSchema()
    return postings

def main():
    comp_df = load_comp_data()
    job_df, job_skill_df, salaries_df = load_job_data()
    postings = load_posting_data()

    # Example action: Show counts of each DataFrame
    print(f"Companies count: {comp_df.select("company_id").distinct().count()}")
    print(f"Jobs count: {job_df.count()}")
    print(f"Postings count: {postings.select("job_id").distinct().count()}")

    # 1) Which company has the highest number of postings available
    company_with_most_postings(postings, comp_df, top_n=10)
    """--- IGNORE ---
    # 2) Which skills are most desirable
    most_desirable_skills(job_skill_df, top_n=20)

    # 3) Top 10 locations with postings
    top_locations(postings, top_n=10)

    # 4) Median salary per skill and highest medians
    median_salary_by_skill(job_skill_df, salaries_df, top_n=20)"""

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    main()
    