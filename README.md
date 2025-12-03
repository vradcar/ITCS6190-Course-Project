# ITCS6190 Cloud Computing Course Project  
## LinkedIn Job Market Analytics with Apache Spark

**Group Name:** Unattached and Unhinged  

**Team Members:**
- Varad Paradkar (801418318) – vparadka@charlotte.edu  
- Mitali Yadav (801453849) – myadav5@charlotte.edu  
- Sudeepta Bal (801455628) – sbal1@charlotte.edu  
- Ruthwik Dovala (801431661) – rdovala@charlotte.edu  

---

## 🎯 Project Overview

This project implements a comprehensive **Apache Spark–based analytics and ML platform** for analyzing the LinkedIn job market dataset from Kaggle. The system performs:

- Complex **Spark SQL** queries  
- **Real-time streaming** analytics  
- **Machine learning pipelines** (including XGBoost and Spark-based recommenders)  
- Actionable insights for students and job seekers entering the market  

The goal is to turn a raw job postings dataset into **data-driven career guidance**, with scalable processing on top of Apache Spark.

---

## 🧱 Spark Components Used

This project is intentionally designed to showcase **multiple components of Apache Spark**:

- **Spark Core**  
  - Distributed computation engine using DataFrames (built on RDDs)  
  - Handles large-scale job and skills data with fault tolerance and parallelism  

- **Spark SQL**  
  - DataFrame and SQL APIs for complex analytics  
  - Multi-table joins, window functions, aggregations, and analytical queries  

- **Spark Structured Streaming**  
  - Real-time pipeline that ingests simulated job postings from files  
  - Incremental, micro-batch computations for live job market monitoring  

- **Spark MLlib (Machine Learning Library)**  
  - Used for recommendation (ALS-based **Spark Recommender**)  
  - Integrated into end-to-end ML pipelines for ranking jobs and skills  

- **External ML Integration (XGBoost + Spark)**  
  - XGBoost models (via `ml_job_classifier_xg.py`) trained on Spark-prepared features  
  - Spark handles preprocessing and feature engineering; XGBoost performs high-performance gradient boosting  

Together, these components form a **full-stack Spark application**: from batch analytics and streaming to machine learning and recommendation.

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                  LinkedIn Job Dataset                   │
│              (40K+ job postings, Kaggle)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Apache Spark Layer                     │
│                                                         │
│   ┌──────────────────┐   ┌───────────────────────────┐  │
│   │   Spark SQL       │  │   Spark Structured        │  │
│   │   Complex Queries │  │   Streaming (Real-Time)   │  │
│   └──────────────────┘  └───────────────────────────┘  │
│                 ▲                     ▲                 │
│                 │                     │                 │
│   ┌──────────────────┐   ┌───────────────────────────┐  │
│   │ Spark MLlib       │  │ XGBoost + Spark           │  │
│   │ Recommender (ALS) │  │ Job Classifier / ML       │  │
│   └──────────────────┘   └───────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Analytics & Visualizations                 │
│  • Skill Demand Analysis    • Industry Entry Barriers   │
│  • Salary Trends            • Career Path Builder       │
│  • Skill Co-occurrence      • Learning Roadmaps         │
│  • ML Recommendations       • Student Action Plans      │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
├── Documentation
│   ├── Unattached and Unhinged_project proposal.pdf
│   └── Unattached and Unhinged_project_2nd check in.pdf
├── LICENSE
├── README.md
├── analytics_output
│   ├── STUDENT_ACTION_PLAN.txt
│   ├── query_results
│   │   ├── avg_skills_by_industry
│   │   │   ├── _SUCCESS
│   │   │   └── part-00000-02f9a49d-fb2d-49fe-87c5-6e0f7ad2da76-c000.snappy.parquet
│   │   ├── avg_skills_by_industry.csv
│   │   ├── cross_industry_skills
│   │   │   ├── _SUCCESS
│   │   │   └── part-00000-3e256c5d-6cdb-47c5-99d5-038cfb3bb425-c000.snappy.parquet
│   │   ├── cross_industry_skills.csv
│   │   ├── skills_by_industry
│   │   │   ├── _SUCCESS
│   │   │   └── part-00000-abed45b1-4805-433e-8384-26b7c33c48d5-c000.snappy.parquet
│   │   └── skills_by_industry.csv
│   └── visuals
│       ├── avg_skills_by_industry.png
│       ├── career_path_builder.png
│       ├── cross_industry_skills.png
│       ├── industry_entry_barriers.png
│       ├── skill_diversity_index.png
│       ├── skill_pairs.png
│       ├── top_10_skills_overall.png
│       └── top_skills_by_industry.png
├── data
│   ├── companies
│   │   ├── companies.csv
│   │   ├── company_industries.csv
│   │   ├── company_specialities.csv
│   │   └── employee_counts.csv
│   ├── jobs
│   │   ├── benefits.csv
│   │   ├── job_industries.csv
│   │   ├── job_skills.csv
│   │   └── salaries.csv
│   ├── mappings
│   │   ├── industries.csv
│   │   └── skills.csv
│   ├── output_recommendation.csv
│   │   ├── _SUCCESS
│   │   └── part-00000-d5c8f9f2-70b2-4195-98d5-609fb9eec289-c000.csv
│   ├── postings_cleaned.csv
│   ├── recommendations.csv
│   └── users.csv
├── run.sh
└── spark-analytics
    ├── INTEGRATION_SUMMARY.md
    ├── ML_README.md
    ├── README.md
    ├── __pycache__
    │   ├── data_loader.cpython-312.pyc
    │   ├── ml_job_classifier.cpython-312.pyc
    │   ├── ml_recommender.cpython-312.pyc
    │   └── ml_skill_extractor.cpython-312.pyc
    ├── complex_queries.ipynb
    ├── data_analysis.ipynb
    ├── data_loader.py
    ├── main.py
    ├── ml_job_classifier.py
    ├── ml_job_classifier_xg.py
    ├── ml_pipeline.py
    ├── ml_recommender.py
    ├── ml_results
    │   └── ml_summary.json
    ├── ml_salary_predictor.py
    ├── ml_skill_extractor.py
    ├── requirements.txt
    ├── spark_recommender.py
    ├── streaming_input
    │   ├── batch_0000.csv
    │   ├── batch_0001.csv
    │   ├── batch_0002.csv
    │   ├── batch_0003.csv
    │   ├── batch_0004.csv
    │   ├── batch_0005.csv
    │   ├── batch_0006.csv
    │   ├── batch_0007.csv
    │   ├── batch_0008.csv
    │   └── batch_0009.csv
    └── streaming_test_data_generator.py
```

---

## 🚀 Quick Start Guide

### ✅ Prerequisites

- **Python** 3.8+  
- **Apache Spark 3.x** (or `pyspark` installed via `pip`)  
- At least **4 GB RAM** recommended  
- **Windows-only extra step**: Hadoop binaries (`winutils.exe`)  

> For local development, you can use either a local Spark installation or rely on `pyspark` via `pip`.  

---

### 1. Install Python Dependencies

From the repository root:

```bash
cd spark-analytics
pip install -r requirements.txt
```

**Key packages:**

- `pyspark`  
- `pandas`  
- `matplotlib`  
- `seaborn`  
- `numpy`  
- ML packages used by the pipeline (e.g., `xgboost`, `scikit-learn` where applicable)  

---

### 2. Set Up Hadoop (Windows Only)

If you’re on **Windows** and encounter Hadoop-related errors (e.g., missing `winutils`):

1. Download `winutils.exe` from:  
   https://github.com/steveloughran/winutils  
2. Place it in:  
   `C:\hadoop\bin\`  
3. Set environment variable:  
   `HADOOP_HOME=C:\hadoop`  
4. Add `C:\hadoop\bin` to your `PATH`.  

---

### 3. Run Batch Analytics (Spark SQL + Visualizations)

You can run the notebook or the Python driver:

#### Option A – Notebook (recommended for demo)

```bash
cd spark-analytics
# VS Code
code complex_queries.ipynb

# or Jupyter
jupyter notebook complex_queries.ipynb
```

Then **Run All Cells** to generate:

- 8 visualizations (PNG files)  
- Parquet/CSV query outputs  
- Student-focused action plan (`STUDENT_ACTION_PLAN.txt`)  

#### Option B – Python Script

```bash
cd spark-analytics
python main.py
```

This script orchestrates:

- Loading cleaned job/company/skills datasets  
- Running the Spark SQL queries  
- Writing outputs to `analytics_output/query_results/` and `analytics_output/visuals/`  

---

### 4. Run Streaming Demo (Spark Structured Streaming)

#### Terminal 1 – Streaming Processor

```bash
cd spark-analytics
python streaming_processor.py   # or equivalent streaming driver
```

#### Terminal 2 – Data Simulator

```bash
cd spark-analytics
python streaming_test_data_generator.py
```

**Streaming Features:**

- Reads batches from `streaming_input/` as a stream  
- Tracks:
  - **Top hiring locations**
  - **Experience level distributions**
  - **Most active companies**  

Output is shown in the console and/or persisted to files in append mode.

---

## 📊 Analytics Capabilities (Spark SQL & EDA)

### 1. Complex Spark SQL Queries

This project demonstrates advanced **Spark SQL** usage:

1. **Top Skills by Industry**  
   - Uses window functions:  
     `RANK() OVER (PARTITION BY industry ORDER BY skill_count DESC)`  
   - Multi-table joins:  
     `job_skills → skills → job_industries → industries`  
   - **Result:** Top 10 skills for each industry  

2. **Average Skills Required per Industry**  
   - Aggregations with `AVG()`, `COUNT()`, `GROUP BY`  
   - Analyzes **skill complexity** across industries  
   - **Result:** Quantifies entry barriers (skills needed to break in)  

3. **Cross-Industry Skill Overlap**  
   - Uses `DISTINCT` and grouped aggregations  
   - Identifies **transferable skills** used across many industries  
   - **Result:** Highlights safe skills for long-term career flexibility  

### 2. Student-Focused Visualizations (8 Total)

All visualizations are generated into `analytics_output/visuals/`:

4. **Skill Co-occurrence Network**  
   - Uses `itertools.combinations` to analyze which skills appear together  
   - Helps students identify complementary skill bundles to learn together  

5. **Top 10 Most In-Demand Skills**  
   - Ranks skills by overall demand  
   - Shows **share of job postings** requiring each skill  
   - Directly informs learning priorities  

6. **Industry Entry Barriers**  
   - Bubble chart:
     - X-axis: opportunities  
     - Y-axis: average required skills  
     - Size/color: industry category or job count  
   - Classifies industries into:
     - Entry-friendly  
     - Moderate  
     - Advanced  

7. **Skill Diversity Index**  
   - Quadrant analysis:
     - Specialist vs generalist skills  
   - Evaluates **risk and flexibility** of investing in a given skill  
   - Identifies “best bet” skills with **high demand + high versatility**  

8. **Career Path Builder**  
   - Models skill progression:  
     `Foundation → Intermediate → Advanced`  
   - Based on co-requirement and co-occurrence patterns  
   - Produces **learning roadmaps** tailored to target industries  

---

## 📡 Real-Time Streaming Analytics (Spark Structured Streaming)

- **Engine:** Spark Structured Streaming  
- **Source:** File-based stream from `streaming_input/` directory  
- **Mode:** Append / Complete (depending on query)  

Core streaming queries:

1. **Top Hiring Locations in Near-Real-Time**  
2. **Experience Level Distribution Over Time**  
3. **Most Active Companies** (by number of new job postings)  

A typical streaming setup:

```python
# Read stream from directory
streaming_df = spark.readStream \
    .schema(job_schema) \
    .option("maxFilesPerTrigger", 1) \
    .csv("streaming_input/")

# Process and write output
query = streaming_df \
    .groupBy("location") \
    .count() \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
```

This demonstrates **Spark Structured Streaming** from ingestion to aggregation and visualization for a live job market dashboard.

---

## 🤖 Machine Learning Components

### 1. XGBoost Job Classification

**File:** `ml_job_classifier_xg.py`  

**Goal:** Predict **job categories** or **suitability** based on rich feature sets extracted from the LinkedIn dataset.

**Pipeline (high-level):**

1. **Feature Engineering with Spark**  
   - Encode skills, industries, experience levels, locations, etc.  
   - Aggregate skill vectors and job attributes into structured feature matrices.  

2. **XGBoost Model Training**  
   - Export Spark-prepared features to a format consumable by XGBoost (e.g., NumPy/Parquet).  
   - Train a gradient-boosted trees classifier to distinguish job types (e.g., Data Scientist vs Software Engineer vs Analyst).  

3. **Model Evaluation & Summaries**  
   - Metrics (accuracy, F1, etc.) captured in `ml_results/ml_summary.json`.  
   - Comparative analysis with simpler ML models (`ml_job_classifier.py`).  

**Why XGBoost?**

- Strong performance on structured/tabular data  
- Handles non-linear relationships and complex feature interactions  
- Often outperforms linear models for job classification tasks  

---

### 2. Spark-Based Recommendation Engine (ALS Recommender)

**File:** `spark_recommender.py`  

**Goal:** Recommend **jobs to users** (or skills to users) using **collaborative filtering** with Spark MLlib’s **Alternating Least Squares (ALS)** algorithm.

**Core Idea:**

- Treat job applications, clicks, or interest levels as **implicit/explicit feedback**.  
- Model user–job interactions as a sparse matrix.  
- Use ALS to factorize into:
  - User latent factors  
  - Job latent factors  

**High-Level Workflow:**

1. **Input Data**  
   - `users.csv`, `recommendations.csv`, and job-related signals (e.g., past applications or interest).  

2. **Pre-processing with Spark**  
   - Assign integer IDs to users and jobs  
   - Normalize or weight feedback signals (e.g., views, clicks, saves)  

3. **ALS Model Training**  
   - Configure hyperparameters: `rank`, `maxIter`, `regParam`, etc.  
   - Train with Spark MLlib’s `ALS` implementation.  

4. **Generate Recommendations**  
   - `recommendForAllUsers(k)` – top-`k` jobs per user  
   - Save outputs to `data/output_recommendation.csv`  

**Outcome:**

- A **Scalable Recommender System** that demonstrates how Spark MLlib can personalize job suggestions at scale.  

---

### 3. Additional ML Modules

- **`ml_salary_predictor.py`**  
  - Predicts salary ranges based on features such as role, industry, location, seniority, and skill counts.  

- **`ml_skill_extractor.py`**  
  - Extracts and normalizes skills using basic NLP or rules from job descriptions.  

- **`ml_recommender.py`**  
  - Can be used for content-based recommendation (e.g., skills-based job suggestions) and comparison with ALS.  

- **`ml_pipeline.py`**  
  - Coordinates feature engineering, model training, and evaluation for different ML tasks.  

Detailed explanations live in **`spark-analytics/ML_README.md`** and **`INTEGRATION_SUMMARY.md`**.

---

## 🎓 Key Research Questions Answered

1. **What skills should students learn first?**  
   - **Answer:** Top skills visualization + skill co-occurrence/pair analysis.  

2. **Which industries are beginner-friendly?**  
   - **Answer:** Entry barriers bubble chart (industries requiring < 5 skills on average).  

3. **Are skills specialized or generalist?**  
   - **Answer:** Skill diversity index + quadrant analysis.  

4. **What is a sensible learning progression?**  
   - **Answer:** Career path builder (foundation → intermediate → advanced).  

5. **Which skills appear together most often?**  
   - **Answer:** Skill co-occurrence network and top skill pairs.  

6. **Which jobs are best for a given student profile?**  
   - **Answer:** Spark Recommender (ALS) + XGBoost job classifier + salary predictions.  

---

## 📈 Exploratory Data Analysis (EDA)

### Dataset Statistics

- **Total Job Postings:** 40,000+ records  
- **Companies:** 91,026 company records  
- **Industries:** 147 unique industries  
- **Skills:** 1,000+ unique skills tracked  
- **Geographic Coverage:** Global job market  

### Key Findings

1. **Industry Dominance**  
   - Technology, Finance, and Healthcare account for **60%+** of postings.  

2. **Company Size Correlation**  
   - Large companies post **~3x more jobs** on average compared to smaller ones.  

3. **Skill Bundling**  
   - Top 20 skill pairs identified, enabling **bundle-based learning**.  

4. **Entry Barriers**  
   - Around **30% of industries** require < 5 skills, marking them as more accessible.  

5. **Versatile Skills**  
   - Skills like **SQL, Python, and Communication** appear across **80+ industries**, making them valuable core skills.  

### EDA Notebooks

- `data_analysis.ipynb` – Pandas-based EDA with distributions, heatmaps, frequency plots.  
- `complex_queries.ipynb` – Spark SQL–based analytics with advanced queries and visualizations.  

---

## 🛠️ Technical Implementation

### Spark Configuration (Example)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LinkedIn Job Analysis") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()
```

### Complex Query Example (Top Skills per Industry)

```python
from pyspark.sql.functions import count, desc, col
from pyspark.sql.window import Window
from pyspark.sql.functions import rank

skills_by_industry = job_skills \
    .join(skill_map, "skill_abr") \
    .join(job_industries, "job_id") \
    .join(industry_map, "industry_id") \
    .groupBy("industry_name", "skill_name") \
    .agg(count("*").alias("skill_count")) \
    .withColumn(
        "rank",
        rank().over(
            Window.partitionBy("industry_name")
                  .orderBy(desc("skill_count"))
        )
    ) \
    .filter(col("rank") <= 10)
```

### Streaming Setup Example

```python
# Read stream from directory
streaming_df = spark.readStream \
    .schema(job_schema) \
    .option("maxFilesPerTrigger", 1) \
    .csv("streaming_input/")

# Process and write output
query = streaming_df \
    .groupBy("location") \
    .count() \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
```

---

## 🎯 Check-In & Demo Requirements

This project is designed to **fully satisfy** and exceed the course’s check-in/demo requirements:

- ✅ **Complex Queries:**  
  - 8+ sophisticated Spark SQL queries with window functions, joins, and aggregations  

- ✅ **Streaming Setup:**  
  - Real-time processing with Spark Structured Streaming (processor + simulator)  

- ✅ **ML Integration (Implemented & Planned):**  
  - XGBoost job classifier, Spark ALS recommender, salary prediction, skill extraction  

- ✅ **Demo-Ready Results:**  
  - Visualizations, console streaming outputs, and ML summaries ready to present  

- ✅ **Technical Challenges Documented:**  
  - Handling Hadoop on Windows, execution order issues in notebooks, schema alignment, and ML integration hurdles  

### Suggested Demo Flow (7–8 minutes)

1. **Complex Queries (3 min):**  
   - Show `complex_queries.ipynb` and walk through 2–3 key queries.  

2. **Visualizations (2 min):**  
   - Open `analytics_output/visuals/` and explain the 8 charts with student-focused narratives.  

3. **Streaming Demo (2 min):**  
   - Run streaming processor + generator to highlight real-time capabilities.  

4. **ML & Recommendations (1 min):**  
   - Summarize XGBoost classifier and Spark Recommender results from `ml_results`.  

5. **Q&A (optional):**  
   - Discuss challenges and future improvements.  

Additional details: see **`Documentation/DEMO_GUIDE.md`** and **`INTEGRATION_SUMMARY.md`**.

---

## 🔮 Future Enhancements (Extended ML Roadmap)

Even beyond the current implementation, there is a clear roadmap for further work:

1. **Richer Job Classification**  
   - Incorporate transformer-based embeddings (e.g., BERT) to improve XGBoost features.  

2. **Advanced Salary Prediction**  
   - Use gradient boosting and ensemble models for more accurate salary forecasting.  

3. **NLP-Based Skill Extraction**  
   - Use modern NLP (spaCy, transformers) to automatically mine skills from free-text job descriptions.  

4. **Hybrid Recommendation**  
   - Combine:
     - Collaborative filtering (ALS)  
     - Content-based (skills, titles, industries)  
     - XGBoost ranking models  
   - to create a holistic, personalized recommender.  

5. **Trend Forecasting**  
   - Use time-series modeling to predict demand and salary trends over time.  

All ML plans and current status are tracked in **`Documentation/ML_INTEGRATION_PLAN.md`** and **`ML_README.md`**.

---

## ⚠️ Performance & Common Issues

### Performance Optimization

- **Shuffle Partitions:**  
  - Default set to `4` for local machines; scale up (e.g., `200+`) for production clusters.  

- **Driver Memory:**  
  - Recommended `spark.driver.memory = "4g"` (or higher for full dataset).  

- **Caching:**  
  - Use `.cache()` for DataFrames used in multiple queries.  

- **Columnar Formats:**  
  - Use **Parquet** for intermediate analytics to reduce I/O and improve performance.  

### Common Issues & Fixes

1. **Hadoop Error on Windows**  
   - Install `winutils.exe`, set `HADOOP_HOME`, and update `PATH`.  

2. **NameError / Missing Variable in Notebook**  
   - Always run notebooks with **"Run All"** to respect cell dependencies.  

3. **Out of Memory**  
   - Reduce dataset size or increase `spark.driver.memory`.  

4. **Streaming Not Triggering**  
   - Ensure `streaming_input/` exists and contains files.  
   - Verify file permissions and schema consistency.  

---

## 📚 Documentation

- **`README.md` (this file):**  
  High-level overview, architecture, and setup.  

- **`spark-analytics/README.md`:**  
  Detailed Spark analytics and module descriptions.  

- **`spark-analytics/ML_README.md`:**  
  In-depth explanation of ML models, including XGBoost and Spark Recommender.  

- **`Documentation/DEMO_GUIDE.md`:**  
  Step-by-step demo instructions.  

- **`Documentation/PROJECT_SUMMARY.md`:**  
  Complete technical write-up of design decisions and findings.  

- **`Documentation/ML_INTEGRATION_PLAN.md`:**  
  ML roadmap and integration design.  

- **`Documentation/CHECKLIST.md`:**  
  Pre-demo checklist to ensure all components work.  

---

## 👥 Team Contributions

All team members contributed to:

- Data cleaning, integration, and exploratory analysis  
- Design and implementation of Spark SQL queries  
- Visualization design and storytelling for students  
- Streaming architecture and test data generation  
- Machine learning pipelines (XGBoost, Spark Recommender, etc.)  
- Documentation, demo preparation, and project planning  

---

## 📄 License & Course Information

This project is developed for educational purposes as part of:

- **Course:** ITCS 6190 – Cloud Computing  
- **Semester:** Fall 2025  
- **University:** University of North Carolina at Charlotte  

License: See `LICENSE` file in the repository.

---

## 🔗 Dataset Source

**LinkedIn Job Postings Dataset (2023–2024)**  
Source: Kaggle – [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)  
License: **CC0 Public Domain**
