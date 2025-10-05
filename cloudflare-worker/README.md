# Cloudflare Worker for Job Scraper

This directory contains the Cloudflare Worker that receives and stores scraped job data.

## Setup Instructions

### 1. Install Wrangler CLI
```bash
npm install -g wrangler
```

### 2. Login to Cloudflare
```bash
wrangler login
```

### 3. Create D1 Database
```bash
wrangler d1 create job_scraper_db
```

This will output a database ID. Copy this ID and update the `database_id` in `wrangler.toml`.

### 4. Create the Database Schema
```bash
wrangler d1 execute job_scraper_db --file=schema.sql
```

### 5. Install Dependencies
```bash
npm install
```

### 6. Test Locally (Optional)
```bash
npm run dev
```

### 7. Deploy to Production
```bash
npm run deploy
```

## API Endpoints

- `POST /api/jobs` - Store scraped job data
- `GET /api/jobs` - Retrieve job data (with pagination)
- `GET /api/stats` - Get database statistics
- `GET /` - API documentation

## Environment Variables

Update `wrangler.toml` with your actual database ID before deploying.

## Testing the API

After deployment, you'll get a Worker URL. Update your scraper's `.env` file with:
```
WORKER_ENDPOINT=https://your-worker-name.your-subdomain.workers.dev
```

## Database Schema

The `jobs` table stores:
- `id` - Auto-incrementing primary key
- `url` - Job posting URL (unique)
- `source` - Source of the job (e.g., "y_combinator", "linkedin")
- `title` - Job title
- `company` - Company name
- `location` - Job location
- `description_text` - Plain text job description
- `description_html` - HTML job description
- `scraped_at` - When the job was scraped
- `created_at` - When the record was created