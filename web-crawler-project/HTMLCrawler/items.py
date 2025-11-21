# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime
from typing import List


try:
    import scrapy
except ImportError:
    # Fallback when Scrapy is not available
    class Field:
        pass
    
    class Item(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    class scrapy:
        Field = Field
        Item = Item

class CrawlItem(scrapy.Item):
    # Define the fields for your item here
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    matched_keywords = scrapy.Field()
    links_found = scrapy.Field()
    depth = scrapy.Field()
    crawl_time = scrapy.Field()
    loading_time = scrapy.Field()
    
    # DeepSeek AI analysis fields
    ai_summary = scrapy.Field()
    ai_entities = scrapy.Field()
    ai_topics = scrapy.Field()
    ai_sentiment = scrapy.Field()
    ai_key_points = scrapy.Field()
    ai_structured_data = scrapy.Field()
    ai_analysis_timestamp = scrapy.Field()
    ai_keywords = scrapy.Field()
    enhanced_keywords = scrapy.Field()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.setdefault('matched_keywords', [])
        self.setdefault('links_found', [])
        self.setdefault('depth', 0)
        self.setdefault('crawl_time', datetime.now().isoformat())
        self.setdefault('loading_time', 0.0)
        
        # AI analysis defaults
        self.setdefault('ai_summary', '')
        self.setdefault('ai_entities', [])
        self.setdefault('ai_topics', [])
        self.setdefault('ai_sentiment', 'neutral')
        self.setdefault('ai_key_points', [])
        self.setdefault('ai_structured_data', {})
        self.setdefault('ai_analysis_timestamp', '')
        self.setdefault('ai_keywords', [])
        self.setdefault('enhanced_keywords', [])