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


def _save_deepseek_key(api_key: str):
    """Persist API key in user home with restrictive permissions"""
    key_path = os.path.expanduser("~/.deepseek_api_key")
    try:
        with open(key_path, 'w') as f:
            f.write(api_key.strip())
        # Restrict permissions (best-effort; may be ignored on some OS)
        try:
            os.chmod(key_path, 0o600)
        except PermissionError:
            pass
        print(f"Saved DeepSeek API key to {key_path}")
    except Exception as e:
        print(f"⚠️  Could not save DeepSeek API key to {key_path}: {e}")


def _load_saved_deepseek_key():
    """Load saved key if present"""
    key_path = os.path.expanduser("~/.deepseek_api_key")
    if os.getenv('DEEPSEEK_API_KEY'):
        return os.getenv('DEEPSEEK_API_KEY')
    if os.path.isfile(key_path):
        try:
            with open(key_path, 'r') as f:
                key = f.read().strip()
                if key:
                    return key
        except Exception:
            return None
    return None

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)


def _parse_list_arg(value):
    if not value:
        return None
    if isinstance(value, str) and ',' in value:
        return [v.strip() for v in value.split(',') if v.strip()]
    if isinstance(value, str):
        return [value]
    return value


def _apply_deepseek_env(deepseek_api_key, save_key):
    if deepseek_api_key and save_key:
        _save_deepseek_key(deepseek_api_key)
    key_to_use = deepseek_api_key or _load_saved_deepseek_key()
    if key_to_use:
        os.environ['DEEPSEEK_API_KEY'] = key_to_use
        return True
    return False


def _enable_playwright(settings, use_playwright):
    if not use_playwright:
        return False
    try:
        import scrapy_playwright  # noqa: F401
    except ImportError:
        print("⚠️  scrapy-playwright not installed. Install requirements to enable Playwright.")
        return False

    settings.set('DOWNLOAD_HANDLERS', {
        'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
    })
    settings.set('PLAYWRIGHT_BROWSER_TYPE', 'chromium')
    # Prefer asyncio reactor when using playwright so rendering hooks work
    settings.set('TWISTED_REACTOR', 'twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    return True


def _select_pipelines(settings, use_deepseek, deepseek_available):
    if use_deepseek and deepseek_available:
        settings.set('ITEM_PIPELINES', {
            'HTMLCrawler.pipelines.KeywordMatchingPipeline': 300,
            'HTMLCrawler.pipelines.JournalistFilterPipeline': 325,
            'HTMLCrawler.pipelines.DeepSeekAnalysisPipeline': 350,
            'HTMLCrawler.pipelines.EnhancedDataExportPipeline': 400,
        })
        print("🤖 DeepSeek AI analysis enabled")
    else:
        settings.set('ITEM_PIPELINES', {
            'HTMLCrawler.pipelines.KeywordMatchingPipeline': 300,
            'HTMLCrawler.pipelines.JournalistFilterPipeline': 325,
            'HTMLCrawler.pipelines.DataExportPipeline': 400,
        })
        if use_deepseek:
            print("⚠️  DeepSeek requested but API key not found. Using basic analysis.")


def run_keyword_crawler(keywords=None, domain=None, start_url=None, max_depth=3, output_dir="output",
                       use_deepseek=False, deepseek_api_key=None, ai_keywords=False,
                       save_deepseek_key=False, filter_by_keywords=True, allow_all_domains=False,
                       use_playwright=False, close_timeout=None, close_pagecount=None,
                       close_itemcount=None, jobdir=None):
    """Run the keyword-based HTML crawler."""
    os.makedirs(output_dir, exist_ok=True)
    deepseek_available = _apply_deepseek_env(deepseek_api_key, save_deepseek_key)

    settings = get_project_settings()
    playwright_enabled = _enable_playwright(settings, use_playwright)
    settings.set('DEPTH_LIMIT', max_depth)
    settings.set('ROBOTSTXT_OBEY', True)
    if close_timeout:
        settings.set('CLOSESPIDER_TIMEOUT', close_timeout)
    if close_pagecount:
        settings.set('CLOSESPIDER_PAGECOUNT', close_pagecount)
    if close_itemcount:
        settings.set('CLOSESPIDER_ITEMCOUNT', close_itemcount)
    if jobdir:
        settings.set('JOBDIR', jobdir)
    _select_pipelines(settings, use_deepseek, deepseek_available)

    process = CrawlerProcess(settings)

    spider_kwargs = {
        'max_depth': max_depth,
        'use_deepseek': 'true' if use_deepseek else 'false',
        'use_ai_keywords': 'true' if ai_keywords else 'false',
        'use_playwright': 'true' if use_playwright else 'false',
        'filter_by_keywords': 'true' if filter_by_keywords else 'false',
        'output_dir': output_dir
    }
    if keywords:
        spider_kwargs['keywords'] = keywords
    if domain:
        spider_kwargs['target_domain'] = domain
    if start_url:
        spider_kwargs['start_url'] = start_url
    if allow_all_domains:
        spider_kwargs['allow_all_domains'] = 'true'

    process.crawl('keyword_html_crawler', **spider_kwargs)

    print("Starting keyword crawler...")
    print(f"Keywords: {keywords or 'python,web,scrapy,data'}")
    print(f"Target domain: {domain or 'quotes.toscrape.com'}")
    print(f"Start URLs: {start_url or 'http://quotes.toscrape.com'}")
    print(f"Max depth: {max_depth}")
    print(f"Output directory: {output_dir}")
    print(f"Playwright enabled: {playwright_enabled}")

    process.start()


def run_simple_crawler(urls=None, keywords=None, output_dir="output"):
    """
    Run the simple HTML crawler (single page)
    
    Args:
        urls (str): Comma-separated list of URLs to crawl
        keywords (str): Comma-separated list of keywords to search for
        output_dir (str): Directory to save output files
    """
    os.makedirs(output_dir, exist_ok=True)
    settings = get_project_settings()
    playwright_enabled = _enable_playwright(settings, os.getenv('USE_PLAYWRIGHT_SIMPLE') == 'true')
    process = CrawlerProcess(settings)

    spider_kwargs = {
        'output_dir': output_dir,
        'filter_by_keywords': 'false',
        'use_playwright': 'true' if os.getenv('USE_PLAYWRIGHT_SIMPLE') == 'true' else 'false'
    }
    if urls:
        spider_kwargs['urls'] = urls
    if keywords:
        spider_kwargs['keywords'] = keywords

    process.crawl('simple_html_crawler', **spider_kwargs)

    print("Starting simple crawler...")
    print(f"URLs: {urls or 'http://quotes.toscrape.com'}")
    print(f"Keywords: {keywords or 'python,web,data'}")
    print(f"Output directory: {output_dir}")
    print(f"Playwright enabled: {playwright_enabled}")

    process.start()


def run_nhc_forecast_discussion(archive_url=None, year='2025', output_dir="output",
                                use_deepseek=False, deepseek_api_key=None, save_deepseek_key=False,
                                use_playwright=False, close_timeout=None, close_pagecount=None,
                                close_itemcount=None, jobdir=None):
    """
    Run the dedicated NHC forecast discussion spider.
    """
    os.makedirs(output_dir, exist_ok=True)
    deepseek_available = _apply_deepseek_env(deepseek_api_key, save_deepseek_key)

    settings = get_project_settings()
    playwright_enabled = _enable_playwright(settings, use_playwright)
    if close_timeout:
        settings.set('CLOSESPIDER_TIMEOUT', close_timeout)
    if close_pagecount:
        settings.set('CLOSESPIDER_PAGECOUNT', close_pagecount)
    if close_itemcount:
        settings.set('CLOSESPIDER_ITEMCOUNT', close_itemcount)
    if jobdir:
        settings.set('JOBDIR', jobdir)
    _select_pipelines(settings, use_deepseek, deepseek_available)
    process = CrawlerProcess(settings)

    spider_kwargs = {
        'archive_url': archive_url,
        'year': year,
        'use_playwright': 'true' if use_playwright else 'false',
    }

    process.crawl('nhc_forecast_discussion', **spider_kwargs)

    print(f"Starting NHC forecast discussion crawler for year {year}...")
    print(f"Archive URL: {archive_url or f'https://www.nhc.noaa.gov/archive/{year}/'}")
    print(f"Output directory: {output_dir}")
    print(f"Playwright enabled: {playwright_enabled}")

    process.start()


def run_keyword_js_crawler(keywords=None, domain=None, start_url=None, max_depth=3, output_dir="output",
                           use_deepseek=False, deepseek_api_key=None, ai_keywords=False,
                           save_deepseek_key=False, filter_by_keywords=True, allow_all_domains=False,
                           use_playwright=True, close_timeout=None, close_pagecount=None,
                           close_itemcount=None, jobdir=None):
    """Run the Playwright-enabled keyword JS crawler."""
    os.makedirs(output_dir, exist_ok=True)
    deepseek_available = _apply_deepseek_env(deepseek_api_key, save_deepseek_key)

    settings = get_project_settings()
    playwright_enabled = _enable_playwright(settings, use_playwright)
    if close_timeout:
        settings.set('CLOSESPIDER_TIMEOUT', close_timeout)
    if close_pagecount:
        settings.set('CLOSESPIDER_PAGECOUNT', close_pagecount)
    if close_itemcount:
        settings.set('CLOSESPIDER_ITEMCOUNT', close_itemcount)
    if jobdir:
        settings.set('JOBDIR', jobdir)
    _select_pipelines(settings, use_deepseek, deepseek_available)

    process = CrawlerProcess(settings)

    spider_kwargs = {
        'max_depth': max_depth,
        'use_deepseek': 'true' if use_deepseek else 'false',
        'use_ai_keywords': 'true' if ai_keywords else 'false',
        'use_playwright': 'true' if use_playwright else 'false',
        'filter_by_keywords': 'true' if filter_by_keywords else 'false',
        'output_dir': output_dir
    }
    if keywords:
        spider_kwargs['keywords'] = keywords
    if domain:
        spider_kwargs['target_domain'] = domain
    if start_url:
        spider_kwargs['start_url'] = start_url
    if allow_all_domains:
        spider_kwargs['allow_all_domains'] = 'true'

    process.crawl('keyword_js_crawler', **spider_kwargs)

    print("Starting keyword JS crawler...")
    print(f"Keywords: {keywords or 'python,web,scrapy,data'}")
    print(f"Target domain: {domain or 'quotes.toscrape.com'}")
    print(f"Start URLs: {start_url or 'http://quotes.toscrape.com/js/'}")
    print(f"Max depth: {max_depth}")
    print(f"Output directory: {output_dir}")
    print(f"Playwright enabled: {playwright_enabled}")

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
        choices=['keyword_html_crawler', 'keyword_js_crawler', 'simple_html_crawler', 'nhc_forecast_discussion'],
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
        '--archive-url',
        type=str,
        help='For NHC spider: archive URL (e.g., "https://www.nhc.noaa.gov/archive/2025/")'
    )
    parser.add_argument(
        '--year',
        type=str,
        default='2025',
        help='For NHC spider: archive year (default: 2025)'
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
    parser.add_argument(
        '--use-playwright',
        action='store_true',
        help='Render pages with Playwright (for heavy JS sites; requires scrapy-playwright installed)'
    )
    parser.add_argument(
        '--jobdir',
        type=str,
        help='Persist crawl state for resume (Scrapy JOBDIR)'
    )
    parser.add_argument(
        '--close-timeout',
        type=int,
        help='Stop crawl after N seconds (CLOSESPIDER_TIMEOUT)'
    )
    parser.add_argument(
        '--close-pagecount',
        type=int,
        help='Stop crawl after N pages (CLOSESPIDER_PAGECOUNT)'
    )
    parser.add_argument(
        '--close-itemcount',
        type=int,
        help='Stop crawl after N items (CLOSESPIDER_ITEMCOUNT)'
    )
    parser.add_argument(
        '--no-keyword-filter',
        action='store_true',
        help='Do not drop pages when keywords are missing (general-purpose crawling)'
    )
    parser.add_argument(
        '--allow-all-domains',
        action='store_true',
        help='Disable allowed_domains restriction to follow external links (use carefully)'
    )
    parser.add_argument(
        '--save-deepseek-key',
        action='store_true',
        help='Store the provided DeepSeek API key in ~/.deepseek_api_key for reuse'
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
                ai_keywords=args.ai_keywords,
                filter_by_keywords=not args.no_keyword_filter,
                allow_all_domains=args.allow_all_domains,
                use_playwright=args.use_playwright,
                save_deepseek_key=args.save_deepseek_key,
                close_timeout=args.close_timeout,
                close_pagecount=args.close_pagecount,
                close_itemcount=args.close_itemcount,
                jobdir=args.jobdir
            )
        elif args.spider == 'keyword_js_crawler':
            run_keyword_js_crawler(
                keywords=args.keywords,
                domain=args.domain,
                start_url=args.start_url,
                max_depth=args.max_depth,
                output_dir=args.output_dir,
                use_deepseek=args.use_deepseek,
                deepseek_api_key=args.deepseek_api_key,
                ai_keywords=args.ai_keywords,
                filter_by_keywords=not args.no_keyword_filter,
                allow_all_domains=args.allow_all_domains,
                use_playwright=args.use_playwright,
                save_deepseek_key=args.save_deepseek_key,
                close_timeout=args.close_timeout,
                close_pagecount=args.close_pagecount,
                close_itemcount=args.close_itemcount,
                jobdir=args.jobdir
            )
        elif args.spider == 'simple_html_crawler':
            run_simple_crawler(
                urls=args.urls,
                keywords=args.keywords,
                output_dir=args.output_dir
            )
        elif args.spider == 'nhc_forecast_discussion':
            run_nhc_forecast_discussion(
                archive_url=args.archive_url,
                year=args.year,
                output_dir=args.output_dir,
                use_deepseek=args.use_deepseek,
                deepseek_api_key=args.deepseek_api_key,
                save_deepseek_key=args.save_deepseek_key,
                use_playwright=args.use_playwright,
                close_timeout=args.close_timeout,
                close_pagecount=args.close_pagecount,
                close_itemcount=args.close_itemcount,
                jobdir=args.jobdir
            )
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
    except Exception as e:
        print(f"Error running crawler: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
