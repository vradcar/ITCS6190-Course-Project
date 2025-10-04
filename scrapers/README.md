# Job Scrapers

A robust system for scraping job postings from Y Combinator and LinkedIn, designed for cloud deployment with Cloudflare Workers.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies and set up environment
python setup.py

# Copy environment template and configure
cp .env.example .env
# Edit .env with your actual values
```

### 2. Test the System
```bash
# Run all tests to verify setup
python test_scrapers.py
```

### 3. Start Scraping
```bash
# Run Y Combinator scraper (easier target)
python run_scraper.py yc --keywords "Software Engineer"

# Run LinkedIn scraper (requires credentials)
python run_scraper.py linkedin --keywords "Data Scientist" --location "San Francisco"

# Run both scrapers
python run_scraper.py both --keywords "Product Manager"
```

## 📁 Project Structure

```
scrapers/
├── setup.py              # One-time setup script
├── test_scrapers.py      # Test suite
├── run_scraper.py        # Unified scraper runner
├── config.py             # Configuration management
├── yc_scraper.py         # Y Combinator scraper
├── linkedin_scraper.py   # LinkedIn scraper (with browser automation)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your actual configuration (ignored by git)
├── scraped_data/        # Local data storage (fallback)
├── logs/                # Log files
└── debug/               # Debug files
```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# Cloudflare Worker endpoint (for storing data)
WORKER_ENDPOINT=https://your-worker-subdomain.workers.dev

# LinkedIn credentials (required for LinkedIn scraper)
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# Rate limiting settings
SCRAPE_DELAY=2
MAX_JOBS_PER_RUN=50
```

## 🎯 Scrapers Overview

### Y Combinator Scraper (`yc_scraper.py`)
- **Target**: [Work at a Startup](https://www.workatastartup.com)
- **Difficulty**: Easy ✅
- **Method**: HTTP requests + BeautifulSoup
- **Authentication**: None required
- **Rate Limiting**: Respectful delays between requests

**Features**:
- Two-phase scraping (list → detail pages)
- Automatic retry and fallback
- Local storage when Worker is unavailable
- Debug mode for troubleshooting

### LinkedIn Scraper (`linkedin_scraper.py`)
- **Target**: LinkedIn Jobs
- **Difficulty**: Hard ⚠️
- **Method**: Browser automation (Playwright)
- **Authentication**: Login required
- **Rate Limiting**: Extra-long delays to avoid detection

**Features**:
- Realistic browser simulation
- Automatic login handling
- Challenge detection (CAPTCHA, verification)
- Infinite scroll support
- Stealth mode to avoid detection

## 🛠️ Usage Examples

### Basic Usage
```bash
# Y Combinator: Search for software engineers
python run_scraper.py yc --keywords "Software Engineer"

# LinkedIn: Search with location
python run_scraper.py linkedin --keywords "Product Manager" --location "Seattle, WA"

# Both: Run all scrapers
python run_scraper.py both --keywords "AI Engineer" --max-jobs 30
```

### Advanced Usage
```bash
# YC with role type filter
python run_scraper.py yc --keywords "Data Scientist" --role-type "full-time"

# LinkedIn with fewer jobs (for testing)
python run_scraper.py linkedin --keywords "DevOps" --max-jobs 5

# Check configuration
python run_scraper.py --check-config
```

### Individual Scripts
```bash
# Run YC scraper directly
python yc_scraper.py

# Run LinkedIn scraper directly
python linkedin_scraper.py
```

## ⚠️ Important Warnings

### LinkedIn Scraping
- **Terms of Service**: LinkedIn prohibits automated scraping
- **Anti-Bot Measures**: LinkedIn actively detects and blocks scrapers
- **Account Risk**: Your LinkedIn account may be temporarily restricted
- **Rate Limiting**: Use long delays and scrape responsibly
- **Manual Intervention**: You may need to solve CAPTCHAs manually

### Best Practices
1. **Start Small**: Test with `--max-jobs 5` first
2. **Be Patient**: Don't rush the scraping process
3. **Monitor**: Watch for errors and warnings
4. **Backup**: Data is automatically saved locally as fallback
5. **Respect**: Don't hammer servers with rapid requests

## 🔍 Data Flow

```
1. Scraper runs locally (Python)
   ↓
2. Extracts job data (title, company, description, etc.)
   ↓
3. Sends to Cloudflare Worker (HTTP POST)
   ↓
4. Worker stores in D1 database
   ↓
5. Fallback: Save locally if Worker unavailable
```

## 📊 Output Data Schema

Each scraped job contains:
```json
{
  "url": "https://example.com/job/123",
  "source": "y_combinator",
  "title": "Senior Software Engineer",
  "company": "Example Corp",
  "location": "San Francisco, CA",
  "description_text": "We are looking for...",
  "description_html": "<div>We are looking for...</div>",
  "scraped_at": "2025-10-03 15:30:00"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Import errors"**
   - Run `python setup.py` to install dependencies

2. **"No job links found"**
   - Check `debug_*.html` files for page structure changes
   - Website layouts may have changed

3. **"LinkedIn login failed"**
   - Verify credentials in `.env` file
   - Complete manual challenges when prompted
   - Try from a different IP address

4. **"Worker endpoint unreachable"**
   - Data will be saved locally in `scraped_data/`
   - Set up Cloudflare Worker (see `../cloudflare-worker/`)

5. **"Too many requests"**
   - Increase `SCRAPE_DELAY` in `.env`
   - Reduce `MAX_JOBS_PER_RUN`
   - Wait before retrying

### Debug Mode

For debugging, check these files:
- `debug_yc_page.html` - YC search results page
- `debug_yc_job.html` - Individual YC job page
- `scraped_data/*.json` - All scraped job data

## 🔄 Development

### Adding New Scrapers

1. Create new scraper file (e.g., `indeed_scraper.py`)
2. Follow the same pattern as existing scrapers
3. Add to `run_scraper.py`
4. Update tests in `test_scrapers.py`

### Testing Changes

```bash
# Run tests
python test_scrapers.py

# Test specific scraper
python yc_scraper.py

# Check configuration
python run_scraper.py --check-config
```

## 📈 Performance Tips

1. **Parallel Processing**: Don't run multiple scrapers simultaneously
2. **Rate Limiting**: Increase delays if you get blocked
3. **Batch Size**: Use smaller `--max-jobs` for testing
4. **Monitoring**: Watch for HTTP errors and adjust accordingly

## 🔗 Integration

This scraping system is designed to work with:
- **Cloudflare Workers** (data storage)
- **D1 Database** (persistence)
- **Your analytics system** (via API)

See `../cloudflare-worker/` for the backend setup.