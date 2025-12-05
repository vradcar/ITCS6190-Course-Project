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


def load_ml_outputs(spark_dir):
    """Load ML model outputs and streaming data (pandas for simplicity)."""
    ml_dir = os.path.join(spark_dir, "analytics_output", "ml_outputs")
    stream_dir = os.path.join(spark_dir, "streaming_input")
    outputs = {}

    def _read_csv(path):
        try:
            if os.path.exists(path):
                return pd.read_csv(path)
        except Exception:
            pass
        return pd.DataFrame()

    outputs["classification_predictions"] = _read_csv(os.path.join(ml_dir, "classification_predictions.csv"))
    outputs["job_recommendations"] = _read_csv(os.path.join(ml_dir, "job_recommendations.csv"))
    outputs["skill_clusters"] = _read_csv(os.path.join(ml_dir, "skill_clusters.csv"))

    # Streaming latest batch (pick the highest index file)
    stream_batch = pd.DataFrame()
    try:
        if os.path.exists(stream_dir):
            files = [f for f in os.listdir(stream_dir) if f.startswith("test_batch_") and f.endswith(".csv")]
            if files:
                latest = sorted(files)[-1]
                stream_batch = pd.read_csv(os.path.join(stream_dir, latest))
    except Exception:
        pass

    outputs["stream_batch"] = stream_batch
    return outputs


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


def create_visualizations(skills_by_industry, multi_skill_jobs, cross_industry_skills, visuals_out, ml_outputs):
    skills_by_industry_pd = _safe_to_pandas(skills_by_industry)
    avg_skills_pd = _safe_to_pandas(multi_skill_jobs)
    cross_industry_pd = _safe_to_pandas(cross_industry_skills)

    print("Generating visualizations from ML outputs and stream data...")

    # Visualization 1: Top Skills in the #1 Industry (sorted)
    try:
        if not avg_skills_pd.empty:
            top_industry = avg_skills_pd.nlargest(1, 'avg_skills_required')['industry_name'].iloc[0]
            data = (
                skills_by_industry_pd[skills_by_industry_pd['industry_name'] == top_industry]
                .sort_values('skill_count', ascending=False)
                .head(10)
            )
            
            plt.figure(figsize=(10, 6))
            sns.barplot(data=data, y='skill_name', x='skill_count', hue='skill_name', legend=False)
            plt.title(f'Top 3 Skills in {top_industry}', fontsize=14, fontweight='bold')
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

    # Visualization 2: Average skills required by industry (top 15, sorted)
    try:
        if not avg_skills_pd.empty:
            plt.figure(figsize=(12, 8))
            top_15_avg = avg_skills_pd.sort_values('avg_skills_required', ascending=False).head(15)
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

    # Visualization 3: Cross-industry skills (top 20, sorted)
    try:
        if not cross_industry_pd.empty:
            plt.figure(figsize=(12, 8))
            top_20_cross = cross_industry_pd.sort_values('num_industries', ascending=False).head(20)
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

    # Visualization 4: Stream data — title distribution
    try:
        sb = ml_outputs.get("stream_batch", pd.DataFrame())
        if not sb.empty and "title" in sb.columns:
            top_titles = sb["title"].value_counts().head(10).reset_index()
            top_titles.columns = ["title", "count"]
            plt.figure(figsize=(10,6))
            sns.barplot(data=top_titles, x="count", y="title", hue="title", legend=False)
            plt.title("Top Job Titles in Latest Stream Batch", fontsize=14, fontweight='bold')
            plt.xlabel("Count")
            plt.ylabel("Title")
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'stream_top_titles.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping stream_top_titles: No streaming data available")
    except Exception:
        print('⚠️  Failed to build stream_top_titles visualization')
        traceback.print_exc()

    # Visualization 5: Stream data — experience level distribution
    try:
        sb = ml_outputs.get("stream_batch", pd.DataFrame())
        col_name = None
        for c in ["formatted_experience_level", "experience_level"]:
            if c in sb.columns:
                col_name = c
                break
        if not sb.empty and col_name:
            dist = sb[col_name].value_counts().reset_index()
            dist.columns = ["experience_level", "count"]
            plt.figure(figsize=(8,6))
            sns.barplot(data=dist, x="experience_level", y="count")
            plt.title("Experience Levels in Latest Stream Batch", fontsize=14, fontweight='bold')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'stream_experience_levels.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping stream_experience_levels: No data available")
    except Exception:
        print('⚠️  Failed to build stream_experience_levels visualization')
        traceback.print_exc()

    # Visualization 6: Classification predictions — class distribution (use job_category if available)
    try:
        cls = ml_outputs.get("classification_predictions", pd.DataFrame())
        col_name = None
        for c in ["job_category", "predicted_class", "prediction", "label_predicted"]:
            if c in cls.columns:
                col_name = c
                break
        if not cls.empty and col_name:
            dist = cls[col_name].value_counts().reset_index()
            dist.columns = ["class", "count"]
            plt.figure(figsize=(8,6))
            sns.barplot(data=dist.sort_values('count', ascending=False), x="class", y="count")
            plt.title("Classification Predictions Distribution", fontsize=14, fontweight='bold')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'classification_class_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping classification_class_distribution: No data available")
    except Exception:
        print('⚠️  Failed to build classification_class_distribution visualization')
        traceback.print_exc()

    # Visualization 7: Recommendations — score histogram (use available numeric confidence proxy)
    try:
        recs = ml_outputs.get("job_recommendations", pd.DataFrame())
        if not recs.empty and "score" in recs.columns:
            plt.figure(figsize=(8,6))
            sns.histplot(recs["score"].dropna(), bins=20)
            plt.title("Recommendation Score Histogram", fontsize=14, fontweight='bold')
            plt.xlabel("Score")
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'recommendation_score_hist.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping recommendation_score_hist: No data available or column missing")
    except Exception:
        print('⚠️  Failed to build recommendation_score_hist visualization')
        traceback.print_exc()

    # Visualization 8: Recommendations — top recommended jobs per user (unique jobs)
    try:
        recs = ml_outputs.get("job_recommendations", pd.DataFrame())
        if not recs.empty:
            if "user_id" in recs.columns and "job_index" in recs.columns:
                top = recs.groupby("user_id")["job_index"].nunique().reset_index().sort_values("job_index", ascending=False).head(10)
                plt.figure(figsize=(10,6))
                sns.barplot(data=top, x="job_index", y="user_id")
                plt.title("Top Users by Unique Jobs Recommended", fontsize=14, fontweight='bold')
                plt.xlabel("Unique Jobs Recommended")
                plt.ylabel("User ID")
                plt.tight_layout()
                plt.savefig(os.path.join(visuals_out, 'recs_top_users_unique_jobs.png'), dpi=300, bbox_inches='tight')
                plt.close()
            else:
                print("⚠️  Skipping recs_top_users_unique_jobs: Required columns missing")
        else:
            print("⚠️  Skipping recs_top_users_unique_jobs: No data available")
    except Exception:
        print('⚠️  Failed to build recs_top_users_unique_jobs visualization')
        traceback.print_exc()

    # Visualization 9: Skill clusters — cluster size distribution
    try:
        sc = ml_outputs.get("skill_clusters", pd.DataFrame())
        cluster_col = None
        for c in ["cluster_id", "cluster", "group"]:
            if c in sc.columns:
                cluster_col = c
                break
        if not sc.empty and cluster_col:
            top = sc[cluster_col].value_counts().reset_index()
            top.columns = ["cluster", "count"]
            plt.figure(figsize=(10,6))
            sns.barplot(data=top.head(20), x="count", y="cluster")
            plt.title("Skill Cluster Sizes (Top)", fontsize=14, fontweight='bold')
            plt.xlabel("Count")
            plt.ylabel("Cluster")
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'skill_cluster_sizes.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping skill_cluster_sizes: No data available")
    except Exception:
        print('⚠️  Failed to build skill_cluster_sizes visualization')
        traceback.print_exc()

    # Visualization 10: Skill clusters — cluster vs skill frequency heatmap (derive from extracted_skills)
    try:
        sc = ml_outputs.get("skill_clusters", pd.DataFrame())
        if not sc.empty and "cluster_id" in sc.columns and "extracted_skills" in sc.columns:
            # Expand extracted_skills (comma-separated) to rows
            expanded = sc.dropna(subset=["extracted_skills"]).copy()
            expanded = expanded.assign(skill_name=expanded["extracted_skills"].str.split(",")).explode("skill_name")
            expanded["skill_name"] = expanded["skill_name"].str.strip()
            pivot = expanded.groupby(["cluster_id", "skill_name"]).size().reset_index(name="count")
            pivot = pivot.pivot(index="skill_name", columns="cluster_id", values="count").fillna(0)
            plt.figure(figsize=(12,8))
            sns.heatmap(pivot, cmap="Blues")
            plt.title("Skill Frequency by Cluster", fontsize=14, fontweight='bold')
            plt.xlabel("Cluster")
            plt.ylabel("Skill")
            plt.tight_layout()
            plt.savefig(os.path.join(visuals_out, 'skill_cluster_heatmap.png'), dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("⚠️  Skipping skill_cluster_heatmap: Columns missing or no data")
    except Exception:
        print('⚠️  Failed to build skill_cluster_heatmap visualization')
        traceback.print_exc()

    print(f"Saved visualizations under {visuals_out}")


def main():
    spark = init_spark()
    exit_code = 0
    try:
        data_dir, query_out, visuals_out = resolve_paths()
        postings, job_skills, skill_map, job_industries, industry_map = load_data(spark, data_dir)
        ml_outputs = load_ml_outputs(os.path.dirname(os.path.abspath(__file__)))
        skills_by_industry, multi_skill_jobs, cross_industry_skills = run_queries(
            spark, job_skills, skill_map, job_industries, industry_map
        )
        persist_queries(skills_by_industry, multi_skill_jobs, cross_industry_skills, query_out)
        create_visualizations(skills_by_industry, multi_skill_jobs, cross_industry_skills, visuals_out, ml_outputs)
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
