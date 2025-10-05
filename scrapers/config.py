"""
Configuration and utilities for web scrapers
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for scrapers"""
    
    # Worker endpoint
    WORKER_ENDPOINT = os.getenv('WORKER_ENDPOINT', '')
    
    # LinkedIn credentials
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')
    
    # Rate limiting
    SCRAPE_DELAY = int(os.getenv('SCRAPE_DELAY', 2))
    MAX_JOBS_PER_RUN = int(os.getenv('MAX_JOBS_PER_RUN', 50))
    
    # User agents for different scrapers
    USER_AGENTS = {
        'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    }
    
    # Common headers
    COMMON_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def get_headers(user_agent='chrome'):
    """Get headers with specified user agent"""
    headers = Config.COMMON_HEADERS.copy()
    headers['User-Agent'] = Config.USER_AGENTS.get(user_agent, Config.USER_AGENTS['chrome'])
    return headers

def validate_config():
    """Validate that required configuration is present"""
    issues = []
    
    if not Config.WORKER_ENDPOINT:
        issues.append("WORKER_ENDPOINT not set - data will be saved locally")
    
    if not Config.LINKEDIN_EMAIL or not Config.LINKEDIN_PASSWORD:
        issues.append("LinkedIn credentials not set - LinkedIn scraper will not work")
    
    return issues