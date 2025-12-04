# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
import os
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
try:
    from scrapy.exceptions import DropItem
except ImportError:
    # Fallback for when Scrapy is not available
    class DropItem(Exception):
        pass

try:
    from .deepseek_parser import DeepSeekParser, create_deepseek_parser
except ImportError:
    # Fallback when DeepSeek parser is not available
    DeepSeekParser = None
    create_deepseek_parser = None


class KeywordMatchingPipeline:
    """Pipeline to match keywords in the scraped content"""
    
    def __init__(self, keywords=None):
        self.keywords = keywords or []
        # Convert keywords to lowercase for case-insensitive matching
        self.keywords = [keyword.lower() for keyword in self.keywords]
    
    @classmethod
    def from_crawler(cls, crawler):
        # Get keywords from spider settings or custom settings
        keywords = crawler.spider.keywords if hasattr(crawler.spider, 'keywords') else []
        return cls(keywords=keywords)
    
    def process_item(self, item, spider):
        if not self.keywords:
            return item
            
        # Combine title and content for keyword matching
        text_to_search = f"{item.get('title', '')} {item.get('content', '')}".lower()
        
        # Find matching keywords
        matched_keywords = []
        for keyword in self.keywords:
            if keyword in text_to_search:
                matched_keywords.append(keyword)
        
        item['matched_keywords'] = matched_keywords
        
        # Only keep items that match at least one keyword (optional filter)
        if hasattr(spider, 'filter_by_keywords') and spider.filter_by_keywords:
            if not matched_keywords:
                raise DropItem(f"No matching keywords found in {item['url']}")
        
        return item


class JournalistFilterPipeline:
    """Pipeline with journalist-friendly filtering and normalization"""

    def _parse_date(self, date_str):
        """Best-effort date parsing using stdlib only"""
        if not date_str:
            return None
        # Try ISO-like formats first
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # Fallback to email-style parsing
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def process_item(self, item, spider):
        news_only = getattr(spider, 'news_only', False)
        recent_days = getattr(spider, 'recent_days', None)

        published_date_raw = item.get('published_date', '')
        parsed_date = self._parse_date(published_date_raw)

        # Enforce news-only mode: require a publish date hint
        if news_only and not parsed_date:
            raise DropItem(f"No publish date detected for {item.get('url')}")

        # Filter by recency if requested
        if recent_days:
            cutoff = datetime.now(tz=parsed_date.tzinfo if parsed_date else None) - timedelta(days=recent_days)
            if parsed_date:
                if parsed_date < cutoff:
                    raise DropItem(f"Out of recency window for {item.get('url')}")
            else:
                # If we cannot tell the date, drop in recency mode to avoid stale articles
                raise DropItem(f"Unknown publish date while recency filtering for {item.get('url')}")

        # Store normalized date string when available
        if parsed_date:
            item['published_date'] = parsed_date.isoformat()

        # Default lead text to first sentences if missing
        if not item.get('lead') and item.get('content'):
            first_sentences = re.split(r'(?<=[.!?])\\s+', item['content'])
            item['lead'] = ' '.join(first_sentences[:2]).strip()

        return item


class DataExportPipeline:
    """Pipeline to export data to CSV and JSON formats"""
    
    def __init__(self):
        self.items = []
        self.csv_file = None
        self.json_file = None
    
    def open_spider(self, spider):
        # Create output directory if it doesn't exist
        output_dir = getattr(spider, 'output_dir', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamped filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(output_dir, f'crawl_results_{timestamp}.csv')
        json_filename = os.path.join(output_dir, f'crawl_results_{timestamp}.json')
        
        # Open CSV file and write header
        self.csv_file = open(csv_filename, 'w', newline='', encoding='utf-8')
        fieldnames = [
            'url',
            'canonical_url',
            'source_domain',
            'title',
            'author',
            'published_date',
            'lead',
            'content_preview',
            'quotes',
            'matched_keywords',
            'links_count',
            'word_count',
            'forecast_positions',
            'depth',
            'crawl_time'
        ]
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()
        
        # Store JSON filename for later use
        self.json_filename = json_filename
    
    def close_spider(self, spider):
        # Close CSV file
        if self.csv_file:
            self.csv_file.close()
        
        # Write JSON file
        if self.items:
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2, default=str)
    
    def process_item(self, item, spider):
        # Prepare item for CSV export
        csv_item = {
            'url': item.get('url', ''),
            'canonical_url': item.get('canonical_url', ''),
            'source_domain': item.get('source_domain', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'published_date': item.get('published_date', ''),
            'lead': item.get('lead', ''),
            'content_preview': self._truncate_content(item.get('content', '')),
            'quotes': ' | '.join(item.get('quotes', [])),
            'matched_keywords': ', '.join(item.get('matched_keywords', [])),
            'links_count': len(item.get('links_found', [])),
            'word_count': item.get('word_count', 0),
            'forecast_positions': item.get('forecast_positions', ''),
            'depth': item.get('depth', 0),
            'crawl_time': item.get('crawl_time', '')
        }
        
        # Write to CSV
        self.csv_writer.writerow(csv_item)
        
        # Store full item for JSON export
        self.items.append(dict(item))
        
        return item
    
    def _truncate_content(self, content, max_length=200):
        """Truncate content for CSV preview"""
        if not content:
            return ''
        # Remove extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content.strip())
        if len(content) > max_length:
            return content[:max_length] + '...'
        return content


class DuplicateFilterPipeline:
    """Pipeline to filter out duplicate URLs"""
    
    def __init__(self):
        self.urls_seen = set()
    
    def process_item(self, item, spider):
        url = item.get('url')
        if url in self.urls_seen:
            raise DropItem(f"Duplicate item found: {url}")
        else:
            self.urls_seen.add(url)
            return item


class DeepSeekAnalysisPipeline:
    """Pipeline that uses DeepSeek AI for intelligent content analysis"""
    
    def __init__(self):
        self.parser = None
        self.enabled = False
    
    def open_spider(self, spider):
        """Initialize DeepSeek parser when spider opens"""
        try:
            if DeepSeekParser:
                self.parser = create_deepseek_parser()
                self.enabled = self.parser.is_enabled()
                
                if self.enabled:
                    spider.logger.info("DeepSeek AI analysis pipeline enabled")
                else:
                    spider.logger.warning("DeepSeek API key not found. AI analysis disabled.")
            else:
                spider.logger.warning("DeepSeek parser not available. Install openai package.")
        except Exception as e:
            spider.logger.error(f"Failed to initialize DeepSeek parser: {e}")
            self.enabled = False
    
    def process_item(self, item, spider):
        """Process item with DeepSeek AI analysis"""
        if not self.enabled or not self.parser:
            return item
        
        try:
            # Get content for analysis
            content = item.get('content', '')
            title = item.get('title', '')
            url = item.get('url', '')
            
            if not content:
                return item
            
            # Perform AI analysis
            analysis = self.parser.parse_content(content, url, title)
            
            # Add analysis results to item
            item['ai_summary'] = analysis.get('summary', '')
            item['ai_entities'] = analysis.get('entities', [])
            item['ai_topics'] = analysis.get('topics', [])
            item['ai_sentiment'] = analysis.get('sentiment', 'neutral')
            item['ai_key_points'] = analysis.get('key_points', [])
            item['ai_structured_data'] = analysis.get('structured_data', {})
            item['ai_analysis_timestamp'] = analysis.get('analysis_timestamp', '')
            
            # Enhanced keyword extraction using AI
            if hasattr(spider, 'use_ai_keywords') and spider.use_ai_keywords:
                ai_keywords = self.parser.extract_keywords_ai(content)
                existing_keywords = item.get('matched_keywords', [])
                # Combine AI keywords with existing ones
                combined_keywords = list(set(existing_keywords + ai_keywords))
                item['ai_keywords'] = ai_keywords
                item['enhanced_keywords'] = combined_keywords
            
            spider.logger.info(f"DeepSeek analysis completed for {url}")
            
        except Exception as e:
            spider.logger.error(f"DeepSeek analysis failed for {item.get('url', 'unknown')}: {e}")
        
        return item


class EnhancedDataExportPipeline(DataExportPipeline):
    """Enhanced export pipeline that includes DeepSeek AI analysis results"""
    
    def process_item(self, item, spider):
        # Prepare enhanced item for CSV export
        csv_item = {
            'url': item.get('url', ''),
            'canonical_url': item.get('canonical_url', ''),
            'source_domain': item.get('source_domain', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'published_date': item.get('published_date', ''),
            'lead': item.get('lead', ''),
            'content_preview': self._truncate_content(item.get('content', '')),
            'quotes': ' | '.join(item.get('quotes', [])),
            'matched_keywords': ', '.join(item.get('matched_keywords', [])),
            'links_count': len(item.get('links_found', [])),
            'word_count': item.get('word_count', 0),
            'forecast_positions': item.get('forecast_positions', ''),
            'depth': item.get('depth', 0),
            'crawl_time': item.get('crawl_time', ''),
            # DeepSeek AI fields
            'ai_summary': item.get('ai_summary', ''),
            'ai_sentiment': item.get('ai_sentiment', ''),
            'ai_topics': ', '.join(item.get('ai_topics', [])),
            'ai_entities': ', '.join(item.get('ai_entities', [])),
            'ai_keywords': ', '.join(item.get('ai_keywords', [])),
        }
        
        # Write to CSV with enhanced fields
        if not hasattr(self, 'csv_writer_initialized'):
            # Update fieldnames to include AI analysis fields
            fieldnames = list(csv_item.keys())
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            self.csv_writer_initialized = True
        
        self.csv_writer.writerow(csv_item)
        
        # Store full item for JSON export (includes all AI analysis data)
        self.items.append(dict(item))
        
        return item
