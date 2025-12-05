# ML Components — spark-analytics

This document summarizes the ML code in `spark-analytics/`, describes how to run the components, lists dependencies, and points to generated outputs.

Overview
--------
The repository provides several ML modules using Apache Spark (PySpark) and MLlib, plus a small set of scripts that use scikit-learn / NumPy for content-based recommendations.

Key ML modules 
- `ml_job_classifier.py`           — RandomForest-based job classifier (MLlib)
- `ml_job_classifier_xg.py`        — XGBoost-based job classifier (Spark XGBoost wrapper)
- `ml_skill_extractor.py`         — NLP-based skill extraction, TF-IDF and clustering
- `ml_recommender.py`             — Collaborative filtering (ALS) recommender
- `spark_recommender.py`          — TF-IDF content-based recommender (Spark + scikit/NumPy)
- `ml_salary_predictor.py`        — Salary prediction (Linear Regression)
- `ml_pipeline.py`                — Orchestrates the full ML pipeline and streaming inference
- `streaming_test_data_generator.py` — Generates sample CSV batches into `streaming_input/`

Dependencies
------------
The project dependencies are listed in `requirements.txt`. Key packages:

- `pyspark>=3.5.0`
- `py4j`
- `pandas`, `numpy`, `pyarrow`
- `scikit-learn`
- `xgboost` (used by `ml_job_classifier_xg.py`)
- `matplotlib`, `seaborn`

Install with:

```bash
pip install -r requirements.txt
```

Running the pipeline
--------------------
From the `spark-analytics` folder you can run the full ML pipeline or individual components.

Run the full pipeline (default: last 7 days):

```bash
python ml_pipeline.py --days-back 7
```

Run specified components only (choices: `classification`, `skills`, `recommendation`, `salary`):

```bash
python ml_pipeline.py --components classification skills
```

Save ML outputs (CSV summaries) when running the pipeline:

```bash
python ml_pipeline.py --days-back 7 --save
```

Run individual modules for development / debugging

```bash
# Random Forest classifier (quick test)
python ml_job_classifier.py

# XGBoost classifier (improved training pipeline)
python ml_job_classifier_xg.py

# Skill extraction / clustering
python ml_skill_extractor.py

# ALS recommender (uses users.csv if present; otherwise synthetic)
python ml_recommender.py

# Content-based recommender (Spark + NumPy) — writes to analytics_output/Spark_recommendation_results/
python spark_recommender.py

# Salary predictor
python ml_salary_predictor.py

# Generate streaming test batches
python streaming_test_data_generator.py
```

Notes about running
- The scripts expect the repo layout (see top-level `data/` and `spark-analytics/streaming_input/`).
- `ml_recommender.py` will try to read `data/users.csv` — if not found it generates synthetic interactions.
- `spark_recommender.py` expects `data/users.csv` and writes to `analytics_output/Spark_recommendation_results/`.

Saved outputs and visualizations
-------------------------------
ML outputs are written under `spark-analytics/analytics_output/` by the pipeline. Notable locations and files present in this workspace:

- `analytics_output/visuals/` (sample files available):
	- `top_skills_top_industry.png`
	- `avg_skills_by_industry.png`
	- `cross_industry_skills.png`
	- `skill_cluster_heatmap.png`
	- `skill_cluster_sizes.png`
	- `classification_class_distribution.png`
	- `stream_experience_levels.png`
	- `stream_top_titles.png`
	- `recs_top_users_unique_jobs.png`
	- `recommendation_score_hist.png`

- `analytics_output/ml_outputs/` — CSV summaries produced by `ml_pipeline.py --save` (classification, skill clusters, recommendations).
- `analytics_output/Spark_recommendation_results/` — output from `spark_recommender.py` (recommendations CSV).
- `streaming_input/` — test CSV batches (files `test_batch_0000.csv` … `test_batch_0009.csv`) used for streaming demos.

Module summaries (quick)
------------------------
- `ml_job_classifier.py`
	- Uses Spark MLlib `RandomForestClassifier` to train on text features (title + description) plus metadata.
	- Produces a `prediction` column and prints model comparison/evaluation.

- `ml_job_classifier_xg.py`
	- XGBoost-based classifier using `xgboost.spark.SparkXGBClassifier`.
	- Improved labeling from title+description, sampling, class balancing, and detailed per-category metrics.

- `ml_skill_extractor.py`
	- Extracts skills using an internal vocabulary and regex matching, builds TF-IDF features, and clusters jobs with KMeans.
	- Functions: `extract_top_skills`, `analyze_skill_combinations`, `cluster_jobs_by_skills`.

- `ml_recommender.py`
	- Trains an ALS model from user-job interactions (or creates synthetic interactions) and returns recommendations.
	- Helpers to persist recommendations and recommend for specific users.

- `spark_recommender.py`
	- Content-based recommender: TF-IDF on job text, cosine-similarity via NumPy to generate per-user recommendations (writes CSV outputs).

- `ml_salary_predictor.py`
	- Linear regression model to predict salary from extracted features: numeric salary extraction, experience years, high-value skill flags, and TF-IDF description vectors.

- `ml_pipeline.py`
	- Orchestrator: loads data via `data_loader.DataLoader`, runs the requested ML components, persists sampled CSV summaries under `analytics_output/ml_outputs/` and `ml_results/` when `--save` is passed, and can run a streaming inference step.

Dependencies and environment tips
--------------------------------
- Use the `requirements.txt` in this folder to install Python dependencies.
- Ensure Java 11+ is available for Spark.
- The XGBoost Spark wrapper requires the `xgboost` Python package and a compatible Spark build; if you encounter issues, use the RandomForest classifier as a fallback.

Troubleshooting notes
---------------------
- If Spark raises `Java heap space`, increase driver memory via environment variables or by editing the SparkSession builder in the scripts (e.g. `.config("spark.driver.memory","8g")`).
- If streaming jobs do not start, verify `streaming_input/` contains CSV batches and that schema matches expected columns.
- For missing `users.csv` (recommendations), the code falls back to synthetic interactions.
---



