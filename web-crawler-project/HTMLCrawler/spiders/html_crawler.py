import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse
from HTMLCrawler.items import CrawlItem


class KeywordHTMLCrawler(CrawlSpider):
    """
    A comprehensive web crawler that extracts content based on keywords.
    Can be configured for different websites and keyword sets.
    """
    name = 'keyword_html_crawler'
    
    # Default configuration - can be overridden via command line or settings
    allowed_domains = ['quotes.toscrape.com']  # Safe test site
    start_urls = ['http://quotes.toscrape.com']
    
    # Crawling rules
    rules = (
        Rule(
            LinkExtractor(
                allow=r'.*',  # Allow all links by default
                deny=r'(\.pdf|\.doc|\.zip|\.jpg|\.png|\.gif)$',  # Exclude files
            ), 
            callback='parse_item', 
            follow=True
        ),
    )
    
    # Custom settings that can be overridden
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }
    
    def __init__(self, keywords=None, max_depth=3, target_domain=None, start_url=None, 
                 use_deepseek=None, use_ai_keywords=None, *args, **kwargs):
        super(KeywordHTMLCrawler, self).__init__(*args, **kwargs)
        
        # Configure keywords for search
        if keywords:
            if isinstance(keywords, str):
                self.keywords = [k.strip().lower() for k in keywords.split(',')]
            else:
                self.keywords = [k.lower() for k in keywords]
        else:
            self.keywords = ['python', 'web', 'scrapy', 'data']  # Default keywords
        
        # Configure crawling parameters
        self.max_depth = int(max_depth)
        self.filter_by_keywords = True  # Only keep pages with matching keywords
        
        # Configure DeepSeek AI integration
        self.use_deepseek = use_deepseek == 'true' if use_deepseek else True
        self.use_ai_keywords = use_ai_keywords == 'true' if use_ai_keywords else False
        
        # Configure target domain and URL if provided
        if target_domain:
            self.allowed_domains = [target_domain]
        if start_url:
            self.start_urls = [start_url]
        
        self.logger.info(f"Initialized crawler with keywords: {self.keywords}")
        self.logger.info(f"Target domains: {self.allowed_domains}")
        self.logger.info(f"Start URLs: {self.start_urls}")
        self.logger.info(f"DeepSeek AI enabled: {self.use_deepseek}")
        self.logger.info(f"AI keyword extraction enabled: {self.use_ai_keywords}")
    
    def start_requests(self):
        """Generate initial requests with timing information"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_item,
                meta={'start_time': time.time(), 'depth': 0}
            )
    
    def parse_item(self, response):
        """Parse each page and extract relevant information"""
        start_time = response.meta.get('start_time', time.time())
        loading_time = time.time() - start_time
        depth = response.meta.get('depth', 0)
        
        # Create item with basic information
        item = CrawlItem()
        item['url'] = response.url
        item['depth'] = depth
        item['loading_time'] = loading_time
        item['crawl_time'] = datetime.now().isoformat()
        
        # Extract title
        title = response.xpath('//title/text()').get()
        item['title'] = self.clean_text(title) if title else ''
        
        # Extract main content (excluding script and style tags)
        content_selectors = [
            '//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
            '//main//text()',
            '//article//text()',
            '//div[@class*="content"]//text()',
            '//p//text()'
        ]
        
        all_text = []
        for selector in content_selectors:
            texts = response.xpath(selector).getall()
            if texts:
                all_text.extend(texts)
                break  # Use first successful selector
        
        item['content'] = self.clean_text(' '.join(all_text))
        
        # Extract all links found on the page
        links = response.xpath('//a/@href').getall()
        absolute_links = []
        for link in links:
            absolute_url = urljoin(response.url, link)
            if self.is_valid_url(absolute_url):
                absolute_links.append(absolute_url)
        
        item['links_found'] = absolute_links[:50]  # Limit to first 50 links
        
        yield item
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Remove extra whitespace, newlines, and tabs
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text)
        return text.strip()
    
    def is_valid_url(self, url):
        """Check if URL is valid and within allowed domains"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if domain is allowed
            if self.allowed_domains:
                for domain in self.allowed_domains:
                    if domain in parsed.netloc:
                        return True
                return False
            
            return True
        except:
            return False


class SimpleHTMLCrawler(scrapy.Spider):
    """
    A simpler spider for basic HTML crawling without following links.
    Good for targeted single-page or limited crawling.
    """
    name = 'simple_html_crawler'
    
    def __init__(self, urls=None, keywords=None, *args, **kwargs):
        super(SimpleHTMLCrawler, self).__init__(*args, **kwargs)
        
        if urls:
            if isinstance(urls, str):
                self.start_urls = [u.strip() for u in urls.split(',')]
            else:
                self.start_urls = urls
        else:
            self.start_urls = ['http://quotes.toscrape.com']
        
        if keywords:
            if isinstance(keywords, str):
                self.keywords = [k.strip().lower() for k in keywords.split(',')]
            else:
                self.keywords = [k.lower() for k in keywords]
        else:
            self.keywords = ['python', 'web', 'data']
        
        self.filter_by_keywords = False  # Don't filter by default for simple crawler
    
    def parse(self, response):
        """Parse a single page"""
        item = CrawlItem()
        item['url'] = response.url
        item['title'] = response.xpath('//title/text()').get(default='').strip()
        
        # Extract text content
        content_text = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style)]').getall()
        item['content'] = ' '.join([t.strip() for t in content_text if t.strip()])
        
        # Extract links
        links = response.xpath('//a/@href').getall()
        item['links_found'] = [urljoin(response.url, link) for link in links[:20]]
        
        # Set other fields
        item['depth'] = 0
        item['crawl_time'] = datetime.now().isoformat()
        item['loading_time'] = 0.0
        
        yield item


# Legacy DataProcessor class for backward compatibility
class DataProcessor:
    """
    Legacy data processor class - functionality now handled by pipelines.
    Kept for backward compatibility.
    """
    def __init__(self, keywords=None):
        self.keywords = [word.lower() for word in (keywords or [])]

    def clean_text(self, text):
        return ' '.join(text.split()) if text else ''

    def turn_to_csv(self, items, filename='output.csv'):
        import csv
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            if not items:
                return
            
            # Handle both dict and CrawlItem objects
            fieldnames = list(items[0].keys()) if isinstance(items[0], dict) else ['url', 'title', 'content', 'matched_keywords']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                if hasattr(item, 'to_dict'):
                    writer.writerow(item.to_dict())
                else:
                    writer.writerow(item)

    def turn_to_json(self, items, filename='output.json'):
        import json
        with open(filename, 'w', encoding='utf-8') as file:
            data = []
            for item in items:
                if hasattr(item, 'to_dict'):
                    data.append(item.to_dict())
                else:
                    data.append(dict(item) if hasattr(item, 'keys') else item)
            json.dump(data, file, ensure_ascii=False, indent=4)


# Crawler Manager for handling multiple crawlers
class CrawlerManager:
    """
    Manager class for handling multiple crawler instances.
    Useful for coordinating multiple crawling tasks.
    """
    def __init__(self):
        self.crawlers = []
        self.results = []
    
    def add_crawler_config(self, spider_name, **kwargs):
        """Add a crawler configuration"""
        config = {
            'spider_name': spider_name,
            'settings': kwargs
        }
        self.crawlers.append(config)
        return config
    
    def get_crawler_configs(self):
        """Get all crawler configurations"""
        return self.crawlers
    
    def clear_crawlers(self):
        """Clear all crawler configurations"""
        self.crawlers = []