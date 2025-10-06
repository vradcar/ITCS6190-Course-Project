# YC Job Analytics Pipeline

This directory contains the analytics pipeline for processing Y Combinator job data, with both simple and Spark-based implementations.

## 🚀 Quick Start

### Option 1: Simple Analytics (Recommended for GitHub Actions)
```bash
cd spark-analytics
python simple_analytics.py --days-back 7
```

### Option 2: Spark Analytics (Local Development)
```bash
cd spark-analytics
pip install -r requirements.txt
python daily_analytics.py --days-back 7
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