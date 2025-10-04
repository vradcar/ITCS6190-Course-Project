import requests
from bs4 import BeautifulSoup
import time
import json
import os
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class YCScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.worker_endpoint = os.getenv('WORKER_ENDPOINT', '')
        self.scrape_delay = int(os.getenv('SCRAPE_DELAY', 2))
        self.max_jobs = int(os.getenv('MAX_JOBS_PER_RUN', 100))
        
    def get_recent_job_links(self, days_back=30):
        """
        Get individual job listings from Y Combinator from the last month
        """
        print(f"Fetching YC job listings from the last {days_back} days...")
        
        # Try multiple YC job board URLs
        job_urls = [
            "https://www.ycombinator.com/jobs",
            "https://www.workatastartup.com/jobs",
            "https://www.ycombinator.com/companies"
        ]
        
        all_job_links = set()
        
        for base_url in job_urls:
            try:
                print(f"Trying URL: {base_url}")
                response = self.session.get(base_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job links with various patterns
                job_link_patterns = [
                    'a[href*="/companies/"][href*="/jobs/"]',  # Company job links
                    'a[href*="/jobs/"]',                       # Direct job links
                    'a[data-testid*="job"]',                   # Test ID job links
                    '.job-listing a',                          # Job listing containers
                ]
                
                for pattern in job_link_patterns:
                    links = soup.select(pattern)
                    print(f"Found {len(links)} links with pattern: {pattern}")
                    
                    for link in links:
                        href = link.get('href')
                        if href:
                            # Convert relative URLs to absolute
                            if href.startswith('/'):
                                if 'ycombinator.com' in base_url:
                                    full_url = f"https://www.ycombinator.com{href}"
                                else:
                                    full_url = f"https://www.workatastartup.com{href}"
                            else:
                                full_url = href
                            
                            # Filter for actual job postings
                            if any(pattern in full_url for pattern in ['/jobs/', '/companies/']) and 'jobs' in full_url:
                                all_job_links.add(full_url)
                                
                        if len(all_job_links) >= self.max_jobs:
                            break
                    
                    if len(all_job_links) >= self.max_jobs:
                        break
                        
            except requests.RequestException as e:
                print(f"Error fetching from {base_url}: {e}")
                continue
        
        # Also try to get jobs from the YC companies directory
        try:
            companies_url = "https://www.ycombinator.com/companies"
            print(f"Getting company links from: {companies_url}")
            response = self.session.get(companies_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            company_links = soup.select('a[href*="/companies/"]')
            
            print(f"Found {len(company_links)} company links")
            
            # Visit some company pages to find their job listings
            for i, link in enumerate(company_links[:20]):  # Limit to first 20 companies
                href = link.get('href')
                if href:
                    company_url = urljoin("https://www.ycombinator.com", href)
                    job_links = self.get_company_jobs(company_url)
                    all_job_links.update(job_links)
                    
                    if len(all_job_links) >= self.max_jobs:
                        break
                        
                # Small delay between company requests
                time.sleep(1)
                        
        except requests.RequestException as e:
            print(f"Error fetching company directory: {e}")
        
        job_links_list = list(all_job_links)[:self.max_jobs]
        print(f"Total unique job links found: {len(job_links_list)}")
        
        if not job_links_list:
            print("No job links found. Let's debug...")
            self.debug_page_structure(job_urls[0])
        
        return job_links_list
    
    def get_company_jobs(self, company_url):
        """
        Get job listings from a specific YC company page
        """
        job_links = set()
        
        try:
            response = self.session.get(company_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for job links on the company page
            job_elements = soup.select('a[href*="/jobs/"]')
            
            for element in job_elements:
                href = element.get('href')
                if href:
                    full_url = urljoin("https://www.ycombinator.com", href)
                    job_links.add(full_url)
                    
        except requests.RequestException as e:
            print(f"Error fetching company jobs from {company_url}: {e}")
        
        return job_links
    
    def debug_page_structure(self, url):
        """
        Debug helper to understand page structure
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save HTML for manual inspection
            with open('debug_yc_structure.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved page structure to debug_yc_structure.html")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Print all links for analysis
            all_links = soup.find_all('a', href=True)
            print(f"Found {len(all_links)} total links")
            
            # Group links by pattern
            job_related = [link for link in all_links if 'job' in link.get('href', '').lower() or 'job' in link.get_text().lower()]
            company_related = [link for link in all_links if 'compan' in link.get('href', '').lower()]
            
            print(f"Job-related links: {len(job_related)}")
            print(f"Company-related links: {len(company_related)}")
            
            for link in job_related[:10]:
                print(f"  Job link: {link.get('href')} - {link.get_text(strip=True)[:50]}")
                
        except Exception as e:
            print(f"Debug failed: {e}")
            
    def scrape_job_details(self, job_url):
        """
        Enhanced job detail scraping with better selectors for YC job pages
        """
        try:
            print(f"Scraping job details: {job_url}")
            response = self.session.get(job_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize job data
            job_data = {
                'url': job_url,
                'source': 'y_combinator',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Enhanced selectors for YC job pages
            # Job Title
            title_selectors = [
                'h1',
                '[data-testid="job-title"]',
                '.job-title',
                '.title',
                'h1.text-2xl',  # Common Tailwind CSS class
                'h2'
            ]
            
            job_data['title'] = self.extract_text(soup, title_selectors)
            
            # Company Name
            company_selectors = [
                '[data-testid="company-name"]',
                '.company-name',
                '.company',
                'h2',
                'h3',
                '.text-lg',  # Company name might be in a large text element
                'a[href*="/companies/"]'  # Link to company page
            ]
            
            job_data['company'] = self.extract_text(soup, company_selectors)
            
            # Location
            location_selectors = [
                '[data-testid="location"]',
                '.location',
                '.job-location',
                '[aria-label*="location"]',
                'span:contains("Remote")',
                'span:contains("San Francisco")',
                'span:contains("New York")',
                '.text-gray-500'  # Location often in gray text
            ]
            
            job_data['location'] = self.extract_text(soup, location_selectors)
            
            # Job Description
            desc_selectors = [
                '[data-testid="job-description"]',
                '.job-description',
                '.description',
                '.content',
                '.prose',  # Common for markdown content
                'div[class*="description"]',
                '.job-details'
            ]
            
            desc_element = self.extract_element(soup, desc_selectors)
            if desc_element:
                job_data['description_html'] = str(desc_element)
                job_data['description_text'] = desc_element.get_text(strip=True, separator=' ')
            
            # Try to extract additional metadata
            # Salary/Compensation
            salary_selectors = [
                '[data-testid="salary"]',
                '.salary',
                '.compensation',
                'span:contains("$")',
                '.pay'
            ]
            
            salary = self.extract_text(soup, salary_selectors)
            if salary and '$' in salary:
                job_data['salary'] = salary
                
            # Job Type (Full-time, Part-time, etc.)
            type_selectors = [
                '[data-testid="job-type"]',
                '.job-type',
                'span:contains("Full-time")',
                'span:contains("Part-time")',
                'span:contains("Contract")'
            ]
            
            job_type = self.extract_text(soup, type_selectors)
            if job_type:
                job_data['job_type'] = job_type
            
            # Experience Level
            experience_selectors = [
                '[data-testid="experience"]',
                '.experience',
                'span:contains("Senior")',
                'span:contains("Junior")',
                'span:contains("Mid-level")'
            ]
            
            experience = self.extract_text(soup, experience_selectors)
            if experience:
                job_data['experience_level'] = experience
            
            # If we still don't have basic info, try to extract from page title
            if not job_data.get('title') and soup.title:
                title_text = soup.title.string
                if title_text:
                    # YC job titles often follow pattern: "Job Title at Company | Y Combinator"
                    if ' at ' in title_text and 'Y Combinator' in title_text:
                        parts = title_text.split(' at ')
                        job_data['title'] = parts[0].strip()
                        if len(parts) > 1:
                            company_part = parts[1].split('|')[0].strip()
                            if not job_data.get('company'):
                                job_data['company'] = company_part
                    else:
                        job_data['title'] = title_text.split('|')[0].strip()
            
            # Extract company from URL if not found
            if not job_data.get('company') and '/companies/' in job_url:
                url_parts = job_url.split('/companies/')
                if len(url_parts) > 1:
                    company_slug = url_parts[1].split('/')[0]
                    job_data['company'] = company_slug.replace('-', ' ').title()
            
            # Validate we have minimum required data
            if not job_data.get('title'):
                print(f"Warning: No title found for {job_url}")
                # Save page for debugging
                self.save_debug_page(response.text, f"no_title_{int(time.time())}")
            
            return job_data
            
        except requests.RequestException as e:
            print(f"Error scraping job {job_url}: {e}")
            return None
    
    def extract_text(self, soup, selectors):
        """
        Helper to extract text using multiple selectors
        """
        for selector in selectors:
            if ':contains(' in selector:
                # Handle special CSS selectors with :contains
                search_term = selector.split(':contains("')[1].split('")')[0]
                elements = soup.find_all(text=lambda text: text and search_term in text)
                if elements:
                    return elements[0].strip()
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
        return None
    
    def extract_element(self, soup, selectors):
        """
        Helper to extract element using multiple selectors
        """
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        return None
    
    def save_debug_page(self, html_content, filename_suffix):
        """
        Save problematic pages for debugging
        """
        os.makedirs('debug_pages', exist_ok=True)
        filename = f"debug_pages/yc_job_{filename_suffix}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Saved debug page: {filename}")
        except Exception as e:
            print(f"Error saving debug page: {e}")
    
    def send_to_worker(self, job_data):
        """
        Send scraped job data to Cloudflare Worker
        """
        if not self.worker_endpoint:
            print("No worker endpoint configured, saving locally instead")
            return self.save_locally(job_data)
        
        try:
            response = requests.post(
                f"{self.worker_endpoint}/api/jobs",
                json=job_data,
                timeout=30
            )
            response.raise_for_status()
            print(f"✅ Successfully sent: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
            return True
        except requests.RequestException as e:
            print(f"Error sending data to worker: {e}")
            # Fallback to local storage
            return self.save_locally(job_data)
    
    def save_locally(self, job_data):
        """
        Save job data locally as fallback
        """
        os.makedirs('scraped_data', exist_ok=True)
        filename = f"scraped_data/yc_job_{int(time.time())}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            print(f"Saved job data locally: {filename}")
            return True
        except Exception as e:
            print(f"Error saving locally: {e}")
            return False
    
    def run_scraper(self, days_back=30):
        """
        Enhanced main scraping function - get all jobs from last month
        """
        print("=" * 60)
        print("Y COMBINATOR ENHANCED JOB SCRAPER")
        print(f"Scraping jobs from the last {days_back} days")
        print("=" * 60)
        
        # Get recent job links
        job_links = self.get_recent_job_links(days_back)
        
        if not job_links:
            print("No job links found. Check the debug files for more information.")
            return
        
        print(f"\nFound {len(job_links)} jobs. Starting detailed scraping...")
        print("=" * 60)
        
        # Scrape each job
        success_count = 0
        failed_count = 0
        
        for i, job_url in enumerate(job_links, 1):
            print(f"\n[{i}/{len(job_links)}] Processing job...")
            
            job_data = self.scrape_job_details(job_url)
            
            if job_data and job_data.get('title'):
                # Send to worker or save locally
                if self.send_to_worker(job_data):
                    success_count += 1
                else:
                    failed_count += 1
                    print(f"❌ Failed to store job data")
            else:
                failed_count += 1
                print(f"❌ Failed to scrape job details or missing title")
            
            # Be polite - wait between requests
            if i < len(job_links):
                print(f"Waiting {self.scrape_delay} seconds...")
                time.sleep(self.scrape_delay)
        
        print("\n" + "=" * 60)
        print(f"SCRAPING COMPLETE")
        print(f"✅ Successfully processed: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📊 Total attempted: {len(job_links)}")
        print(f"📈 Success rate: {(success_count/len(job_links)*100):.1f}%")
        print("=" * 60)

if __name__ == "__main__":
    scraper = YCScraper()
    
    # Scrape jobs from the last 30 days with enhanced data extraction
    scraper.run_scraper(days_back=30)