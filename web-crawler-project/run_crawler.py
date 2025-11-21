#!/usr/bin/env python3
"""
Web Crawler Example Usage Script

This script demonstrates how to use the HTML crawler project
with different configurations and settings.

Usage:
    python run_crawler.py --help
    python run_crawler.py --spider keyword_html_crawler --keywords "python,web,scrapy"
    python run_crawler.py --spider simple_html_crawler --urls "http://example.com"
"""

import argparse
import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)


def run_keyword_crawler(keywords=None, domain=None, start_url=None, max_depth=3, output_dir="output"):
    """
    Run the keyword-based HTML crawler
    
    Args:
        keywords (str): Comma-separated list of keywords to search for
        domain (str): Target domain to crawl
        start_url (str): Starting URL for crawling
        max_depth (int): Maximum crawl depth
        output_dir (str): Directory to save output files
    """
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Configure custom settings
    settings.set('DEPTH_LIMIT', max_depth)
    settings.set('ROBOTSTXT_OBEY', True)
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
def run_keyword_crawler(keywords=None, domain=None, start_url=None, max_depth=3, output_dir="output", 
                       use_deepseek=False, deepseek_api_key=None, ai_keywords=False):
    """
    Run the keyword-based HTML crawler
    
    Args:
        keywords (str): Comma-separated list of keywords to search for
        domain (str): Target domain to crawl
        start_url (str): Starting URL for crawling
        max_depth (int): Maximum crawl depth
        output_dir (str): Directory to save output files
        use_deepseek (bool): Enable DeepSeek AI analysis
        deepseek_api_key (str): DeepSeek API key
        ai_keywords (bool): Use AI for keyword extraction
    """
    # Set DeepSeek API key if provided
    if deepseek_api_key:
        os.environ['DEEPSEEK_API_KEY'] = deepseek_api_key
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Configure custom settings
    settings.set('DEPTH_LIMIT', max_depth)
    settings.set('ROBOTSTXT_OBEY', True)
    
    # Configure pipelines based on DeepSeek availability
    if use_deepseek and (deepseek_api_key or os.getenv('DEEPSEEK_API_KEY')):
        # Use enhanced pipelines with AI analysis
        settings.set('ITEM_PIPELINES', {
            'HTMLCrawler.pipelines.KeywordMatchingPipeline': 300,
            'HTMLCrawler.pipelines.DeepSeekAnalysisPipeline': 350,
            'HTMLCrawler.pipelines.EnhancedDataExportPipeline': 400,
        })
        print("🤖 DeepSeek AI analysis enabled")
    else:
        # Use basic pipelines
        settings.set('ITEM_PIPELINES', {
            'HTMLCrawler.pipelines.KeywordMatchingPipeline': 300,
            'HTMLCrawler.pipelines.DataExportPipeline': 400,
        })
        if use_deepseek:
            print("⚠️  DeepSeek requested but API key not found. Using basic analysis.")
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Spider arguments
    spider_kwargs = {}
    if keywords:
        spider_kwargs['keywords'] = keywords
    if domain:
        spider_kwargs['target_domain'] = domain
    if start_url:
        spider_kwargs['start_url'] = start_url
    spider_kwargs['max_depth'] = max_depth
    spider_kwargs['use_deepseek'] = 'true' if use_deepseek else 'false'
    spider_kwargs['use_ai_keywords'] = 'true' if ai_keywords else 'false'
    
    # Add spider to process
    process.crawl('keyword_html_crawler', **spider_kwargs)
    
    print(f"Starting keyword crawler...")
    print(f"Keywords: {keywords or 'python,web,scrapy,data'}")
    print(f"Target domain: {domain or 'quotes.toscrape.com'}")
    print(f"Start URL: {start_url or 'http://quotes.toscrape.com'}")
    print(f"Max depth: {max_depth}")
    print(f"Output directory: {output_dir}")
    
    # Start crawling
    process.start()


def run_simple_crawler(urls=None, keywords=None, output_dir="output"):
    """
    Run the simple HTML crawler (single page)
    
    Args:
        urls (str): Comma-separated list of URLs to crawl
        keywords (str): Comma-separated list of keywords to search for
        output_dir (str): Directory to save output files
    """
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Spider arguments
    spider_kwargs = {}
    if urls:
        spider_kwargs['urls'] = urls
    if keywords:
        spider_kwargs['keywords'] = keywords
    
    # Add spider to process
    process.crawl('simple_html_crawler', **spider_kwargs)
    
    print(f"Starting simple crawler...")
    print(f"URLs: {urls or 'http://quotes.toscrape.com'}")
    print(f"Keywords: {keywords or 'python,web,data'}")
    print(f"Output directory: {output_dir}")
    
    # Start crawling
    process.start()


def main():
    """Main function to parse arguments and run crawler"""
    parser = argparse.ArgumentParser(
        description='Web Crawler - Extract content from websites based on keywords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run keyword crawler with default settings
  python run_crawler.py
  
  # Run with custom keywords
  python run_crawler.py --keywords "python,machine learning,AI"
  
  # Run on specific domain
  python run_crawler.py --domain "example.com" --start-url "http://example.com"
  
  # Run simple crawler on specific URLs
  python run_crawler.py --spider simple_html_crawler --urls "http://example.com,http://test.com"
  
  # Limit crawl depth
  python run_crawler.py --max-depth 2 --keywords "web scraping"
        """
    )
    
    parser.add_argument(
        '--spider',
        choices=['keyword_html_crawler', 'simple_html_crawler'],
        default='keyword_html_crawler',
        help='Spider to use (default: keyword_html_crawler)'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        help='Comma-separated list of keywords to search for (e.g., "python,web,data")'
    )
    
    parser.add_argument(
        '--urls',
        type=str,
        help='Comma-separated list of URLs to crawl (for simple crawler)'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        help='Target domain to crawl (e.g., "example.com")'
    )
    
    parser.add_argument(
        '--start-url',
        type=str,
        help='Starting URL for crawling (e.g., "http://example.com")'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum crawl depth (default: 3)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--use-deepseek',
        action='store_true',
        help='Enable DeepSeek AI analysis (requires API key)'
    )
    
    parser.add_argument(
        '--deepseek-api-key',
        type=str,
        help='DeepSeek API key (or set DEEPSEEK_API_KEY environment variable)'
    )
    
    parser.add_argument(
        '--ai-keywords',
        action='store_true',
        help='Use AI for enhanced keyword extraction'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        if args.spider == 'keyword_html_crawler':
            run_keyword_crawler(
                keywords=args.keywords,
                domain=args.domain,
                start_url=args.start_url,
                max_depth=args.max_depth,
                output_dir=args.output_dir,
                use_deepseek=args.use_deepseek,
                deepseek_api_key=args.deepseek_api_key,
                ai_keywords=args.ai_keywords
            )
        elif args.spider == 'simple_html_crawler':
            run_simple_crawler(
                urls=args.urls,
                keywords=args.keywords,
                output_dir=args.output_dir
            )
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
    except Exception as e:
        print(f"Error running crawler: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())