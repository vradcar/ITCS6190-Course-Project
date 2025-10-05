# GitHub Secrets Configuration Guide

## Required Secrets for Automated Pipeline

To enable the GitHub Actions automation, you need to configure the following secrets in your repository:

### 🔑 How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 📋 Required Secrets

#### `WORKER_ENDPOINT`
- **Value**: `https://job-scraper-worker.job-scraper-unhinged.workers.dev`
- **Description**: Cloudflare Worker API endpoint for job data submission

### 🚀 Workflow Triggers

#### Daily Scraping Workflow
- **File**: `.github/workflows/daily-scraping.yml`
- **Schedule**: 6:30 AM UTC daily (30 min after Worker cron)
- **Manual Trigger**: Available with custom parameters
- **Actions**:
  1. Runs enhanced YC scraper
  2. Processes jobs with analytics pipeline
  3. Submits data to Worker API

#### Weekly Analytics Workflow  
- **File**: `.github/workflows/weekly-analytics.yml`
- **Schedule**: 8:00 AM UTC every Sunday
- **Manual Trigger**: Available with date range options
- **Actions**:
  1. Generates comprehensive weekly reports
  2. Analyzes trends and insights
  3. Uploads results as artifacts

### 🔧 Manual Triggering

You can manually trigger workflows from GitHub Actions tab:

#### Daily Scraping Parameters:
- `max_jobs`: Number of jobs to scrape (default: 50)
- `days_back`: Days back to search (default: 30)

#### Weekly Analytics Parameters:
- `start_date`: Analysis start date (YYYY-MM-DD)
- `end_date`: Analysis end date (YYYY-MM-DD)  
- `report_type`: daily or weekly (default: weekly)

### ✅ Setup Verification

After adding secrets, test the setup:

1. Go to **Actions** tab in your repository
2. Select **Enhanced YC Job Scraping Pipeline**
3. Click **Run workflow**
4. Monitor the execution logs

### 📊 Expected Results

**Daily Pipeline**:
- Enhanced YC jobs scraped and submitted to Worker
- Analytics processed and saved
- Data available in Cloudflare D1 database

**Weekly Pipeline**:
- Comprehensive trend analysis
- Skill demand insights
- Salary range analysis
- Results downloadable as artifacts

### 🔍 Troubleshooting

**Common Issues**:
- **Secret not found**: Check secret name matches exactly
- **API connection failed**: Verify Worker endpoint URL
- **Scraping failed**: Check if YC changed their structure

**Debug Steps**:
1. Check workflow logs in Actions tab
2. Verify Worker is responding: `curl [WORKER_ENDPOINT]/api/stats`
3. Test scraper locally: `python yc_scraper_enhanced.py`

### 🎯 Complete Automation Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  GitHub Actions │───▶│ Enhanced Scraper │───▶│ Cloudflare     │
│  Daily 6:30 UTC │    │  (50 jobs)       │    │ Worker API     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Spark Analytics  │    │   D1 Database   │
                       │   Processing     │    │   (Storage)     │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Weekly Reports   │    │ R2 Data Export  │
                       │  (Artifacts)     │    │  (Archive)      │
                       └──────────────────┘    └─────────────────┘
```

Your pipeline will be fully automated once secrets are configured! 🚀