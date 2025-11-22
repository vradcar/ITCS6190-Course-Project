# MLlib Machine Learning Pipeline

This directory contains the machine learning components integrated with the YC Job Analytics pipeline using Apache Spark MLlib.

## 🎯 Overview

The ML pipeline includes three comprehensive machine learning features:

1. **Job Classification** - Random Forest classifier for categorizing jobs
2. **Skill Extraction** - NLP-based skill mining from job descriptions
3. **Recommendation System** - Collaborative Filtering (ALS) for job matching
   
## 📁 ML Module Structure

```
spark-analytics/
├── ml_job_classifier.py      # Random Forest job classification
├── ml_skill_extractor.py     # NLP skill extraction
├── ml_recommender.py         # Collaborative filtering recommendations
├── ml_pipeline.py           # Main integration pipeline
└── ML_README.md             # This file
```

## 🚀 Quick Start

### Run Complete ML Pipeline

```bash
cd spark-analytics

# Run all ML components on last 7 days of data
python ml_pipeline.py --days-back 7

# Run specific components
python ml_pipeline.py --components classification salary skills

# Analyze specific date
python ml_pipeline.py --date 2025-10-03

# Save results to disk
python ml_pipeline.py --days-back 7 --save
```

### Run Individual ML Components

```bash
# Job Classification
python ml_job_classifier.py

# Skill Extraction
python ml_skill_extractor.py

# Recommendation System
python ml_recommender.py

```

## 📊 ML Components Details

### 1. Job Classification (Random Forest)

**File:** `ml_job_classifier.py`

**Purpose:** Categorizes jobs into role categories (Software Engineer, Data Scientist, Product Manager, etc.)

**Algorithm:** Random Forest Classifier from MLlib

**Features:**
- Text analysis of job titles and descriptions
- Location and experience level encoding
- Automatic category assignment based on keywords
- Model accuracy evaluation

**Usage:**
```python
from ml_job_classifier import JobClassifier
from daily_analytics import YCJobAnalytics

analytics = YCJobAnalytics()
df = analytics.load_data_from_worker()
classifier = JobClassifier(analytics.spark)
model, predictions = classifier.train_classifier(df)
```

**Output Categories:**
- Software Engineer
- Data Scientist
- Product Manager
- Designer
- Marketing
- Sales
- Operations
- Other

### 2. Skill Extraction (NLP)

**File:** `ml_skill_extractor.py`

**Purpose:** Extracts and mines skills from job descriptions using NLP

**Techniques:**
- Pattern matching with comprehensive skill vocabulary
- TF-IDF feature extraction
- N-gram analysis (bigrams, trigrams)
- KMeans clustering for skill-based job grouping

**Usage:**
```python
from ml_skill_extractor import SkillExtractor

extractor = SkillExtractor(spark)

# Extract top skills
top_skills = extractor.extract_top_skills(df, top_n=20)

# Cluster jobs by skills
clustered_df, model, tfidf = extractor.cluster_jobs_by_skills(df, n_clusters=5)

# Analyze skill combinations
combinations = extractor.analyze_skill_combinations(df)
```

**Skill Categories:**
- Programming Languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Django, Spring, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Cloud & DevOps (AWS, Kubernetes, Docker, etc.)
- Specialized (Machine Learning, AI, Blockchain, etc.)

### 3. Recommendation System (Collaborative Filtering)

**File:** `ml_recommender.py`

**Purpose:** Recommends jobs to users based on collaborative filtering

**Algorithm:** Alternating Least Squares (ALS) from MLlib

**Features:**
- User-job interaction modeling
- Implicit feedback handling
- Cold start strategy
- Similar job discovery

**Usage:**
```python
from ml_recommender import JobRecommender

recommender = JobRecommender(spark)

# Train model
model, job_indexer, predictions = recommender.train_recommender(df, num_users=100)

# Get recommendations for user
recommendations = recommender.recommend_jobs_for_user(
    model, user_id=0, job_indexer=job_indexer, df=df, num_recommendations=10
)
```

**Note:** Currently uses synthetic user data. 

## 🔧 Integration with Existing Code

The ML components are designed to work **alongside** the existing `daily_analytics.py` without modifying it:

1. **Data Loading:** ML modules use the same `YCJobAnalytics` class for data loading
2. **Standalone Usage:** Each ML component can run independently
3. **Pipeline Integration:** `ml_pipeline.py` orchestrates all components

### Example: Using ML with Existing Analytics

```python
from daily_analytics import YCJobAnalytics
from ml_pipeline import MLPipeline

# Option 1: Run existing analytics
analytics = YCJobAnalytics()
df = analytics.load_data_from_worker()
analytics.analyze_daily_jobs(df, "2025-10-03")

# Option 2: Run ML pipeline on same data
ml = MLPipeline()
results = ml.run_full_pipeline(days_back=7)

# Option 3: Combine both
analytics.analyze_daily_jobs(df, "2025-10-03")
ml_results = ml.run_job_classification(df)
```

## 📈 Model Performance

### Typical Performance Metrics

**Job Classification:**
- Accuracy: 75-85% (depends on data quality)
- Categories: 8 job categories
- Training Time: ~2-5 minutes for 1000+ jobs

**Skill Extraction:**
- Vocabulary: 100+ known skills
- Extraction Rate: 5-15 skills per job
- Clustering: 5 skill-based clusters

**Recommendation System:**
- RMSE: 0.5-1.0 (on 1-5 rating scale)
- Users: Configurable (default: 100 synthetic users)
- Recommendations: Top 10 per user


## 🛠️ Requirements

All MLlib functionality is included with PySpark. No additional dependencies required:

```bash
pip install pyspark>=3.5.0
```

Java 8+ is required for Spark to run.

## 📝 Example Output

### Job Classification
```
🎯 Training Job Classifier (Random Forest)...
📊 Prepared 150 jobs for classification

📈 Category Distribution:
   • Software Engineer: 85 jobs
   • Data Scientist: 25 jobs
   • Product Manager: 20 jobs
   • Designer: 12 jobs
   • Other: 8 jobs

✅ Model Accuracy: 82.50%
```

### Skill Extraction
```
🛠️ Extracting top 20 skills from job descriptions...

📊 Top 20 Skills:
   1. Python              : 85 jobs (56.7%)
   2. JavaScript         : 72 jobs (48.0%)
   3. React              : 65 jobs (43.3%)
   4. AWS                : 58 jobs (38.7%)
   ...
```

### Recommendation System
```
🎯 Training Job Recommender (Collaborative Filtering - ALS)...
📚 Training on 450 interactions, testing on 112 interactions

✅ Model RMSE: 0.687

📊 Sample Recommendations:
   User 0, Job 23: Actual=4.0, Predicted=3.85
   ...
```

## 🔄 Pipeline Execution

The complete pipeline can be run with all components:

```bash
python ml_pipeline.py --days-back 7 --save
```

This will:
1. Load job data from the last 7 days
2. Run all 3 ML components sequentially
3. Display results and metrics
4. Save summary to `./ml_results/`

## 🎓 MLlib Components Used

- **Classification:** `RandomForestClassifier`
- **Clustering:** `KMeans`
- **Recommendation:** `ALS` (Alternating Least Squares)
- **Feature Engineering:** `Tokenizer`, `StopWordsRemover`, `CountVectorizer`, `HashingTF`, `IDF`, `NGram`, `StringIndexer`, `VectorAssembler`
- **Evaluation:** `MulticlassClassificationEvaluator`, `RegressionEvaluator`

## ⚠️ Notes

1. **Data Requirements:** ML models require sufficient data (typically 50+ jobs per component)
2. **Training Time:** Full pipeline takes 10-20 minutes depending on data volume
3. **Memory:** Ensure sufficient Spark driver/executor memory for large datasets
4. **Synthetic Data:** Recommendation system currently uses synthetic user data
5. **Model Persistence:** Models can be saved/loaded for production use (not shown in examples)

## 🚀 Next Steps

- Integrate with actual user interaction data for recommendations
- Add model persistence (save/load trained models)
- Implement hyperparameter tuning
- Add real-time prediction endpoints
- Create visualization dashboards for ML insights

