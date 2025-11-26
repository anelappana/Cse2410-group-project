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
            follow=True,
            process_request='playwright_request'
        ),
    )
    
    # Custom settings that can be overridden
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }
    
    def __init__(self, keywords=None, max_depth=3, target_domain=None, start_url=None, 
                 use_deepseek=None, use_ai_keywords=None, news_only=None, recent_days=None,
                 filter_by_keywords=None, allow_all_domains=None, use_playwright=None, *args, **kwargs):
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
        self.filter_by_keywords = False if (filter_by_keywords == 'false' or filter_by_keywords is False) else True
        
        # Configure DeepSeek AI integration
        self.use_deepseek = use_deepseek == 'true' if use_deepseek else True
        self.use_ai_keywords = use_ai_keywords == 'true' if use_ai_keywords else False
        self.news_only = news_only == 'true' if news_only else False
        self.recent_days = int(recent_days) if recent_days else None
        self.use_playwright = use_playwright == 'true' if use_playwright else False
        
        # Configure target domain and URL if provided
        if allow_all_domains == 'true':
            self.allowed_domains = []
        elif target_domain:
            self.allowed_domains = [target_domain]
        if start_url:
            if isinstance(start_url, str) and ',' in start_url:
                self.start_urls = [u.strip() for u in start_url.split(',') if u.strip()]
            else:
                self.start_urls = [start_url]
        
        self.logger.info(f"Initialized crawler with keywords: {self.keywords}")
        self.logger.info(f"Target domains: {self.allowed_domains}")
        self.logger.info(f"Start URLs: {self.start_urls}")
        self.logger.info(f"DeepSeek AI enabled: {self.use_deepseek}")
        self.logger.info(f"AI keyword extraction enabled: {self.use_ai_keywords}")
        self.logger.info(f"News-only mode: {self.news_only}, recent_days: {self.recent_days}")
        self.logger.info(f"Playwright enabled: {self.use_playwright}")
    
    def start_requests(self):
        """Generate initial requests with timing information"""
        for url in self.start_urls:
            meta = {'start_time': time.time(), 'depth': 0}
            if self.use_playwright:
                meta['playwright'] = True
            yield scrapy.Request(url=url, callback=self.parse_item, meta=meta)
    
    def parse_item(self, response):
        """Parse each page and extract relevant information"""
        start_time = response.meta.get('start_time', time.time())
        loading_time = time.time() - start_time
        depth = response.meta.get('depth', 0)
        
        # Create item with basic information
        item = CrawlItem()
        item['url'] = response.url
        item['canonical_url'] = self.extract_canonical_url(response) or response.url
        item['source_domain'] = urlparse(response.url).netloc
        item['depth'] = depth
        item['loading_time'] = loading_time
        item['crawl_time'] = datetime.now().isoformat()
        
        # Extract title/headline
        title = response.xpath('//title/text()').get()
        headline = self.extract_headline(response)
        chosen_title = headline or title
        item['title'] = self.clean_text(chosen_title) if chosen_title else ''
        
        # Extract main content (excluding script and style tags)
        content_selectors = [
            '//article//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
            '//main//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
            '//div[contains(@class,"content")]//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
            '//body//p//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
            '//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]',
        ]
        
        all_text = []
        for selector in content_selectors:
            texts = response.xpath(selector).getall()
            if texts:
                all_text.extend(texts)
                break  # Use first successful selector
        
        item['content'] = self.clean_text(' '.join(all_text))
        item['word_count'] = len(item['content'].split()) if item['content'] else 0
        item['lead'] = self.extract_lead(item['content'])
        item['quotes'] = self.extract_quotes(item['content'])
        item['published_date'] = self.extract_published_date(response)
        item['author'] = self.extract_author(response)
        
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

    def extract_canonical_url(self, response):
        """Extract canonical URL when available"""
        canonical = response.xpath('//link[@rel="canonical"]/@href').get()
        return canonical

    def extract_headline(self, response):
        """Extract a likely headline for the article"""
        headline = response.xpath('//meta[@property="og:title"]/@content').get()
        if headline:
            return headline
        headline = response.xpath('//h1/text()').get()
        if headline:
            return headline
        return None

    def extract_published_date(self, response):
        """Try multiple strategies to grab the published/updated date"""
        date_selectors = [
            '//meta[@property="article:published_time"]/@content',
            '//meta[@name="pubdate"]/@content',
            '//meta[@name="publish-date"]/@content',
            '//meta[@name="date"]/@content',
            '//time/@datetime',
            '//time/text()'
        ]
        for selector in date_selectors:
            date_value = response.xpath(selector).get()
            if date_value:
                return self.clean_text(date_value)
        return ''

    def extract_author(self, response):
        """Extract author from common meta tags"""
        author_selectors = [
            '//meta[@name="author"]/@content',
            '//meta[@property="article:author"]/@content',
            '//a[@rel="author"]/text()',
            '//span[@class="author"]/text()'
        ]
        for selector in author_selectors:
            author = response.xpath(selector).get()
            if author:
                return self.clean_text(author)
        return ''

    def extract_lead(self, content, sentences=2):
        """Return the first couple of sentences as the lede"""
        if not content:
            return ''
        sentence_candidates = re.split(r'(?<=[.!?])\s+', content)
        lead_sentences = sentence_candidates[:sentences]
        return ' '.join(lead_sentences).strip()

    def extract_quotes(self, content, max_quotes=5):
        """Pull out quoted statements to help journalists find pull quotes"""
        if not content:
            return []
        quotes = re.findall(r'“([^”]+)”|"([^"]+)"', content)
        flat_quotes = []
        for q1, q2 in quotes:
            flat_quotes.append(q1 or q2)
        cleaned_quotes = [self.clean_text(q) for q in flat_quotes if q]
        # De-duplicate while preserving order
        seen = set()
        unique_quotes = []
        for quote in cleaned_quotes:
            if quote not in seen:
                seen.add(quote)
                unique_quotes.append(quote)
            if len(unique_quotes) >= max_quotes:
                break
        return unique_quotes

    def playwright_request(self, request):
        """Attach Playwright flag to requests when enabled"""
        if self.use_playwright:
            request.meta['playwright'] = True
        return request


class SimpleHTMLCrawler(scrapy.Spider):
    """
    A simpler spider for basic HTML crawling without following links.
    Good for targeted single-page or limited crawling.
    """
    name = 'simple_html_crawler'
    
    def __init__(self, urls=None, keywords=None, *args, **kwargs):
        super(SimpleHTMLCrawler, self).__init__(*args, **kwargs)
        # Allow pipelines to honor output_dir and filtering flags
        self.output_dir = kwargs.get('output_dir', 'output')
        
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
        
        # Don't drop pages for simple crawler
        self.filter_by_keywords = False  
    
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


class NHCForecastDiscussionSpider(scrapy.Spider):
    """
    Targeted spider to collect forecast discussions from NHC archive pages.
    """
    name = 'nhc_forecast_discussion'
    allowed_domains = ['www.nhc.noaa.gov', 'nhc.noaa.gov']

    def __init__(self, archive_url=None, year='2025', *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = archive_url or f'https://www.nhc.noaa.gov/archive/{year}/'
        self.start_urls = [base]
        self.year = str(year)
        self.archive_base = base if base.endswith('/') else base + '/'
        self.archive_path_prefix = f"/archive/{self.year}/"
        # Disable keyword filtering for this spider
        self.filter_by_keywords = False
        self._seen = set()

    def parse(self, response):
        """
        Find links that likely contain discussions and follow them.
        """
        if not self._is_html(response):
            return

        hrefs = response.xpath('//a/@href').getall()
        for href in hrefs:
            url = urljoin(response.url, href)
            if url in self._seen:
                continue
            if not self._is_same_archive(url) or self._is_binary(url):
                continue
            self._seen.add(url)
            if self._looks_like_discussion(url):
                yield scrapy.Request(url, callback=self.parse_discussion)
            else:
                yield scrapy.Request(url, callback=self.parse)

    def parse_discussion(self, response):
        """
        Extract the forecast discussion block from a storm page.
        """
        if not self._is_html(response):
            return

        item = CrawlItem()
        item['url'] = response.url
        item['source_domain'] = urlparse(response.url).netloc
        item['title'] = self.clean_text(response.xpath('//title/text()').get(default=''))
        item['canonical_url'] = response.xpath('//link[@rel="canonical"]/@href').get(default=response.url)
        item['matched_keywords'] = ['forecast discussion']

        raw_blocks = response.xpath('//pre/text()').getall()
        if not raw_blocks:
            raw_blocks = response.xpath('//div[contains(@id,"content") or contains(@class,"content")]//text()').getall()

        joined = ' '.join(list(raw_blocks)) if raw_blocks else ''
        full_text = self.clean_text(joined) if joined else ''
        item['content'] = self.extract_discussion_section(full_text)
        item['forecast_positions'] = self.extract_forecast_positions(full_text)
        item['lead'] = self._safe_extract_lead(item.get('content', ''))
        item['quotes'] = self._safe_extract_quotes(item.get('content', ''))
        item['word_count'] = len(item['content'].split()) if item['content'] else 0

        yield item

    def extract_discussion_section(self, text):
        if not text:
            return ''
        if not isinstance(text, str):
            text = ' '.join(list(text))
        try:
            lower = text.lower()
        except Exception:
            return ''
        start = lower.find('forecast discussion')
        if start == -1:
            return text
        tail = text[start:]
        for stop_marker in ['FORECAST POSITIONS AND MAX WINDS', 'NEXT ADVISORY', '$$']:
            idx = tail.upper().find(stop_marker)
            if idx != -1:
                tail = tail[:idx]
                break
        return tail.strip()

    def extract_forecast_positions(self, text: str) -> str:
        """Extract the FORECAST POSITIONS AND MAX WINDS block if present."""
        if not text:
            return ''
        if not isinstance(text, str):
            text = ' '.join(list(text))
        try:
            upper = text.upper()
        except Exception:
            return ''
        marker = 'FORECAST POSITIONS AND MAX WINDS'
        start = upper.find(marker)
        if start == -1:
            return ''
        tail = text[start:]
        # Stop at common end markers
        for stop in ['NEXT ADVISORY', '$$', 'FORECAST DISCUSSION']:
            idx = tail.upper().find(stop)
            if idx > 0:
                tail = tail[:idx]
                break
        # Normalize spacing
        lines = [line.strip() for line in tail.splitlines() if line.strip()]
        return ' | '.join(lines)

    def _is_same_archive(self, url: str) -> bool:
        """Keep navigation inside the chosen archive year, regardless of scheme."""
        parsed = urlparse(url)
        if not parsed.netloc.endswith('nhc.noaa.gov'):
            return False
        return parsed.path.startswith(self.archive_path_prefix)

    def _is_binary(self, url: str) -> bool:
        """Skip obvious binary resources to avoid xpath errors."""
        binary_ext = ('.zip', '.kmz', '.gz', '.tgz')
        return url.lower().endswith(binary_ext)

    def _is_html(self, response) -> bool:
        """Check if the response is HTML/text."""
        ctype = response.headers.get('Content-Type', b'').decode(errors='ignore').lower()
        return 'text/html' in ctype or 'application/xhtml+xml' in ctype

    def _looks_like_discussion(self, url: str) -> bool:
        """Heuristic for discussion/advisory pages inside the archive."""
        lowered = url.lower()
        keywords = ['discussion', 'discus', 'fstadv', 'fcstadv', 'public', 'adv']
        return any(k in lowered for k in keywords) and (lowered.endswith('.shtml') or lowered.endswith('.html') or '.shtml?' in lowered or '.html?' in lowered)

    def clean_text(self, text):
        """Shared text normalizer (trim, collapse whitespace, keep punctuation)."""
        if not text:
            return ''
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text)
        return text.strip()

    def _safe_extract_lead(self, content):
        try:
            return self.extract_lead(content)
        except Exception:
            return ''

    def _safe_extract_quotes(self, content):
        try:
            return self.extract_quotes(content)
        except Exception:
            return []
        
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
