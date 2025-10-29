import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

urls = input().split()
key_words = input().split()
class HTML_Spider(scrapy.Spider):
    name = 'html_spider'
    start_urls = urls
    
    


        