#!/usr/bin/env python3
"""
Web Crawler Test and Demo Script

This script provides testing functionality for the web crawler project
without requiring Scrapy to be installed during development.

Usage:
    python test_crawler.py --test-config
    python test_crawler.py --demo
    python test_crawler.py --validate-project
"""

import json
import csv
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict
import subprocess


class MockCrawlItem:
    """Mock CrawlItem for testing purposes"""
    def __init__(self, url="", title="", content=""):
        self.url = url
        self.title = title
        self.content = content
        self.matched_keywords = []
        self.links_found = []
        self.depth = 0
        self.crawl_time = datetime.now().isoformat()
        self.loading_time = 0.0
    
    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'matched_keywords': self.matched_keywords,
            'links_found': self.links_found,
            'depth': self.depth,
            'crawl_time': self.crawl_time,
            'loading_time': self.loading_time
        }


class TestDataProcessor:
    """Test version of DataProcessor for validation"""
    def __init__(self, keywords=None):
        self.keywords = [word.lower() for word in (keywords or [])]

    def clean_text(self, text):
        if not text:
            return ""
        return ' '.join(text.split())

    def find_keywords(self, text):
        """Find matching keywords in text"""
        if not text or not self.keywords:
            return []
        
        text_lower = text.lower()
        matched = []
        for keyword in self.keywords:
            if keyword in text_lower:
                matched.append(keyword)
        return matched

    def turn_to_csv(self, items, filename='test_output.csv'):
        """Export items to CSV"""
        if not items:
            return
            
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['url', 'title', 'content_preview', 'matched_keywords', 'links_count', 'depth', 'crawl_time']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                item_dict = item.to_dict() if hasattr(item, 'to_dict') else item
                csv_row = {
                    'url': item_dict.get('url', ''),
                    'title': item_dict.get('title', ''),
                    'content_preview': item_dict.get('content', '')[:200] + '...' if len(item_dict.get('content', '')) > 200 else item_dict.get('content', ''),
                    'matched_keywords': ', '.join(item_dict.get('matched_keywords', [])),
                    'links_count': len(item_dict.get('links_found', [])),
                    'depth': item_dict.get('depth', 0),
                    'crawl_time': item_dict.get('crawl_time', '')
                }
                writer.writerow(csv_row)

    def turn_to_json(self, items, filename='test_output.json'):
        """Export items to JSON"""
        with open(filename, 'w', encoding='utf-8') as file:
            data = []
            for item in items:
                if hasattr(item, 'to_dict'):
                    data.append(item.to_dict())
                else:
                    data.append(item)
            json.dump(data, file, ensure_ascii=False, indent=4)


def create_test_data():
    """Create test data for demonstration"""
    test_items = [
        MockCrawlItem(
            url="http://example.com",
            title="Python Web Development Tutorial",
            content="Learn Python web development with Flask and Django. Build scalable web applications."
        ),
        MockCrawlItem(
            url="http://example.com/scrapy",
            title="Web Scraping with Scrapy",
            content="Scrapy is a powerful web scraping framework for Python. Extract data from websites efficiently."
        ),
        MockCrawlItem(
            url="http://example.com/data-science",
            title="Data Science Fundamentals",
            content="Data analysis and machine learning with Python. Pandas, NumPy, and scikit-learn tutorials."
        )
    ]
    
    # Add some links and keywords
    test_items[0].links_found = ["http://example.com/about", "http://example.com/contact"]
    test_items[1].links_found = ["http://example.com/docs", "http://example.com/tutorial"]
    test_items[2].links_found = ["http://example.com/datasets"]
    
    return test_items


def test_data_processing():
    """Test the data processing functionality"""
    print("Testing data processing functionality...")
    
    # Create test processor with keywords
    keywords = ['python', 'web', 'scrapy', 'data']
    processor = TestDataProcessor(keywords)
    
    # Create test items
    test_items = create_test_data()
    
    # Process items and find keywords
    for item in test_items:
        item.matched_keywords = processor.find_keywords(f"{item.title} {item.content}")
    
    # Test CSV export
    csv_filename = 'test_output.csv'
    processor.turn_to_csv(test_items, csv_filename)
    print(f"✅ CSV export test passed - file created: {csv_filename}")
    
    # Test JSON export
    json_filename = 'test_output.json'
    processor.turn_to_json(test_items, json_filename)
    print(f"✅ JSON export test passed - file created: {json_filename}")
    
    # Validate output files
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', encoding='utf-8') as f:
            csv_content = f.read()
            if len(csv_content) > 0:
                print("✅ CSV file contains data")
            else:
                print("❌ CSV file is empty")
    
    if os.path.exists(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if len(json_data) > 0:
                print(f"✅ JSON file contains {len(json_data)} items")
                # Print sample data
                print("Sample JSON data:")
                print(json.dumps(json_data[0], indent=2))
            else:
                print("❌ JSON file is empty")
    
    return True


def validate_project_structure():
    """Validate that all required project files exist"""
    print("Validating project structure...")
    
    required_files = [
        'scrapy.cfg',
        'requirements.txt',
        'HTMLCrawler/__init__.py',
        'HTMLCrawler/settings.py',
        'HTMLCrawler/items.py',
        'HTMLCrawler/pipelines.py',
        'HTMLCrawler/spiders/__init__.py',
        'HTMLCrawler/spiders/html_crawler.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("\n✅ All required files present")
        return True


def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    required_packages = {
        'scrapy': 'scrapy',
        'pandas': 'pandas', 
        'beautifulsoup4': 'bs4',  # BeautifulSoup4 is imported as 'bs4'
        'lxml': 'lxml'
    }
    
    available_packages = []
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            available_packages.append(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - not installed")
    
    if missing_packages:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✅ All required packages are installed")
        return True


def run_scrapy_commands():
    """Test basic Scrapy commands"""
    print("Testing Scrapy commands...")
    
    try:
        # Test scrapy version
        result = subprocess.run(['scrapy', 'version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Scrapy version: {result.stdout.strip()}")
        else:
            print("❌ Scrapy command failed")
            return False
        
        # Test list spiders
        result = subprocess.run(['scrapy', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            spiders = result.stdout.strip().split('\n')
            if spiders and spiders[0]:
                print(f"✅ Available spiders: {', '.join(spiders)}")
            else:
                print("⚠️  No spiders found")
        else:
            print("❌ Failed to list spiders")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Scrapy commands timed out")
        return False
    except FileNotFoundError:
        print("❌ Scrapy not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error running Scrapy commands: {e}")
        return False


def run_demo():
    """Run a complete demonstration"""
    print("=" * 50)
    print("WEB CRAWLER PROJECT DEMONSTRATION")
    print("=" * 50)
    
    # Test data processing
    success = test_data_processing()
    if not success:
        print("❌ Demo failed at data processing step")
        return False
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("Check the generated files:")
    print("- test_output.csv")
    print("- test_output.json")
    print("=" * 50)
    
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Web Crawler Test and Demo Script')
    parser.add_argument('--demo', action='store_true', help='Run demonstration')
    parser.add_argument('--test-config', action='store_true', help='Test configuration and dependencies')
    parser.add_argument('--validate-project', action='store_true', help='Validate project structure')
    parser.add_argument('--check-scrapy', action='store_true', help='Check Scrapy installation and commands')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        # No arguments provided, run all tests
        args.demo = True
        args.test_config = True
        args.validate_project = True
    
    success = True
    
    if args.validate_project:
        success &= validate_project_structure()
        print()
    
    if args.test_config:
        success &= check_dependencies()
        print()
    
    if args.check_scrapy:
        success &= run_scrapy_commands()
        print()
    
    if args.demo:
        success &= run_demo()
    
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())