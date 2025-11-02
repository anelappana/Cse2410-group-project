"""
KeywordSpider:
- Fetch a URL with httpx (basic).
- Pull <title> and full text via BeautifulSoup.
- Emit CrawlItem for downstream processing.
"""
import httpx
from bs4 import BeautifulSoup
from webscraper.models.crawl_item import CrawlItem

class KeywordSpider:
    def __init__(self, keywords, data_processor, allowed_domains=None):
        self.keywords = keywords or []
        self.data_processor = data_processor
        self.allowed_domains = allowed_domains or []

    def parse(self, url: str):
        try:
            r = httpx.get(url, timeout=15)
            r.raise_for_status()
        except Exception:
            return []
        soup = BeautifulSoup(r.text, "lxml")
        title = (soup.title.string.strip() if soup.title else "") or url
        text = soup.get_text(separator=" ", strip=True)
        yield CrawlItem(url=url, title=title, content=text)
