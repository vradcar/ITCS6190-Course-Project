# The Job Intelligence Engine 
## LinkedIn Job Market Analytics with Apache Spark

**Group Name: Unattached and Unhinged**

**Team Members:**
- Varad Paradkar (801418318) - vparadka@charlotte.edu
- Mitali Yadav (801453849) - myadav5@charlotte.edu  
- Sudeepta Bal (801455628) - sbal1@charlotte.edu
- Ruthwik Dovala (801431661) - rdovala@charlotte.edu

---

## 🎯 Project Overview

This project implements a comprehensive **Apache Spark-based analytics platform** for analyzing the LinkedIn job market dataset from Kaggle. The system performs complex queries, streaming-style analytics, and provides actionable insights for students and job seekers entering the market.

### Key Features

- **Complex Spark SQL Queries**: Window functions, multi-table joins, and advanced aggregations  
- **Streaming**: Spark Structured Streaming for processing simulated job market data in micro-batches  
- **Professional Visualizations**: 5 comprehensive charts showing market trends and opportunities  
- **Scalable Architecture**: Distributed processing with Apache Spark for large-scale data analysis  

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
│              Apache Spark Processing                    │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Spark SQL       │      │  Spark Streaming │        │
│  │  Complex Queries │      │  Streaming Data  │        │
│  └──────────────────┘      └──────────────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Analytics & Visualizations                 │
│  • Skill Demand Analysis    • Industry Entry Barriers   │
│  • Salary Trends            • Career Path Builder       │
│  • Skill Co-occurrence      • Learning Roadmaps         │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
.
├── Documentation
│   ├── The Job Intelligence Engine(Final Presentation).pdf
│   ├── Unattached and Unhinged_project proposal.pdf
│   └── Unattached and Unhinged_project_2nd check in.pdf
├── LICENSE
├── Project Demo and Technical aspects video
│   └── Video of the Demo and technical explanations of our project.pdf
├── README.md
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
│   └── users.csv
├── run.sh
└── spark-analytics
    ├── README.md
    ├── analytics_output
    │   ├── Spark_recommendation_results
    │   │   └── recommendations.csv
    │   ├── ml_outputs
    │   │   ├── classification_predictions.csv
    │   │   ├── job_recommendations.csv
    │   │   └── skill_clusters.csv
    │   ├── query_results
    │   │   ├── avg_skills_by_industry.csv
    │   │   ├── cross_industry_skills.csv
    │   │   └── skills_by_industry.csv
    │   └── visuals
    │       ├── avg_skills_by_industry.png
    │       ├── classification_class_distribution.png
    │       ├── cross_industry_skills.png
    │       ├── recommendation_score_hist.png
    │       ├── recs_top_users_unique_jobs.png
    │       ├── skill_cluster_heatmap.png
    │       ├── skill_cluster_sizes.png
    │       ├── stream_experience_levels.png
    │       ├── stream_top_titles.png
    │       └── top_skills_top_industry.png
    ├── complex_queries_job.py
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
    │   ├── test_batch_0000.csv
    │   ├── test_batch_0001.csv
    │   ├── test_batch_0002.csv
    │   ├── test_batch_0003.csv
    │   ├── test_batch_0004.csv
    │   ├── test_batch_0005.csv
    │   ├── test_batch_0006.csv
    │   ├── test_batch_0007.csv
    │   ├── test_batch_0008.csv
    │   └── test_batch_0009.csv
    └── streaming_test_data_generator.py
```

---

## 🚀 Quick Start Guide
### 0. One-Command Run (Recommended)

From the **repo root**, you can run the entire pipeline (environment setup, analytics, ML, and complex queries) with a single command:

```bash
chmod +x run.sh      # one-time
./run.sh
```

What `run.sh` does:

- Creates and activates a virtual environment under `spark-analytics/.venv`  
- Installs all dependencies from `spark-analytics/requirements.txt`  
- Generates streaming-style test data with `streaming_test_data_generator.py`  
- Runs the main ML pipeline via `ml_pipeline.py --save`  
- Runs the XGBoost classifier (`ml_job_classifier_xg.py`) as a comparative model  
- Runs the Spark-based recommender system (`spark_recommender.py`)  
- Runs the complex analytics + visualization job (`complex_queries_job.py`) to produce query CSVs and charts  
- Prints a summary of where all artifacts are saved, including:  
  - ML summary & models: `spark-analytics/ml_results`  
  - ML detailed outputs: `spark-analytics/analytics_output/ml_outputs`  
  - Spark recommendation outputs: `spark-analytics/analytics_output/Spark_recommendation_results`  
  - Query results: `spark-analytics/analytics_output/query_results`  
  - Visualizations: `spark-analytics/analytics_output/visuals`  

You can still run individual components manually (e.g., specific notebooks or scripts), but `run.sh` is the easiest way to **run everything end-to-end** for grading or demos.


---
### Prerequisites

- Python 3.8+  
- Apache Spark 3.x (or PySpark installed via pip)  
- 4GB+ RAM recommended  
- Windows users: Install Hadoop binaries (`winutils.exe`)  

### 1. Install Dependencies

```bash
cd spark-analytics
pip install -r requirements.txt
```

**Required packages:**
- pyspark  
- pandas  
- matplotlib  
- seaborn  
- numpy  

### 2. Set Up Hadoop (Windows Only)

If you're on Windows and encounter Hadoop errors:

1. Download `winutils.exe` from: https://github.com/steveloughran/winutils  
2. Place it in `C:\hadoop\bin\`  
3. Set environment variable: `HADOOP_HOME=C:\hadoop`  

### 3. Run Complex Queries Analysis

```bash
# Open the notebook in VS Code or Jupyter
cd spark-analytics
code complex_queries.ipynb  # or jupyter notebook

# Run all cells to generate:
# - 5 visualizations
# - Query results (CSV/Parquet)
```

### 4.  Streaming-Style Demo

The end-to-end run via `./run.sh` already generates streaming-style batches and runs the Spark jobs.  
If you want to **only regenerate the streaming input data** used by the pipeline, run:

```bash
cd spark-analytics
python streaming_test_data_generator.py
```

This script writes multiple CSV batches into the `streaming_input/` directory, simulating a feed of incoming job postings.  
These batches are then consumed by the Spark jobs as a **streaming-style, file-based pipeline**, rather than a strict low-latency real-time system.


## 📊 Analytics Capabilities

### Complex Queries (Spark SQL)

The project demonstrates advanced Spark SQL capabilities:

1. **Top Skills by Industry**  
   - Window functions: `rank() OVER (PARTITION BY industry ORDER BY count DESC)`  
   - Multi-table joins: job_skills → skills → job_industries → industries  
   - Result: Top 10 skills for each industry  

2. **Average Skills Required**  
   - Aggregations: `AVG()`, `COUNT()`, `GROUP BY`  
   - Analyzes skill complexity across industries  
   - Result: Entry barriers for different sectors  

3. **Cross-Industry Skill Overlap**  
   - `DISTINCT` analysis with grouping  
   - Identifies transferable skills  
   - Result: Skills valuable across multiple sectors  

## Visualizations (10 Total)


Our pipeline produces a rich set of visual outputs across streaming analytics, core Spark SQL analytics, clustering, classification, and recommendations.

#### A. Streaming-Style Analytics

1. **Top Job Titles in Latest Stream Batch** (`stream_top_titles.png`)  
   - Horizontal bar chart of the most common job titles in the most recent micro-batch.  
   - Shows which roles (e.g., DevOps Engineer, UX Designer, Cloud Architect) are currently dominating the incoming stream.

2. **Experience Levels in Latest Stream Batch** (`stream_experience_levels.png`)  
   - Bar chart of experience levels (Entry, Mid, Senior, Director, Internship) in the latest batch.  
   - Helps students see how “senior” the current market is skewing in near-real-time.

#### B. Core Spark SQL Analytics

3. **Top Skills in Focus Industry** (`top_skills_top_industry.png`)  
   - Top 10 skills for the highest–skill-demand industry (e.g., Newspaper Publishing).  
   - Concrete list of what you need to break into that specific sector.

4. **Average Skills Required by Industry (Top 15)** (`avg_skills_by_industry.png`)  
   - Average number of skills required per job across the top 15 industries.  
   - Interpreted as **entry barriers**: fewer skills → easier entry for students.

5. **Most Versatile Skills (Top 20)** (`cross_industry_skills.png`)  
   - Ranks skills by how many industries they appear in.  
   - Highlights “safe bet” skills like Management or IT that transfer across many sectors.

#### C. Clustering & Skill Landscape

6. **Skill Cluster Sizes (Top)** (`skill_cluster_sizes.png`)  
   - Shows how many skills fall into each cluster discovered by the ML pipeline.  
   - Indicates which clusters are broad (lots of skills) vs. tightly specialized.

7. **Skill Frequency by Cluster (Heatmap)** (`skill_cluster_heatmap.png`)  
   - Heatmap of key skills (Python, SQL, AWS, Spark, etc.) vs. clusters.  
   - Darker cells indicate skills that define or dominate specific clusters.

#### D. Classification & Recommendation Insights

8. **Classification Predictions Distribution** (`classification_class_distribution.png`)  
   - Histogram of predicted job classes from the classifier.  
   - Used to inspect class imbalance and sanity-check the model’s behavior.

9. **Top Users by Unique Jobs Recommended** (`recs_top_users_unique_jobs.png`)  
   - Bar plot of users vs. number of unique jobs recommended.  
   - Shows which users receive the most diverse recommendation set.

10. **Recommendation Score Histogram** (`recommendation_score_hist.png`)  
    - Histogram of recommendation scores from the collaborative filtering model.  
    - Reveals the score distribution and helps pick sensible thresholds for “strong” vs. “weak” recommendations.


## Streaming Analytics

- **Technology**: Spark Structured Streaming  
- **Source**: File-based (easily migrated to Kafka or other streaming sources)  
- **Processing**: 3 streaming queries executed over sequential micro-batches:  
  - Top hiring locations  
  - Experience level distribution  
  - Most active companies  
- **Output**: Console + file output in append mode  

This is a **streaming-style, batch-fed pipeline** using files, not a hard real-time system with strict latency guarantees.

---

## 🎓 Key Research Questions

Our Job Intelligence Engine is designed around a set of student- and job-seeker-focused research questions:

1. **Which job titles are currently most in demand?**  
   - Answered by streaming visualizations of top job titles in the latest micro-batch.

2. **How is demand distributed across experience levels?**  
   - Entry vs. Mid vs. Senior vs. Director vs. Internship, from the streaming experience-level chart.

3. **Which skills matter most in each industry?**  
   - Answered by the “Top Skills in Focus Industry” and industry-specific skill ranking queries.

4. **Which industries have low entry barriers for students?**  
   - Derived from “Average Skills Required by Industry” — industries needing fewer skills are more beginner-friendly.

5. **Which skills are the most versatile across the job market?**  
   - Answered by the “Most Versatile Skills (Top 20)” visualization based on cross-industry skill overlap.

6. **How do technical skills naturally cluster together?**  
   - Investigated via skill clusters and the “Skill Frequency by Cluster” heatmap.

7. **Is our job classifier well-balanced across classes?**  
   - Checked using the “Classification Predictions Distribution” plot.

8. **Are job recommendations diverse and fair across users?**  
   - Studied using “Top Users by Unique Jobs Recommended” and the recommendation score histogram.

9. **What recommendation score ranges correspond to strong vs. weak matches?**  
   - Inferred from the shape of the recommendation score histogram.

Together, these questions guide how we turn raw LinkedIn job postings into **actionable career intelligence** for students and early-career professionals.


---

## 📈 Exploratory Data Analysis (EDA)

## 📈 Dataset Statistics (from `data_analysis.ipynb`)

- **Total Job Postings (raw `postings.csv`)**: 123,849 records  
- **Job–Industry Links (`job_industries.csv`)**: 164,808 records  
- **Job–Skill Links (`job_skills.csv`)**: 213,768 records  
- **Industries (`mappings/industries.csv`)**: 422 unique industries  
- **Skills (`mappings/skills.csv`)**: 35 aggregated skill categories  
- **Geographic Coverage**: Global job market data (multiple countries and cities in the `location` column)

---

## 🔍 Key Findings (from EDA)

- **Industry Dominance**: A small set of industries (e.g., Technology and related sectors) account for a large share of postings.  
- **Company Size & Activity**: Some companies appear frequently across the postings, indicating higher hiring activity and market presence.  
- **Skill Bundling**: Many jobs list multiple required skills, and repeated co-occurrence patterns suggest natural “skill bundles” for students to learn together.  
- **Entry Barriers**: Certain industries tend to have lower average skill counts per job, making them more beginner-friendly than highly specialized sectors.  
- **Versatile Skills**: General-purpose skills like programming, data, and business/communication recur across many industries, making them strong “core” investments.

---

## 📓 Analysis Components

- **`data_analysis.ipynb`**  
  Pandas-based exploratory data analysis with:
  - Loading core CSVs from the `data/` folder  
  - Basic profiling of tables (`head()`, `.info()`, `.describe()`)  
  - Frequency plots / bar charts for industries, companies, and skills  
  - Cleaning the raw postings data and exporting a slimmer
    `postings_cleaned.csv` used by all Spark jobs

- **`complex_queries_job.py`**  
  Production Spark script (used instead of a notebook) that:
  - Initializes a Spark session and resolves paths to the `data/` and
    `analytics_output/` directories  
  - Loads `postings_cleaned.csv`, `jobs/job_skills.csv`,
    `jobs/job_industries.csv`, and the `mappings/skills.csv` and
    `mappings/industries.csv` lookup tables  
  - Runs three main Spark SQL aggregations:
    - Top skills per industry with window functions for ranking  
    - Average number of skills per job by industry (entry-barrier signal)  
    - Cross-industry skill overlap (how many industries use each skill)  
  - Writes the aggregated tables as CSVs under
    `spark-analytics/analytics_output/query_results/` for downstream use in
    visualizations and reporting :contentReference[oaicite:0]{index=0}


## 🛠️ Technical Implementation

### Spark Configuration

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("LinkedIn Job Complex Analytics")
    .config("spark.driver.memory", "4g")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
```

### Core Complex Queries (Spark SQL)

Below is a representative example of how we implement the main analytics in `complex_queries_job.py`.

#### 1️⃣ Top 10 Skills per Industry (with Ranking)

This query ranks skills within each industry using window functions and broadcast joins for efficiency.

```python
from pyspark.sql.functions import col, count, desc, rank, broadcast
from pyspark.sql.window import Window

# Clean industry mapping (drop nulls)
industry_map_clean = industry_map.dropna()

# Top 10 skills per industry with ranking
skills_by_industry = (
    job_skills
    .join(broadcast(skill_map), "skill_abr")
    .join(job_industries, "job_id")
    .join(broadcast(industry_map_clean), "industry_id")
    .groupBy("industry_name", "skill_name")
    .agg(count("*").alias("skill_count"))
    .withColumn(
        "rank",
        rank().over(
            Window.partitionBy("industry_name")
                  .orderBy(desc("skill_count"))
        )
    )
    .filter(col("rank") <= 10)
    .orderBy("industry_name", "rank")
)
```

#### 2️⃣ Average Skills Required per Job by Industry

We compute the average number of skills required per job, grouped by industry, which we later interpret as an **entry barrier** signal.

```python
from pyspark.sql.functions import avg

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
```

#### 3️⃣ Cross-Industry Skill Overlap

This query measures how many different industries use each skill, which we use to identify **versatile, high-transferability** skills.

```python
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
```


## 🎯 Spark Functionality & Design Approach

Our Job Intelligence Engine showcases several core Spark capabilities:

- **Unified Batch + Streaming-Style Processing**  
  We use Spark to handle both historical batch data (from Kaggle) and streaming-style micro-batches generated into `streaming_input/`, giving a realistic pipeline that can be later migrated to Kafka or other real-time sources.

- **Spark SQL for Rich Analytics**  
  Complex Spark SQL queries power our core insights:
  - Window functions to rank top skills by industry  
  - Multi-table joins across jobs, skills, companies, and industries  
  - Aggregations for entry barriers, cross-industry skill overlap, and demand patterns  

- **ML & Recommendations on Spark Data**  
  Cleaned and aggregated Spark outputs feed into our ML pipeline:
  - Random Forest and XGBoost classifiers for job category prediction  
  - A Spark-based recommender system that suggests jobs to users and logs scores for analysis  

### Design Approach

- **Student-Centric Insight First**: Every query and visualization was designed to answer concrete questions a student or early-career job seeker might ask (Which skills? Which industries? Which roles?).
- **Script-First, Reproducible Pipeline**: Instead of relying only on notebooks, we implemented `run.sh`, `ml_pipeline.py`, and `complex_queries_job.py` so the entire system can be run end-to-end with a single command for grading, demos, or future extensions.
- **Modular Architecture**: The project is structured into clear layers—data preparation (`data_analysis.ipynb`), Spark analytics (`complex_queries_job.py`), ML (`ml_pipeline.py`, XGBoost classifier), and recommendations—making it easy to swap components or scale parts independently.


## 📋 Future Enhancements

A key next step is to build a **user-friendly interface** (web or desktop) on top of this Spark + ML pipeline, so students and job seekers can interactively:

- Explore job market insights and visualizations  
- Get personalized recommendations and skill roadmaps  

All without needing to run any code or understand the underlying infrastructure.

## ⚠️ Important Notes

### Performance Optimization

- **Shuffle Partitions**: Set to 4 for local development (adjust for cluster: 200+)  
- **Driver Memory**: 4GB recommended for full dataset processing  
- **Data Caching**: Use `.cache()` for DataFrames used multiple times  
- **File Formats**: Parquet preferred over CSV for analytics output  

### Common Issues & Solutions

1. **Missing Dependencies / Import Errors**  
   - Make sure **all** Python packages listed in `spark-analytics/requirements.txt` are installed in your active environment.  
   - Easiest option: run `./run.sh`, which automatically creates a virtual environment and installs everything from `requirements.txt`.

2. **NameError in Notebook**  
   - Solution: Run all cells in order (use “Run All” in Jupyter/VS Code) to ensure every variable and function is defined before plots or queries.

3. **Out of Memory (OOM)**  
   - Solution:  
     - Increase `spark.driver.memory` in the Spark configuration, or  
     - Work with a sampled subset of the data (as done in `complex_queries_job.py`), or  
     - Close other heavy applications while running the pipeline.

4. **Streaming-Style Pipeline Not Producing Data**  
   - Solution:  
     - Ensure the `streaming_input/` directory exists under `spark-analytics/`.  
     - Re-run the generator script:
       ```bash
       cd spark-analytics
       python streaming_test_data_generator.py
       ```
---

## 📚 Documentation

- **README.md** (this file): Project overview and setup  
- **spark-analytics/README.md**: Detailed analytics documentation 

---

## 👥 Team Contributions

All team members contributed equally to:
- Data analysis and query design  
- Visualization development  
- Streaming architecture  
- Documentation and presentation preparation  

---

## 📄 License

This project is for educational purposes as part of ITCS 6190 - Cloud Computing.

**Course**: ITCS 6190 - Cloud Computing  
**Semester**: Fall 2025  
**University**: University of North Carolina at Charlotte  

---

## 🔗 Dataset Source

**LinkedIn Job Postings Dataset** (2023-2024)  
Source: Kaggle - [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)  
License: CC0 Public Domain  

---

