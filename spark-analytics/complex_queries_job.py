#!/usr/bin/env python3
"""Complex analytics & visualization job.

Replicates notebook logic (complex_queries.ipynb) in a script so it can be
orchestrated via run.sh. Generates:
  - Aggregated query result parquet/CSV datasets
  - Eight visualizations (PNG) focused on student / job seeker insights

Outputs are written inside `spark-analytics/analytics_output`.
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, avg, rank, broadcast
from pyspark.sql.window import Window
import matplotlib
matplotlib.use("Agg")  # Headless environment safe backend
import matplotlib.pyplot as plt
import seaborn as sns
import traceback
import pandas as pd


def init_spark():
    spark = (
        SparkSession.builder
        .appName("LinkedIn Job Complex Analytics")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    print(f"Spark Version: {spark.version}")
    return spark


def resolve_paths():
    spark_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(spark_dir)
    data_dir = os.path.join(repo_root, "data")
    out_base = os.path.join(spark_dir, "analytics_output")
    query_out = os.path.join(out_base, "query_results")
    visuals_out = os.path.join(out_base, "visuals")
    os.makedirs(query_out, exist_ok=True)
    os.makedirs(visuals_out, exist_ok=True)
    return data_dir, query_out, visuals_out


def load_data(spark, data_dir):
    # Load with sampling to prevent OOM in local mode
    sample_limit = 20000
    print(f"Loading data with {sample_limit} row limit for stability...")
    
    postings = spark.read.csv(os.path.join(data_dir, "postings_cleaned.csv"), header=True, inferSchema=True).limit(sample_limit)
    job_skills = spark.read.csv(os.path.join(data_dir, "jobs", "job_skills.csv"), header=True, inferSchema=True).limit(sample_limit)
    job_industries = spark.read.csv(os.path.join(data_dir, "jobs", "job_industries.csv"), header=True, inferSchema=True).limit(sample_limit)
    
    # Small mapping tables - no limit needed
    skill_map = spark.read.csv(os.path.join(data_dir, "mappings", "skills.csv"), header=True, inferSchema=True)
    industry_map = spark.read.csv(os.path.join(data_dir, "mappings", "industries.csv"), header=True, inferSchema=True)
    
    print("Data loaded successfully (sampled)!")
    return postings, job_skills, skill_map, job_industries, industry_map


def run_queries(spark, job_skills, skill_map, job_industries, industry_map):
    industry_map_clean = industry_map.dropna()

    # Query 1: Top 10 skills per industry with ranking
    # Optimized with broadcast joins
    skills_by_industry = (
        job_skills
        .join(broadcast(skill_map), "skill_abr")
        .join(job_industries, "job_id")
        .join(broadcast(industry_map_clean), "industry_id")
        .groupBy("industry_name", "skill_name")
        .agg(count("*").alias("skill_count"))
        .withColumn("rank", rank().over(Window.partitionBy("industry_name").orderBy(desc("skill_count"))))
        .filter(col("rank") <= 10)
        .orderBy("industry_name", "rank")
    )

    # Query 2: Average number of skills per job by industry
    multi_skill_jobs = (
        job_skills
        .groupBy("job_id")
        .agg(count("skill_abr").alias("num_skills"))
        .join(job_industries, "job_id")
        .join(broadcast(industry_map_clean), "industry_id")
        .groupBy("industry_name")
        .agg(
            avg("num_skills").alias("avg_skills_required"),
            count("job_id").alias("total_jobs")
        )
        .orderBy(desc("avg_skills_required"))
    )

    # Query 3: Cross-industry skill overlap
    cross_industry_skills = (
        job_skills
        .join(broadcast(skill_map), "skill_abr")
        .join(job_industries, "job_id")
        .join(broadcast(industry_map_clean), "industry_id")
        .select("skill_name", "industry_name")
        .distinct()
        .groupBy("skill_name")
        .agg(count("industry_name").alias("num_industries"))
        .orderBy(desc("num_industries"))
    )

    return skills_by_industry, multi_skill_jobs, cross_industry_skills


def _safe_to_pandas(df, limit_rows=10000):
    """Convert a Spark DataFrame to pandas with a row cap to avoid OOM."""
    return df.limit(limit_rows).toPandas()

def persist_queries(skills_by_industry, multi_skill_jobs, cross_industry_skills, query_out):
    try:
        # Parquet writing disabled to avoid HADOOP_HOME errors on Windows
        # skills_by_industry.write.mode("overwrite").parquet(os.path.join(query_out, "skills_by_industry"))
        # multi_skill_jobs.write.mode("overwrite").parquet(os.path.join(query_out, "avg_skills_by_industry"))
        # cross_industry_skills.write.mode("overwrite").parquet(os.path.join(query_out, "cross_industry_skills"))
        
        # CSV (sampled) - using pandas to avoid Spark/Hadoop write issues
        _safe_to_pandas(skills_by_industry).to_csv(os.path.join(query_out, "skills_by_industry.csv"), index=False)
        _safe_to_pandas(multi_skill_jobs).to_csv(os.path.join(query_out, "avg_skills_by_industry.csv"), index=False)
        _safe_to_pandas(cross_industry_skills).to_csv(os.path.join(query_out, "cross_industry_skills.csv"), index=False)
        print(f"Saved query outputs (CSV only) under {query_out}")
    except Exception as e:
        print(f"❌ Failed persisting query outputs: {e}")
        raise


def create_visualizations(skills_by_industry, multi_skill_jobs, cross_industry_skills, visuals_out):
    skills_by_industry_pd = _safe_to_pandas(skills_by_industry)
    avg_skills_pd = _safe_to_pandas(multi_skill_jobs)
    cross_industry_pd = _safe_to_pandas(cross_industry_skills)

    print("Generating simplified visualizations...")

    # Visualization 1: Top Skills in the #1 Industry only (Simplified from subplots)
    try:
        if not avg_skills_pd.empty:
            top_industry = avg_skills_pd.nlargest(1, 'avg_skills_required')['industry_name'].iloc[0]
            data = skills_by_industry_pd[skills_by_industry_pd['industry_name'] == top_industry].head(10)
            
            plt.figure(figsize=(10, 6))
            sns.barplot(data=data, y='skill_name', x='skill_count', hue='skill_name', legend=False)
            plt.title(f'Top 10 Skills in {top_industry}', fontsize=14, fontweight='bold')
            plt.xlabel('Job Postings')
            plt.ylabel('Skill')
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'top_skills_top_industry.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping top_skills_top_industry: No data available")
    except Exception:
        print('⚠️  Failed to build top_skills_top_industry visualization')
        traceback.print_exc()

    # Visualization 2: Average skills required by industry (top 15)
    try:
        if not avg_skills_pd.empty:
            plt.figure(figsize=(12, 8))
            top_15_avg = avg_skills_pd.head(15)
            sns.barplot(data=top_15_avg, y='industry_name', x='avg_skills_required', hue='industry_name', legend=False)
            plt.title('Average Skills Required by Industry (Top 15)', fontsize=14, fontweight='bold')
            plt.xlabel('Avg Skills')
            plt.ylabel('Industry')
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'avg_skills_by_industry.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping avg_skills_by_industry: No data available")
    except Exception:
        print('⚠️  Failed to build avg_skills_by_industry visualization')
        traceback.print_exc()

    # Visualization 3: Cross-industry skills (top 20)
    try:
        if not cross_industry_pd.empty:
            plt.figure(figsize=(12, 8))
            top_20_cross = cross_industry_pd.head(20)
            sns.barplot(data=top_20_cross, y='skill_name', x='num_industries', hue='skill_name', legend=False)
            plt.title('Most Versatile Skills (Top 20)', fontsize=14, fontweight='bold')
            plt.xlabel('Industry Count')
            plt.ylabel('Skill')
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'cross_industry_skills.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping cross_industry_skills: No data available")
    except Exception:
        print('⚠️  Failed to build cross_industry_skills visualization')
        traceback.print_exc()

    print(f"Saved simplified visualizations under {visuals_out}")


def main():
    spark = init_spark()
    exit_code = 0
    try:
        data_dir, query_out, visuals_out = resolve_paths()
        postings, job_skills, skill_map, job_industries, industry_map = load_data(spark, data_dir)
        skills_by_industry, multi_skill_jobs, cross_industry_skills = run_queries(
            spark, job_skills, skill_map, job_industries, industry_map
        )
        persist_queries(skills_by_industry, multi_skill_jobs, cross_industry_skills, query_out)
        create_visualizations(skills_by_industry, multi_skill_jobs, cross_industry_skills, visuals_out)
        print("\nComplex analytics job complete.")
        # Summary counts (lightweight actions)
        print("Summary:")
        print(f"  Industries w/ skills ranked: {skills_by_industry.select('industry_name').distinct().count()}")
        print(f"  Skill ranking rows: {skills_by_industry.count()}")
        print(f"  Industries (avg skills): {multi_skill_jobs.count()}")
        print(f"  Cross-industry skills: {cross_industry_skills.count()}")
    except Exception as e:
        print(f"❌ Complex analytics job failed: {e}")
        exit_code = 1
    finally:
        try:
            spark.stop()
        except Exception:
            pass
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
