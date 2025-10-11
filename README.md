# ITCS6190 Cloud Computing Course Project
## Y Combinator Job Market Analysis Pipeline

<ins>**Group Name: Unattached and Unhinged**</ins>

**Team Members:**
- Varad Paradkar (801418318) - vparadka@charlotte.edu
- Mitali Yadav (801453849) - myadav5@charlotte.edu  
- Sudeepta Bal (801455628) - sbal1@charlotte.edu
- Ruthwik Dovala (801431661) - rdovala@charlotte.edu

## 🎯 Project Overview

This project builds a comprehensive cloud-based data pipeline for Y Combinator job market analysis, featuring automated web scraping, real-time data processing, and analytics to provide insights into startup hiring trends, salary ranges, and job market opportunities.

### 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  YC Enhanced    │───▶│ Cloudflare Worker │───▶│   D1 Database   │
│    Scraper      │    │  (API + Cron)     │    │   (Storage)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        ▼                        │
         │              ┌──────────────────┐               │
         └─────────────▶│   R2 Storage     │◀──────────────┘
                        │  + Spark Analytics│
                        └──────────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │   Job Insights   │
                       │  & Visualizations │
                       └──────────────────┘
```

## 🚀 Features

- **Enhanced YC Job Scraping**: Comprehensive job data extraction with salary ranges, locations, and detailed descriptions
- **24/7 Automated Pipeline**: Daily scraping and data export via Cloudflare Workers cron jobs
- **Cloud-Native Storage**: Cloudflare Workers + D1 Database + R2 Object Storage
- **Rich Data Quality**: Company names, locations, descriptions, salary ranges, job types, and experience levels
- **Scalable Architecture**: Built for cloud deployment and automated processing

## 📂 Project Structure

```
ITCS6190-Course-Project/
├── Documentation/                 # Project documentation & proposal
├── scrapers/                     # Enhanced web scraping system
│   ├── yc_scraper_enhanced.py   # Main YC scraper with comprehensive data extraction
│   ├── run_scraper.py           # Scraper execution script
│   ├── config.py                # Configuration management
│   ├── requirements.txt         # Python dependencies
│   ├── scraped_data/           # Sample scraped data (5 recent files)
│   └── README.md               # Scraper documentation
├── cloudflare-worker/          # Cloud backend & automation
│   ├── src/worker.js          # Worker with cron jobs & data export
│   ├── schema.sql             # Database schema with enhanced fields
│   ├── wrangler.toml          # Cloudflare configuration
│   └── README.md              # Deployment instructions
├── spark-analytics/           # Data processing & analytics
│   ├── daily_analytics.py     # Spark job for data analysis
│   ├── requirements.txt       # Spark dependencies
│   └── README.md              # Analytics documentation
├── .github/workflows/         # CI/CD automation
│   └── daily-scraping.yml     # GitHub Actions for automated scraping
└── README.md                  # This file
```

## 🛠️ Quick Start Guide

### 1. Test the Enhanced YC Scraper

```bash
cd scrapers/

# Install dependencies
pip install -r requirements.txt

# Run the enhanced scraper manually
python yc_scraper_enhanced.py

# Test pipeline integration
cd .. && python test_pipeline.py
```

### 2. Set Up GitHub Actions Automation

```bash
# 1. Fork/clone this repository to your GitHub account

# 2. Configure repository secrets:
#    Go to Settings → Secrets → Actions → New repository secret
#    Add: WORKER_ENDPOINT = https://job-scraper-worker.job-scraper-unhinged.workers.dev

# 3. Enable GitHub Actions:
#    Go to Actions tab and enable workflows

# 4. Manual trigger test:
#    Actions → Enhanced YC Job Scraping Pipeline → Run workflow
```

### 3. Deploy Cloudflare Worker (Optional - Already Deployed)

```bash
cd cloudflare-worker/

# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy (database and worker already configured)
wrangler deploy
```

### 4. Run Spark Analytics

```bash
cd spark-analytics/

# Install dependencies
pip install -r requirements.txt

# Run daily analysis
python daily_analytics.py --date 2025-10-03

# Generate weekly report
python daily_analytics.py --weekly --start-date 2025-09-27 --end-date 2025-10-03
```

---

## 📊 Exploratory Data Analysis (EDA)

The exploratory data analysis (EDA) was conducted to uncover patterns, trends, and relationships within the Y Combinator job market dataset.

### 🔹 **Datasets Analyzed**
- **companies.csv** – 91,026 company records  
- **jobs.csv** – 288,439 job listings  
- **postings.csv** – 204,693 job postings  
- **company_industries.csv** and **company_specialities.csv** – industry-level attributes  

All analyses and visualizations are implemented in:
- `spark-analytics/data_analysis.py`

---

### 🔍 **Key Findings**

#### 1. Industry and Specialization Insights
- Visualizations of the **top 20 industries and specialties** reveal dominance by **Technology**, **Finance**, and **Healthcare** sectors.  
- Frequency plots and bar charts show these sectors contributing the majority of job postings.

#### 2. Company Scale vs Job Activity
- Merging `companies.csv`, `employee_counts.csv`, and `company_industries.csv` confirmed that **larger organizations post more jobs**.  
- A strong positive correlation was observed between **company size** and **posting frequency**.

#### 3. Sector-wise Job Density
- PySpark joins linking jobs and industry datasets highlight **IT**, **Consulting**, and **Finance** as sectors with the highest **job density** and **posting frequency**.

#### 4. Data Quality & Cleaning
- `.info()` and `.value_counts()` were used to inspect missing values and outliers.  
- Identified companies with **>500 postings**, indicating possible **data skew or intensive recruitment**.  
- The `postings.csv` file was cleaned to remove missing and inconsistent entries for accurate analysis.

---

### 📈 **Visualization Summary**

| Visualization Type | Description |
|---------------------|-------------|
| **Bar Charts** | Top 20 industries and specialties |
| **Heatmaps** | Company size vs. number of postings |
| **Frequency Plots** | Job distribution across sectors |
| **Trend Lines** | Company size vs. posting activity |

All visuals are available in **`spark-analytics/data_analysis.ipynb`** under the **Spark Analytics branch**.

---

### 🧠 **Insights**
- A few dominant industries (Technology, Finance, Healthcare) account for most postings, following a **power-law trend**.  
- **Company size** directly influences job posting activity.  
- Cleaned datasets ensure reliability for **Spark MLlib** and **real-time job forecasting** in later phases.

---


## 🎯 Automated Pipeline Features

### ✅ **Currently Active:**
- **Daily Scraping**: GitHub Actions runs enhanced YC scraper at 6:30 AM UTC
- **Data Storage**: Cloudflare Worker API with D1 database
- **Data Export**: Daily job data export to R2 storage
- **Analytics**: Comprehensive Spark-based job market analysis
- **Rich Data**: Salary ranges, job types, experience levels, company details

### � **Data Analysis Capabilities:**
- **Company Trends**: Top hiring companies and job volumes
- **Salary Analysis**: Compensation ranges and market rates
- **Skill Demand**: Most requested technical skills
- **Location Insights**: Geographic distribution of opportunities
- **Remote Work**: Remote vs on-site job percentages
- **Weekly Reports**: Trend analysis and market insights
- [x] API for data access (implemented)

### Phase 2: Spark Analytics (In Progress)
- [ ] Spark SQL for job market analysis
- [ ] Real-time streaming processing
- [ ] Data aggregation and trend analysis
- [ ] Geographic and temporal insights

### Phase 3: Machine Learning (Planned)
- [ ] Job classification models (MLlib)
- [ ] Skill extraction and analysis
- [ ] Salary prediction models
- [ ] Industry trend forecasting

### Phase 4: Visualization (Planned)
- [ ] Interactive dashboards
- [ ] Real-time monitoring
- [ ] Market insights reports
- [ ] API for external integrations

## 🎯 Key Research Questions

1. **Market Trends**: Which roles are in highest demand?
2. **Geographic Analysis**: Where are the best opportunities?
3. **Skill Mapping**: What skills are most valuable?
4. **Company Insights**: Who's hiring the most?
5. **Temporal Patterns**: How do job postings vary over time?

## ⚠️ Important Notes

### Web Scraping Ethics
- **Respectful scraping**: Built-in rate limiting and delays
- **Terms of Service**: Be aware of website policies
- **Account Safety**: LinkedIn scraping may trigger security measures
- **Data Usage**: For educational and research purposes only

### Technical Considerations
- **Scalability**: Designed for cloud deployment
- **Reliability**: Fallback mechanisms and error handling
- **Performance**: Optimized for large-scale data processing
- **Maintenance**: Modular design for easy updates

## 📈 Current Status

- ✅ **Web Scrapers**: Y Combinator and LinkedIn scrapers implemented
- ✅ **Cloud Backend**: Cloudflare Worker with D1 database
- ✅ **Data Pipeline**: Complete scraping → storage → API flow
- 🔄 **Analytics**: Spark analysis components in development
- 📋 **ML Pipeline**: Machine learning models planned
- 📋 **Visualization**: Dashboard and reporting planned

---

**Course**: ITCS 6190 - Cloud Computing  
**Semester**: Fall 2025  
**University**: University of North Carolina at Charlotte
