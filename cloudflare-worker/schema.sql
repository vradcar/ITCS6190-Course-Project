-- Database schema for job scraper
-- This creates the table structure for storing scraped job data

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    title TEXT,
    company TEXT,
    location TEXT,
    description_text TEXT,
    description_html TEXT,
    salary TEXT,              -- New field for salary range
    job_type TEXT,            -- New field for job type (Full-time, Part-time, etc.)
    experience_level TEXT,    -- New field for experience level (Senior, Junior, etc.)
    scraped_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table for tracking automated scraping jobs
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    job_type TEXT NOT NULL,
    source TEXT,
    max_jobs INTEGER,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    jobs_scraped INTEGER DEFAULT 0,
    error_message TEXT
);

-- Table for tracking data exports to R2
CREATE TABLE IF NOT EXISTS data_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    file_path TEXT NOT NULL,
    job_count INTEGER NOT NULL,
    exported_at TEXT NOT NULL,
    file_size INTEGER,
    status TEXT DEFAULT 'completed'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_started ON scraping_jobs(started_at);
CREATE INDEX IF NOT EXISTS idx_data_exports_date ON data_exports(date);