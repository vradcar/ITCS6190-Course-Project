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
│       ├── classification_class_distribution.png
│       ├── cross_industry_skills.png
│       ├── skill_cluster_sizes.png
│       └── top_skills_top_industry.png
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
### 0. One-Command Run (Recommended)

From the **repo root**, you can run the entire pipeline (environment setup, analytics, ML, and complex queries) with a single command:

```bash
chmod +x run.sh      # one-time
./run.sh
```

What `run.sh` does:

- Creates and activates a virtual environment under `spark-analytics/.venv`  
- Installs all dependencies from `spark-analytics/requirements.txt`  
- Generates streaming test data with `streaming_test_data_generator.py`  
- Runs batch analytics and ML pipeline scripts (e.g., `main.py`, `ml_pipeline.py`, `ml_job_classifier_xg.py`, `spark_recommender.py`)  
- Runs the complex analytics job to produce query CSVs and visualizations  
- Prints a summary of where outputs are stored, including:
  - Query results under `spark-analytics/analytics_output/query_results`  
  - Visuals under `spark-analytics/analytics_output/visuals`  
  - ML outputs and recommendations under `spark-analytics/ml_results` and `data/recommendations.csv`  

You can still run individual components manually (see below), but `run.sh` is the easiest way to **run everything** for grading or demos.

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
# - Student action plan
```

### 4. Run Streaming Demo

Terminal 1 (Streaming Processor):
```bash
cd spark-analytics
python streaming_processor.py
```

Terminal 2 (Data Simulator):
```bash
cd spark-analytics
python streaming_data_simulator.py
```

This demonstrates a **streaming-style pipeline** over file-based job posting batches, rather than a strict low-latency real-time system.

---

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

### Visualizations (5 Total)

1. **Top Skills in Focus Industry** (`top_skills_top_industry.png`)
   - Horizontal bar chart of the top 10 skills in the highest–skill-demand industry (e.g., Newspaper Publishing).
   - Helps students see which skills dominate a particular sector.

2. **Average Skills Required by Industry (Top 15)** (`avg_skills_by_industry.png`)
   - Shows average number of skills required per job across the top 15 industries.
   - Interpreted as **entry barriers**: fewer required skills → easier to enter.

3. **Most Versatile Skills (Top 20)** (`cross_industry_skills.png`)
   - Ranks skills by the number of industries they appear in.
   - Highlights “safe bet” skills that transfer across many sectors (e.g., Management, IT, Sales).

4. **Skill Cluster Sizes** (`skill_cluster_sizes.png`)
   - Visualizes how many skills fall into each cluster (from the ML-based clustering step).
   - Gives a sense of which skill groups are broad vs. highly specialized.

5. **Classification Predictions Distribution** (`classification_class_distribution.png`)
   - Shows the distribution of predicted classes from the job classifier.
   - Useful for spotting class imbalance and understanding how the model is behaving across job categories.

   Under the hood, we compared two classification models:
   - A **Spark ML Random Forest** (primary model used in the pipeline)  
   - An **XGBoost classifier** as a reference model  

   XGBoost achieved accuracy within **<1% of the Random Forest model**, but was slightly lower, so we kept Random Forest as the primary production model and used XGBoost as a benchmark for robustness.

### Streaming Analytics

- **Technology**: Spark Structured Streaming  
- **Source**: File-based (easily migrated to Kafka or other streaming sources)  
- **Processing**: 3 streaming queries executed over sequential micro-batches:  
  - Top hiring locations  
  - Experience level distribution  
  - Most active companies  
- **Output**: Console + file output in append mode  

This is a **streaming-style, batch-fed pipeline** using files, not a hard real-time system with strict latency guarantees.

---

## 🎓 Key Research Questions Answered

1. **What skills should students learn first?**  
   - Answer: Top 10 visualization + skill pairs analysis  

2. **Which industries are beginner-friendly?**  
   - Answer: Entry barriers bubble chart (< 5 skills required)  

3. **Are skills specialized or generalist?**  
   - Answer: Skill diversity quadrant analysis  

4. **What's the learning progression?**  
   - Answer: Career path builder with foundation/intermediate/advanced  

5. **What skills appear together?**  
   - Answer: Skill co-occurrence pairs (learn bundles efficiently)  

---

## 📈 Exploratory Data Analysis (EDA)

### Dataset Statistics

- **Total Job Postings**: 40,000+ records  
- **Companies**: 91,026 company records  
- **Industries**: 147 unique industries  
- **Skills**: 1,000+ unique skills tracked  
- **Geographic Coverage**: Global job market data  

### Key Findings

1. **Industry Dominance**: Technology, Finance, and Healthcare account for 60%+ of postings  
2. **Company Size Correlation**: Larger companies post 3x more jobs on average  
3. **Skill Bundling**: Top 20 skill pairs identified for efficient learning  
4. **Entry Barriers**: 30% of industries require < 5 skills, marking them as beginner-friendly  
5. **Versatile Skills**: SQL, Python, and Communication appear in 80+ industries  

### Analysis Notebooks

- `data_analysis.ipynb`: Pandas-based EDA with frequency plots, heatmaps, and distributions  
- `complex_queries.ipynb`: Spark SQL-based analysis with advanced aggregations  

All visualizations saved to: `analytics_output/visuals/`

---

## 🛠️ Technical Implementation

### Spark Configuration

```python
spark = SparkSession.builder \
    .appName("LinkedIn Job Analysis") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()
```

### Complex Query Example

```python
# Top 10 skills per industry with ranking
skills_by_industry = job_skills \
    .join(skill_map, "skill_abr") \
    .join(job_industries, "job_id") \
    .join(industry_map, "industry_id") \
    .groupBy("industry_name", "skill_name") \
    .agg(count("*").alias("skill_count")) \
    .withColumn("rank", rank().over(
        Window.partitionBy("industry_name")
              .orderBy(desc("skill_count"))
    )) \
    .filter(col("rank") <= 10)
```

### Streaming Setup

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
```

---

## 🎯 Check-In Demo Requirements

This project fully satisfies all check-in requirements:

✅ **Complex Queries**: 8 sophisticated Spark SQL queries with window functions, joins, aggregations  
✅ **Streaming Setup**: Streaming pipeline with Spark Structured Streaming (processor + simulator)  
✅ **Demo Results**: All visualizations + console output ready to show  
✅ **Technical Challenges**: Documented (Hadoop on Windows, cell execution order, data/schema alignment)  
✅ **ML Integration Plan**: Detailed roadmap in `Documentation/ML_INTEGRATION_PLAN.md`  

### Demo Flow (~30 minutes)

1. **Show Complex Queries** (3 min): Open `complex_queries.ipynb`, demonstrate 3 original queries  
2. **Show Visualizations** (2 min): Display 5 charts with student insights  
3. **Run Streaming Demo** (2 min): Demo of streaming processor + simulator on file-based batches  
4. **Q&A** (1 min): Discuss challenges and next steps  

---

## 📋 Future Enhancements (Phase 3: ML)

### Planned Machine Learning Integration

1. **Job Classification**: MLlib Random Forest for categorizing roles (with XGBoost as a comparative baseline)  
2. **Salary Prediction**: Linear regression based on skills, experience, location  
3. **Skill Extraction**: NLP-based skill mining from job descriptions  
4. **Recommendation System**: Collaborative filtering for job matching  
5. **Trend Forecasting**: Time-series analysis for market predictions  

See: `Documentation/ML_INTEGRATION_PLAN.md` for complete roadmap

---

## ⚠️ Important Notes

### Performance Optimization

- **Shuffle Partitions**: Set to 4 for local development (adjust for cluster: 200+)  
- **Driver Memory**: 4GB recommended for full dataset processing  
- **Data Caching**: Use `.cache()` for DataFrames used multiple times  
- **File Formats**: Parquet preferred over CSV for analytics output  

### Common Issues & Solutions

1. **Hadoop Error (Windows)**:  
   - Solution: Install `winutils.exe` and set `HADOOP_HOME`  

2. **NameError in Notebook**:  
   - Solution: Run all cells in order (use "Run All")  

3. **Out of Memory**:  
   - Solution: Increase `spark.driver.memory` or reduce dataset size  

4. **Streaming Not Starting**:  
   - Solution: Ensure `streaming_input/` directory exists  

---

## 📚 Documentation

- **README.md** (this file): Project overview and setup  
- **spark-analytics/README.md**: Detailed analytics documentation  
- **Documentation/DEMO_GUIDE.md**: Presentation instructions  
- **Documentation/PROJECT_SUMMARY.md**: Complete technical explanation  
- **Documentation/ML_INTEGRATION_PLAN.md**: Future ML roadmap  
- **Documentation/CHECKLIST.md**: Demo day checklist  

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

