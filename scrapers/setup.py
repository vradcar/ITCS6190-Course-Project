#!/usr/bin/env python3
"""
Setup script for the job scrapers
Run this to install dependencies and set up the environment
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("JOB SCRAPER SETUP")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install Playwright browsers (for LinkedIn scraper)
    if not run_command("playwright install chromium", "Installing Playwright browser"):
        print("⚠️ Playwright installation failed. LinkedIn scraper may not work.")
    
    # Create .env file if it doesn't exist
    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"\n📝 Creating {env_path} file...")
        try:
            with open(".env.example", "r") as example_file:
                content = example_file.read()
            
            with open(env_path, "w") as env_file:
                env_file.write(content)
            
            print(f"✅ Created {env_path}")
            print("⚠️ Please edit .env file with your actual configuration values")
        except Exception as e:
            print(f"❌ Failed to create {env_path}: {e}")
    else:
        print(f"✅ {env_path} already exists")
    
    # Create data directories
    data_dirs = ["scraped_data", "logs", "debug"]
    for directory in data_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration")
    print("2. Test the Y Combinator scraper: python yc_scraper.py")
    print("3. Set up your Cloudflare Worker (see cloudflare-worker/ directory)")
    print("4. Test the LinkedIn scraper: python linkedin_scraper.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)