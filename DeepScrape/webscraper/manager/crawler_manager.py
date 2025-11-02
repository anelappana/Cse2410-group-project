"""
CrawlerManager:
- Coordinates spiders, URL frontier, processing, and storage.
- start_crawl(): main loop pulling URLs and processing items.
"""
from typing import List
from webscraper.spiders.keyword_spider import KeywordSpider

class CrawlerManager:
    def __init__(self, settings, storage, data_processor, url_manager):
        self.settings = settings
        self.storage = storage
        self.data_processor = data_processor
        self.url_manager = url_manager
        self.spiders: List[KeywordSpider] = []

    def start_crawl(self, urls, keywords, fields):
        spider = KeywordSpider(keywords=keywords, data_processor=self.data_processor)
        self.spiders.append(spider)
        self.url_manager.add_urls(urls)
        rows = []
        while True:
            url = self.url_manager.get_next_url()
            if not url:
                break
            for item in spider.parse(url):
                processed = self.data_processor.process_item(item, fields=fields)
                if processed:
                    rows.append(processed.to_dict())
        if rows:
            self.storage.save_data(rows, "export")
        return {"items": len(rows)}

    def stop_crawling(self):
        """Cooperative stop (stub)."""
        return True

    def get_crawl_status(self):
        """Return simple status for presentation/UI."""
        return {"spiders": len(self.spiders)}
