"""
WebScraperApp wires managers and starts a crawl.
"""
from webscraper.manager.crawler_manager import CrawlerManager
from webscraper.settings.settings_manager import SettingsManager
from webscraper.storage.storage_manager import StorageManager
from webscraper.processing.data_processor import DataProcessor
from webscraper.url.url_manager import URLManager

class WebScraperApp:
    """Entry point used by CLI/scripts."""
    def __init__(self):
        self.settings = SettingsManager()
        self.storage = StorageManager()
        self.data_processor = DataProcessor()
        self.url_manager = URLManager()
        self.manager = CrawlerManager(
            settings=self.settings,
            storage=self.storage,
            data_processor=self.data_processor,
            url_manager=self.url_manager,
        )

    def run(self, urls, keywords, fields):
        """Start a crawl with provided inputs."""
        self.manager.start_crawl(urls=urls, keywords=keywords, fields=fields)
