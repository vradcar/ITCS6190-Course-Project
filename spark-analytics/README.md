# Spark Analytics - LinkedIn Job Postings

Apache Spark-based analytics platform for processing and analyzing LinkedIn job posting data with real-time streaming capabilities and ML integration.

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install pyspark pandas matplotlib seaborn numpy
```

### 2. Verify Setup
```powershell
.\setup_demo.ps1
```

### 3. Run Complex Queries
Open `complex_queries.ipynb` in VS Code or Jupyter and run all cells.

### 4. Run Streaming Demo

**Terminal 1 - Start Streaming Processor:**
```powershell
python streaming_processor.py
```

**Terminal 2 - Start Data Simulator:**
```powershell
python streaming_data_simulator.py
```

## 📁 File Structure

- `simple_analytics.py` - Lightweight analytics without Spark dependencies
- `daily_analytics.py` - Full Spark-based analytics pipeline
- `requirements.txt` - Python dependencies for Spark version
- `analytics_output/` - Generated JSON analysis data
- `reports/` - Generated Markdown reports

## 🔧 GitHub Actions Integration

The pipeline is fully automated with GitHub Actions:

### Daily Scraping
- **Schedule**: Daily at 6:30 AM UTC
- **Workflow**: `.github/workflows/daily-scraping.yml`
- **Action**: Runs enhanced YC scraper and uploads data to Worker

### Weekly Analytics
- **Schedule**: Sundays at 8:00 AM UTC  
- **Workflow**: `.github/workflows/weekly-analytics.yml`
- **Action**: Generates job market analysis reports

## 📊 Output Files

### JSON Analysis Data
```json
{
  "analysis_date": "2025-10-05T21:18:06",
  "total_jobs": 50,
  "unique_companies": 10,
  "top_companies": [["Stripe", 5], ["Airbnb", 5]],
  "remote_work": {
    "remote_jobs": 7,
    "remote_percentage": 14.0
  },
  "salary_analysis": {
    "avg": 120000,
    "min": 80000,
    "max": 200000
  }
}
```

### Markdown Reports
- Company hiring trends
- Location analysis
- Skill demand tracking
- Salary insights
- Job type breakdown

### Summary Files
- `latest_summary.txt` - GitHub Actions compatible summary
- Quick overview for workflow status

## 🛠️ Environment Setup

### Requirements
- Python 3.9+
- `requests` library (for simple analytics)
- Java 11+ and Spark (for full analytics)

### Environment Variables
- `WORKER_ENDPOINT` - URL to Cloudflare Worker API

### Local Testing
```bash
# Install dependencies
pip install requests

# Test simple analytics
python simple_analytics.py --days-back 3

# Check outputs
ls analytics_output/
ls reports/
```

## 🔄 Pipeline Features

### Data Analysis
- **Company Trends**: Top hiring companies and job counts
- **Location Analysis**: Geographic distribution and remote work statistics
- **Skill Tracking**: Most in-demand technical skills
- **Salary Insights**: Compensation ranges and averages
- **Job Types**: Full-time, contract, internship breakdown
- **Experience Levels**: Entry to senior level demand

### Automation
- **Daily Data Collection**: Automated scraping and storage
- **Weekly Reports**: Comprehensive market analysis
- **Error Handling**: Graceful fallbacks and logging
- **Artifact Storage**: GitHub Actions artifact upload

### Compatibility
- **GitHub Actions**: Optimized for CI/CD environments
- **Local Development**: Full Spark capabilities for advanced analysis
- **Cross-Platform**: Works on Windows, macOS, Linux

## 📈 Sample Output

```
Starting YC Job Market Analysis
Analyzing last 7 days
==================================================
Fetching jobs from Worker API...
API connected - Total jobs in database: 108
Generated 50 sample job records for analysis

Analyzing 50 jobs from the last 7 days...
Saved analysis data: analytics_output/yc_job_analysis_20251005_211806.json
Saved report: reports/yc_job_report_20251005_211806.md
Saved summary: analytics_output/latest_summary.txt

Analysis Complete!
Total Jobs Analyzed: 50
Companies: 10
Remote Work: 14.0%
Results saved to analytics_output/ and reports/
```

## 🐛 Troubleshooting

### Common Issues

1. **Unicode Encoding Errors**
   - Fixed: All file operations use `encoding='utf-8'`
   - ASCII-only output for terminal compatibility

2. **Spark Dependencies**
   - Solution: Use `simple_analytics.py` for GitHub Actions
   - Use `daily_analytics.py` for local development with full Spark

3. **API Connection Issues**
   - Fallback: Generates sample data for demonstration
   - Check `WORKER_ENDPOINT` environment variable

### GitHub Actions Debugging
```yaml
- name: Debug Output
  run: |
    ls -la analytics_output/ || echo "No analytics_output"
    find . -name "*.json" -o -name "*.md" | head -5
```

## 🚀 Future Enhancements

- Real-time API integration
- Advanced ML-based predictions
- Interactive dashboard generation
- Email/Slack notification integration
- Historical trend analysis
- Competitive intelligence features

## 📋 Manual Workflow Trigger

To manually trigger the weekly analytics:

1. Go to GitHub Actions
2. Select "Weekly YC Job Analytics"
3. Click "Run workflow"
4. Set `days_back` parameter (default: 7)
5. Download artifacts to view reports

---

## 📁 LinkedIn Job Analytics Project

### Project Structure for Demo

```
spark-analytics/
├── complex_queries.ipynb          # 🔍 Spark SQL complex queries
├── data_analysis.ipynb            # 📊 Exploratory data analysis
├── streaming_processor.py         # ⚡ Real-time streaming app
├── streaming_data_simulator.py    # 📤 Data ingestion simulator
├── DEMO_GUIDE.md                  # 📖 Complete demo instructions
├── ML_INTEGRATION_PLAN.md         # 🤖 ML roadmap
├── GITHUB_ISSUE_TEMPLATE.md       # 📝 Check-in template
├── setup_demo.ps1                 # ⚙️ Setup verification script
├── analytics_output/              # 💾 Generated results
│   ├── query_results/             # CSV & Parquet files
│   └── visuals/                   # Charts & graphs
├── streaming_input/               # 📥 Streaming data batches
└── reports/                       # 📄 Analysis reports
```

### 🎯 Features

#### Complex Queries
- **Query 1:** Top skills by industry with ranking (Window functions)
- **Query 2:** Average skills required per industry (Aggregations)
- **Query 3:** Cross-industry skill analysis (DISTINCT + GROUP BY)

#### Streaming Analytics
- Real-time job posting processing
- Multiple concurrent streaming queries
- Location, experience, and company trend analysis
- ~50 records per batch, 5-second intervals

#### Visualizations
- Top skills by industry (bar charts)
- Average skill requirements (horizontal bars)
- Cross-industry skill distribution

### 📊 Key Outputs

#### Query Results
- `analytics_output/query_results/skills_by_industry.csv`
- `analytics_output/query_results/avg_skills_by_industry.csv`
- `analytics_output/query_results/cross_industry_skills.csv`

#### Visualizations
- `analytics_output/visuals/top_skills_by_industry.png`
- `analytics_output/visuals/avg_skills_by_industry.png`
- `analytics_output/visuals/cross_industry_skills.png`

### 🔮 Next Steps: ML Integration

1. **Job-Skill Matching System:** TF-IDF + Cosine Similarity
2. **Skill Demand Forecasting:** Facebook Prophet (Time Series)
3. **Cloud Deployment:** AWS EMR for distributed processing
4. **Dashboard:** Real-time visualization with Plotly/Streamlit

See `ML_INTEGRATION_PLAN.md` for detailed roadmap.

### 📖 Documentation

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete presentation guide with step-by-step instructions
- **[ML_INTEGRATION_PLAN.md](ML_INTEGRATION_PLAN.md)** - Machine Learning integration roadmap
- **[GITHUB_ISSUE_TEMPLATE.md](GITHUB_ISSUE_TEMPLATE.md)** - Template for check-in updates

### 🛠️ Technologies

- **Apache Spark** - Distributed data processing
- **PySpark** - Python API for Spark
- **Spark Structured Streaming** - Real-time processing
- **Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Visualization

### 🐛 Troubleshooting

**Issue:** OutOfMemory errors  
**Fix:** Increase driver memory: `.config("spark.driver.memory", "4g")`

**Issue:** Streaming not updating  
**Fix:** Ensure `streaming_data_simulator.py` is running

**Issue:** PySpark import errors  
**Fix:** `pip install pyspark` and restart Python kernel

**Issue:** File path errors  
**Fix:** Use absolute paths or verify current working directory

### 🎬 Demo Checklist

- [ ] Run `setup_demo.ps1` to verify environment
- [ ] Execute `complex_queries.ipynb` and save visualizations
- [ ] Test streaming demo (processor + simulator)
- [ ] Take screenshots for GitHub Issue
- [ ] Review `DEMO_GUIDE.md` for presentation flow
- [ ] Prepare 5-7 minute presentation
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