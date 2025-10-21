# Spark Analytics - LinkedIn Job Market Analysis# Spark Analytics - LinkedIn Job Postings



Apache Spark-based analytics platform for processing and analyzing LinkedIn job posting data with complex queries, real-time streaming capabilities, and student-focused insights.Apache Spark-based analytics platform for processing and analyzing LinkedIn job posting data with real-time streaming capabilities and ML integration.



---## 🚀 Quick Start



## 🚀 Quick Start### 1. Install Dependencies

```powershell

### 1. Install Dependenciespip install pyspark pandas matplotlib seaborn numpy

```bash```

pip install -r requirements.txt

```### 2. Verify Setup

```powershell

**Required packages:**.\setup_demo.ps1

- pyspark>=3.5.0```

- pandas>=2.1.4

- matplotlib>=3.8.2### 3. Run Complex Queries

- seaborn>=0.13.0Open `complex_queries.ipynb` in VS Code or Jupyter and run all cells.

- numpy>=1.24.0

### 4. Run Streaming Demo

### 2. Run Complex Queries Analysis

**Terminal 1 - Start Streaming Processor:**

Open `complex_queries.ipynb` in VS Code or Jupyter and run all cells:```powershell

python streaming_processor.py

```bash```

# VS Code

code complex_queries.ipynb**Terminal 2 - Start Data Simulator:**

```powershell

# Or Jupyterpython streaming_data_simulator.py

jupyter notebook complex_queries.ipynb```

```

## 📁 File Structure

This will generate:

- 8 comprehensive visualizations- `simple_analytics.py` - Lightweight analytics without Spark dependencies

- Query results in CSV/Parquet format- `daily_analytics.py` - Full Spark-based analytics pipeline

- Student action plan text file- `requirements.txt` - Python dependencies for Spark version

- `analytics_output/` - Generated JSON analysis data

### 3. Run Streaming Demo- `reports/` - Generated Markdown reports



**Terminal 1 - Start Streaming Processor:**## 🔧 GitHub Actions Integration

```bash

python streaming_processor.pyThe pipeline is fully automated with GitHub Actions:

```

### Daily Scraping

**Terminal 2 - Start Data Simulator:**- **Schedule**: Daily at 6:30 AM UTC

```bash- **Workflow**: `.github/workflows/daily-scraping.yml`

python streaming_data_simulator.py- **Action**: Runs enhanced YC scraper and uploads data to Worker

```

### Weekly Analytics

The streaming demo will:- **Schedule**: Sundays at 8:00 AM UTC  

- Process job postings in real-time- **Workflow**: `.github/workflows/weekly-analytics.yml`

- Display top locations, companies, and experience levels- **Action**: Generates job market analysis reports

- Update console output continuously

## 📊 Output Files

---

### JSON Analysis Data

## 📁 File Structure```json

{

```  "analysis_date": "2025-10-05T21:18:06",

spark-analytics/  "total_jobs": 50,

├── complex_queries.ipynb       # Main analysis (8 visualizations)  "unique_companies": 10,

├── data_analysis.ipynb         # Exploratory data analysis  "top_companies": [["Stripe", 5], ["Airbnb", 5]],

├── streaming_processor.py      # Real-time Spark Structured Streaming  "remote_work": {

├── streaming_data_simulator.py # Simulates streaming data    "remote_jobs": 7,

├── main.py                     # Batch analytics script    "remote_percentage": 14.0

├── requirements.txt            # Python dependencies  },

├── analytics_output/           # Generated outputs  "salary_analysis": {

│   ├── visuals/               # PNG charts    "avg": 120000,

│   ├── query_results/         # CSV/Parquet results    "min": 80000,

│   └── STUDENT_ACTION_PLAN.txt # Career guidance    "max": 200000

└── reports/                    # Analysis reports  }

```}

```

---

### Markdown Reports

## 📊 Analytics Capabilities- Company hiring trends

- Location analysis

### Complex Queries (complex_queries.ipynb)- Skill demand tracking

- Salary insights

The notebook demonstrates 8 sophisticated Spark SQL analyses:- Job type breakdown



1. **Top Skills by Industry**### Summary Files

   - Window functions with `rank() OVER (PARTITION BY ...)`- `latest_summary.txt` - GitHub Actions compatible summary

   - Multi-table joins across 4 tables- Quick overview for workflow status

   - Shows top 10 skills for each industry

## 🛠️ Environment Setup

2. **Average Skills Required**

   - Aggregations: `AVG()`, `COUNT()`, `GROUP BY`### Requirements

   - Analyzes entry barriers across industries- Python 3.9+

   - Identifies beginner-friendly sectors- `requests` library (for simple analytics)

- Java 11+ and Spark (for full analytics)

3. **Cross-Industry Skills**

   - `DISTINCT` analysis with grouping### Environment Variables

   - Identifies transferable, versatile skills- `WORKER_ENDPOINT` - URL to Cloudflare Worker API

   - Shows which skills work across multiple industries

### Local Testing

4. **Skill Co-occurrence Network**```bash

   - Analyzes which skills appear together# Install dependencies

   - Uses `itertools.combinations` for pair analysispip install requests

   - Helps students learn complementary skills

# Test simple analytics

5. **Top 10 Most In-Demand Skills**python simple_analytics.py --days-back 3

   - Overall market demand ranking

   - Percentage of jobs requiring each skill# Check outputs

   - Priority learning list for job seekersls analytics_output/

ls reports/

6. **Industry Entry Barriers**```

   - Bubble chart: skill requirements vs opportunities

   - Color-coded by complexity level## 🔄 Pipeline Features

   - Helps choose target industry by skill level

### Data Analysis

7. **Skill Diversity Index**- **Company Trends**: Top hiring companies and job counts

   - Quadrant analysis: Specialist vs Generalist- **Location Analysis**: Geographic distribution and remote work statistics

   - Shows skill versatility across industries- **Skill Tracking**: Most in-demand technical skills

   - Risk assessment for skill investment- **Salary Insights**: Compensation ranges and averages

- **Job Types**: Full-time, contract, internship breakdown

8. **Career Path Builder**- **Experience Levels**: Entry to senior level demand

   - Foundation → Intermediate → Advanced progression

   - Based on co-requirement analysis### Automation

   - Creates personalized learning roadmap- **Daily Data Collection**: Automated scraping and storage

- **Weekly Reports**: Comprehensive market analysis

### Streaming Analytics (streaming_processor.py)- **Error Handling**: Graceful fallbacks and logging

- **Artifact Storage**: GitHub Actions artifact upload

Real-time job market monitoring using Spark Structured Streaming:

### Compatibility

- **3 Concurrent Queries**:- **GitHub Actions**: Optimized for CI/CD environments

  1. Top hiring locations- **Local Development**: Full Spark capabilities for advanced analysis

  2. Experience level distribution- **Cross-Platform**: Works on Windows, macOS, Linux

  3. Most active companies

## 📈 Sample Output

- **Processing**: File-based source (easily migrated to Kafka)

- **Output**: Console display + file output```

- **Mode**: Complete output mode with live updatesStarting YC Job Market Analysis

Analyzing last 7 days

---==================================================

Fetching jobs from Worker API...

## 🎓 Student Action PlanAPI connected - Total jobs in database: 108

Generated 50 sample job records for analysis

The analysis generates a personalized career guidance plan:

Analyzing 50 jobs from the last 7 days...

```Saved analysis data: analytics_output/yc_job_analysis_20251005_211806.json

STUDENT_ACTION_PLAN.txtSaved report: reports/yc_job_report_20251005_211806.md

Saved summary: analytics_output/latest_summary.txt

- Top 10 skills to learn (with job counts)

- Skill combinations to learn togetherAnalysis Complete!

- Entry-friendly industries (< 5 skills required)Total Jobs Analyzed: 50

- 90-day learning roadmapCompanies: 10

- Industry selection guideRemote Work: 14.0%

```Results saved to analytics_output/ and reports/

```

---

## 🐛 Troubleshooting

## 📈 Output Files

### Common Issues

### Visualizations (analytics_output/visuals/)

- `top_skills_by_industry.png` - Skill demand by sector1. **Unicode Encoding Errors**

- `avg_skills_by_industry.png` - Industry complexity   - Fixed: All file operations use `encoding='utf-8'`

- `cross_industry_skills.png` - Versatile skills   - ASCII-only output for terminal compatibility

- `skill_pairs.png` - Complementary skill combinations

- `top_10_skills_overall.png` - Overall market demand2. **Spark Dependencies**

- `industry_entry_barriers.png` - Complexity vs opportunity   - Solution: Use `simple_analytics.py` for GitHub Actions

- `skill_diversity_index.png` - Specialist vs generalist   - Use `daily_analytics.py` for local development with full Spark

- `career_path_builder.png` - Learning progression

3. **API Connection Issues**

### Query Results (analytics_output/query_results/)   - Fallback: Generates sample data for demonstration

- CSV files for quick viewing   - Check `WORKER_ENDPOINT` environment variable

- Parquet files for efficient Spark processing

- Includes all query outputs for further analysis### GitHub Actions Debugging

```yaml

---- name: Debug Output

  run: |

## 🛠️ Technical Details    ls -la analytics_output/ || echo "No analytics_output"

    find . -name "*.json" -o -name "*.md" | head -5

### Spark Configuration```



```python## 🚀 Future Enhancements

spark = SparkSession.builder \

    .appName("LinkedIn Job Analysis") \- Real-time API integration

    .config("spark.driver.memory", "4g") \- Advanced ML-based predictions

    .config("spark.sql.shuffle.partitions", "4") \- Interactive dashboard generation

    .getOrCreate()- Email/Slack notification integration

```- Historical trend analysis

- Competitive intelligence features

### Key Technologies

## 📋 Manual Workflow Trigger

- **Apache Spark 3.x**: Distributed data processing

- **Spark SQL**: Complex queries with window functionsTo manually trigger the weekly analytics:

- **Spark Structured Streaming**: Real-time analytics

- **PySpark**: Python API for Spark1. Go to GitHub Actions

- **Pandas**: Data conversion and analysis2. Select "Weekly YC Job Analytics"

- **Matplotlib/Seaborn**: Professional visualizations3. Click "Run workflow"

4. Set `days_back` parameter (default: 7)

### Data Processing5. Download artifacts to view reports



- **Joins**: Multi-table joins across skills, jobs, industries, companies---

- **Aggregations**: COUNT, AVG, SUM with GROUP BY

- **Window Functions**: RANK, DENSE_RANK, ROW_NUMBER with PARTITION BY## 📁 LinkedIn Job Analytics Project

- **Streaming**: File-based source with maxFilesPerTrigger=1

### Project Structure for Demo

---

```

## 🎯 Demo Instructionsspark-analytics/

├── complex_queries.ipynb          # 🔍 Spark SQL complex queries

For check-in presentations (7-8 minutes):├── data_analysis.ipynb            # 📊 Exploratory data analysis

├── streaming_processor.py         # ⚡ Real-time streaming app

1. **Complex Queries** (3 min): Open complex_queries.ipynb, show 3 original queries├── streaming_data_simulator.py    # 📤 Data ingestion simulator

2. **Visualizations** (2 min): Display 8 charts with student insights├── DEMO_GUIDE.md                  # 📖 Complete demo instructions

3. **Streaming** (2 min): Live demo with processor + simulator├── ML_INTEGRATION_PLAN.md         # 🤖 ML roadmap

4. **Q&A** (1 min): Discuss challenges and ML integration plans├── GITHUB_ISSUE_TEMPLATE.md       # 📝 Check-in template

├── setup_demo.ps1                 # ⚙️ Setup verification script

See `../Documentation/DEMO_GUIDE.md` for detailed presentation flow.├── analytics_output/              # 💾 Generated results

│   ├── query_results/             # CSV & Parquet files

---│   └── visuals/                   # Charts & graphs

├── streaming_input/               # 📥 Streaming data batches

## ⚠️ Common Issues & Solutions└── reports/                       # 📄 Analysis reports

```

### 1. Hadoop Error (Windows)

**Error**: `HADOOP_HOME and hadoop.home.dir are unset`### 🎯 Features



**Solution**:#### Complex Queries

1. Download `winutils.exe` from: https://github.com/steveloughran/winutils- **Query 1:** Top skills by industry with ranking (Window functions)

2. Place in `C:\hadoop\bin\`- **Query 2:** Average skills required per industry (Aggregations)

3. Set environment variable: `HADOOP_HOME=C:\hadoop`- **Query 3:** Cross-industry skill analysis (DISTINCT + GROUP BY)



### 2. NameError in Notebook#### Streaming Analytics

**Error**: `NameError: 'skills_by_industry' is not defined`- Real-time job posting processing

- Multiple concurrent streaming queries

**Solution**:- Location, experience, and company trend analysis

- Run all cells in order using "Run All"- ~50 records per batch, 5-second intervals

- Do not skip cells or run out of sequence

#### Visualizations

### 3. Out of Memory- Top skills by industry (bar charts)

**Error**: `Java heap space`- Average skill requirements (horizontal bars)

- Cross-industry skill distribution

**Solution**:

- Increase driver memory: `.config("spark.driver.memory", "8g")`### 📊 Key Outputs

- Reduce dataset size for testing

#### Query Results

### 4. Streaming Not Starting- `analytics_output/query_results/skills_by_industry.csv`

**Error**: Streaming query fails to start- `analytics_output/query_results/avg_skills_by_industry.csv`

- `analytics_output/query_results/cross_industry_skills.csv`

**Solution**:

- Ensure `streaming_input/` directory exists#### Visualizations

- Check that simulator is writing files- `analytics_output/visuals/top_skills_by_industry.png`

- Verify schema matches input data- `analytics_output/visuals/avg_skills_by_industry.png`

- `analytics_output/visuals/cross_industry_skills.png`

---

### 🔮 Next Steps: ML Integration

## 📚 Dataset Information

1. **Job-Skill Matching System:** TF-IDF + Cosine Similarity

**Source**: LinkedIn Job Postings Dataset (Kaggle)2. **Skill Demand Forecasting:** Facebook Prophet (Time Series)

- 40,000+ job postings3. **Cloud Deployment:** AWS EMR for distributed processing

- 91,000+ companies4. **Dashboard:** Real-time visualization with Plotly/Streamlit

- 1,000+ unique skills

- 147 industriesSee `ML_INTEGRATION_PLAN.md` for detailed roadmap.

- Global coverage

### 📖 Documentation

**Files Used**:

- `../data/postings_cleaned.csv` - Main job data- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete presentation guide with step-by-step instructions

- `../data/jobs/job_skills.csv` - Job-skill mappings- **[ML_INTEGRATION_PLAN.md](ML_INTEGRATION_PLAN.md)** - Machine Learning integration roadmap

- `../data/mappings/skills.csv` - Skill reference- **[GITHUB_ISSUE_TEMPLATE.md](GITHUB_ISSUE_TEMPLATE.md)** - Template for check-in updates

- `../data/jobs/job_industries.csv` - Job-industry mappings

- `../data/mappings/industries.csv` - Industry reference### 🛠️ Technologies



---- **Apache Spark** - Distributed data processing

- **PySpark** - Python API for Spark

## 🔮 Future Enhancements (Phase 3: ML)- **Spark Structured Streaming** - Real-time processing

- **Pandas** - Data manipulation

Planned machine learning integration:- **Matplotlib/Seaborn** - Visualization



1. **Job Classification**: MLlib Random Forest for role categorization### 🐛 Troubleshooting

2. **Salary Prediction**: Linear regression based on skills/location

3. **Skill Extraction**: NLP-based mining from descriptions**Issue:** OutOfMemory errors  

4. **Recommendation Engine**: Collaborative filtering for job matching**Fix:** Increase driver memory: `.config("spark.driver.memory", "4g")`

5. **Trend Forecasting**: Time-series analysis for market predictions

**Issue:** Streaming not updating  

See `../Documentation/ML_INTEGRATION_PLAN.md` for complete roadmap.**Fix:** Ensure `streaming_data_simulator.py` is running



---**Issue:** PySpark import errors  

**Fix:** `pip install pyspark` and restart Python kernel

## 📞 Support

**Issue:** File path errors  

For questions or issues:**Fix:** Use absolute paths or verify current working directory

- Check `../Documentation/PROJECT_SUMMARY.md` for complete project explanation

- Review `../Documentation/DEMO_GUIDE.md` for presentation tips### 🎬 Demo Checklist

- Contact team members (emails in main README.md)

- [ ] Run `setup_demo.ps1` to verify environment

---- [ ] Execute `complex_queries.ipynb` and save visualizations

- [ ] Test streaming demo (processor + simulator)

**Last Updated**: October 2025  - [ ] Take screenshots for GitHub Issue

**Team**: Unattached and Unhinged  - [ ] Review `DEMO_GUIDE.md` for presentation flow

**Course**: ITCS 6190 - Cloud Computing- [ ] Prepare 5-7 minute presentation

- [ ] Upload visuals to GitHub Issue

### 📝 For Check-In Presentation

**What to Demonstrate:**
1. Complex queries with Spark SQL (2-3 min)
2. Streaming setup with live demo (3-4 min)
3. Results and visualizations (1 min)
4. Challenges and ML roadmap (1 min)

**Materials Needed:**
- Screenshots of query results
- Live streaming demo or video recording
- Visualization charts
- GitHub Issue with all visuals uploaded

---

**Project Status:** ✅ Ready for Check-In Demo  
**Last Updated:** October 20, 2025