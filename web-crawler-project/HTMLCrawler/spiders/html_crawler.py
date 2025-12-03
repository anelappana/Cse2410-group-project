import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from HTMLCrawler.items import CrawlItem
from openai import OpenAI



class HTMLCrawler(CrawlSpider):
    name = "html_crawler"

    rules = (
        Rule(
            LinkExtractor(
                allow=r'.*',
                deny = r'(\.pdf|\.doc|\.zip|\.jpg|\.png|\.gif)$',
            ),
            callback='parse',
            follow=True,
            # process_request='playwright_request'  # Remove this line if not implemented
        ),
    )
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }
    def __init__(self, start_urls = None, allowed_domains = None, keywords = None, *args, **kwargs):
        super(HTMLCrawler, self).__init__(*args, **kwargs)
        self.items = []
        if start_urls:
            self.start_urls = [u.strip() for u in start_urls.split(',') if u.strip()]
        else:
            self.start_urls = ['https://www.nba.com']
    
        if allowed_domains:
            self.allowed_domains = [u.strip() for u in allowed_domains.split(',') if u.strip()]
        else:
            self.allowed_domains = []
        
        if keywords:
            self.keywords = [u.strip() for u in keywords.split(',') if u.strip()]
        else:
            self.keywords = []

    async def start(self):        
        if self.start_urls:
            for url in self.start_urls:
                yield scrapy.Request(url, self.parse)
    
    def parse(self, response):
        item = CrawlItem()
        item['url'] = response.url
        item['title'] = response.xpath('//title/text()').get(default='').strip()
        content_text = response.css('script::text').getall()
        item['content'] = ' '.join([t.strip() for t in content_text if t.strip()])
        links = response.xpath('href').getall()
        item['links_found'] = [urljoin(response.url, link) for link in links[:20]]

        if self.keywords:
            for keyword in self.keywords:
                if keyword in item['content']:
                    yield item
        else:
            yield item
        
        for url in item['links_found']:
            yield scrapy.Request(url, self.parse)
    


    