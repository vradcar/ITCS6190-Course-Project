# Job Market Analytics with Apache Spark

This directory contains Spark jobs for processing job data from R2 storage.

## Architecture

```
R2 Bucket (job-data/) → Spark → Analytics Results
```

## Setup

### 1. Install Dependencies
```bash
pip install pyspark boto3 pandas matplotlib seaborn
```

### 2. Configure AWS/R2 Credentials
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_r2_access_key
export AWS_SECRET_ACCESS_KEY=your_r2_secret_key
export R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
export R2_BUCKET=job-data-bucket
```

### 3. Run Analytics
```bash
# Daily job market analysis
python daily_analytics.py --date 2025-10-03

# Company analysis
python company_analysis.py --start-date 2025-10-01 --end-date 2025-10-03

# Skills extraction
python skills_analysis.py --source y_combinator
```

## Jobs

- `daily_analytics.py` - Daily job market trends
- `company_analysis.py` - Company hiring patterns
- `skills_analysis.py` - In-demand skills analysis
- `location_analysis.py` - Geographic job distribution
- `trend_analysis.py` - Historical trend analysis

## Output

Results are saved to:
- Local CSV files
- R2 bucket (`analytics-results/`)
- Dashboard data files