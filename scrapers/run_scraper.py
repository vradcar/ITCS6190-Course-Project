#!/usr/bin/env python3
"""
Unified job scraper runner
Can run Y Combinator scraper, LinkedIn scraper, or both
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from yc_scraper import YCScraper
from linkedin_scraper import LinkedInScraper
from config import Config, validate_config

def run_yc_scraper(args):
    """Run the Y Combinator scraper"""
    print("🚀 Starting Y Combinator scraper...")
    
    scraper = YCScraper()
    scraper.run_scraper(
        search_terms=args.keywords,
        role_type=args.role_type
    )

async def run_linkedin_scraper(args):
    """Run the LinkedIn scraper"""
    print("🚀 Starting LinkedIn scraper...")
    
    scraper = LinkedInScraper()
    await scraper.run_scraper(
        keywords=args.keywords,
        location=args.location,
        max_jobs=args.max_jobs
    )

def run_both_scrapers(args):
    """Run both scrapers sequentially"""
    print("🚀 Starting both scrapers...")
    
    # Run YC scraper first (synchronous)
    print("\n" + "="*60)
    print("PHASE 1: Y COMBINATOR SCRAPER")
    print("="*60)
    run_yc_scraper(args)
    
    # Run LinkedIn scraper (asynchronous)
    print("\n" + "="*60)
    print("PHASE 2: LINKEDIN SCRAPER")
    print("="*60)
    asyncio.run(run_linkedin_scraper(args))

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Job Scraper - Scrape jobs from Y Combinator and/or LinkedIn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py yc --keywords "Software Engineer"
  python run_scraper.py linkedin --keywords "Data Scientist" --location "New York"
  python run_scraper.py both --keywords "Product Manager" --max-jobs 20
  python run_scraper.py yc --keywords "AI Engineer" --role-type full-time
        """
    )
    
    parser.add_argument(
        'scraper',
        choices=['yc', 'linkedin', 'both'],
        help='Which scraper to run: yc (Y Combinator), linkedin, or both'
    )
    
    parser.add_argument(
        '--keywords',
        default='Software Engineer',
        help='Job search keywords (default: "Software Engineer")'
    )
    
    parser.add_argument(
        '--location',
        default='',
        help='Job location for LinkedIn search (optional)'
    )
    
    parser.add_argument(
        '--role-type',
        help='Role type filter for Y Combinator (optional)'
    )
    
    parser.add_argument(
        '--max-jobs',
        type=int,
        default=Config.MAX_JOBS_PER_RUN,
        help=f'Maximum number of jobs to scrape (default: {Config.MAX_JOBS_PER_RUN})'
    )
    
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Check configuration
    if args.check_config:
        print("🔧 Checking configuration...")
        issues = validate_config()
        if issues:
            print("⚠️ Configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Configuration looks good!")
        return
    
    # Validate configuration for the chosen scraper
    issues = validate_config()
    if args.scraper in ['linkedin', 'both'] and not Config.LINKEDIN_EMAIL:
        print("❌ LinkedIn credentials required for LinkedIn scraper")
        print("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file")
        return
    
    # Show configuration warnings
    if issues:
        print("⚠️ Configuration warnings:")
        for issue in issues:
            print(f"   - {issue}")
        print()
    
    # Run the appropriate scraper
    try:
        if args.scraper == 'yc':
            run_yc_scraper(args)
        elif args.scraper == 'linkedin':
            asyncio.run(run_linkedin_scraper(args))
        elif args.scraper == 'both':
            run_both_scrapers(args)
    except KeyboardInterrupt:
        print("\n\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()