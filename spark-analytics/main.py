from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    percentile_approx,
    desc,
    when
)
import os

# Get base directory (repo root)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")

spark = SparkSession.builder.appName("LinkedInJobAnalysis").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# -----------------------------
# Data loading helpers
# -----------------------------
def load_comp_data():
    try:
        comp = spark.read.csv(
            os.path.join(data_dir, "companies", "companies.csv"),
            header=True,
            inferSchema=True,
        )
        comp_ind = spark.read.csv(
            os.path.join(data_dir, "companies", "company_industries.csv"),
            header=True,
            inferSchema=True,
        )
        comp_spel = spark.read.csv(
            os.path.join(data_dir, "companies", "company_specialities.csv"),
            header=True,
            inferSchema=True,
        )
        employee_counts = spark.read.csv(
            os.path.join(data_dir, "companies", "employee_counts.csv"),
            header=True,
            inferSchema=True,
        )
    except Exception as e:
        print(f"Error loading company data: {e}")
        print("Please ensure company CSVs are in the data directory.")
        exit(1)

    comp_df = (
        comp.join(comp_ind, "company_id", "left")
        .join(comp_spel, "company_id", "left")
        .join(employee_counts, "company_id", "left")
    )

    print("--- Company DataFrames Loaded and Enriched Successfully ---")
    comp_df.printSchema()
    return comp_df


def load_job_data():
    try:
        job_ind = spark.read.csv(
            os.path.join(data_dir, "jobs", "job_industries.csv"),
            header=True,
            inferSchema=True,
        )
        job_skill = spark.read.csv(
            os.path.join(data_dir, "jobs", "job_skills.csv"),
            header=True,
            inferSchema=True,
        )
        job_sal = spark.read.csv(
            os.path.join(data_dir, "jobs", "salaries.csv"),
            header=True,
            inferSchema=True,
        )
    except Exception as e:
        print(f"Error loading job data: {e}")
        print("Please ensure job CSVs are in the data directory.")
        exit(1)

    job_df = (
        job_ind.join(job_skill, "job_id", "left")
        .join(job_sal, "job_id", "left")
    )

    print("--- Job DataFrames Loaded and Enriched Successfully ---")
    job_df.printSchema()
    return job_df, job_skill, job_sal


def load_posting_data():
    try:
        postings = spark.read.csv(
            os.path.join(data_dir, "postings_cleaned.csv"),
            header=True,
            inferSchema=True,
            multiLine=True,
            escape='"',
        )
    except Exception as e:
        print(f"Error loading posting data: {e}")
        print("Please ensure postings CSV is present.")
        exit(1)

    print("--- Posting DataFrame Loaded Successfully ---")
    postings.printSchema()
    return postings


# -----------------------------
# Analysis / ML-ish functions
# -----------------------------
def company_with_most_postings(postings_df, comp_df=None, top_n=10):
    """Return top companies by number of postings."""
    keyed = postings_df.filter(col("company_id").isNotNull())

    counts = (
        keyed.groupBy("company_id")
        .agg(count("*").alias("postings"))
        .orderBy(desc("postings"))
    )

    print("\nSchema of postings-per-company counts:")
    counts.printSchema()
    counts.show(5, truncate=False)

    if comp_df is not None:
        print("We found the companies")

        # Safe casting: only allow numeric company_ids to avoid SparkNumberFormatException
        counts_str = counts.select(
            when(col("company_id").rlike("^[0-9]+$"), col("company_id"))
            .cast("string")
            .alias("company_id"),
            col("postings"),
        )

        comp_names = comp_df.select(
            when(col("company_id").rlike("^[0-9]+$"), col("company_id"))
            .cast("string")
            .alias("company_id"),
            col("name").alias("company_name"),
        )

        joined = counts_str.join(comp_names, on="company_id", how="left")

        print(f"\n=== [1] Top {top_n} companies by number of postings ===")
        joined.select("company_name", "postings").show(top_n, truncate=False)
        return joined
    else:
        counts.show(top_n, truncate=False)
        return counts


def most_desirable_skills(job_skill_df, top_n=20):
    skill_counts = (
        job_skill_df.groupBy("skill_abr")
        .agg(count("*").alias("count"))
        .orderBy(desc("count"))
    )
    print(f"\n=== [2] Top {top_n} most desirable skills ===")
    skill_counts.show(top_n, truncate=False)
    return skill_counts


def top_locations(postings_df, top_n=10):
    loc_counts = (
        postings_df.groupBy("location")
        .agg(count("*").alias("postings"))
        .orderBy(desc("postings"))
    )
    print(f"\n=== [3] Top {top_n} locations by postings ===")
    loc_counts.show(top_n, truncate=False)
    return loc_counts


def median_salary_by_skill(job_skill_df, salaries_df, top_n=20):
    sal_filtered = (
        salaries_df.filter(
            (col("pay_period") == "YEARLY")
            & (col("currency") == "USD")
            & (col("med_salary").isNotNull())
        )
        .select(col("job_id"), col("med_salary").cast("double").alias("med_salary"))
    )

    skill_sal = job_skill_df.join(sal_filtered, "job_id", "inner")

    median_by_skill = (
        skill_sal.groupBy("skill_abr")
        .agg(
            percentile_approx(col("med_salary"), 0.5).alias("median_salary"),
            count("*").alias("num_jobs"),
        )
        .orderBy(desc("median_salary"))
    )

    print(f"\n=== [4] Top {top_n} skills by median yearly salary ===")
    median_by_skill.show(top_n, truncate=False)
    return median_by_skill


# -----------------------------
# Main pipeline
# -----------------------------
def main():
    comp_df = load_comp_data()
    job_df, job_skill_df, salaries_df = load_job_data()
    postings = load_posting_data()

    print("\n=== Dataset sizes ===")
    print(f"Companies: {comp_df.select('company_id').distinct().count()}")
    print(f"Jobs: {job_df.count()}")
    print(f"Postings: {postings.select('job_id').distinct().count()}")

    # Run analytics
    company_with_most_postings(postings, comp_df, top_n=10)
    most_desirable_skills(job_skill_df, top_n=20)
    top_locations(postings, top_n=10)
    median_salary_by_skill(job_skill_df, salaries_df, top_n=20)

    spark.stop()


if __name__ == "__main__":
    main()
