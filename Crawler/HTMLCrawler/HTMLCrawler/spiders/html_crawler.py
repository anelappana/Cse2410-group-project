import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

#this class will use to represent a singular crawled url
class CrawlItem:
    #any other functions you would like to add you can. This is for Nick
    def __init__(self, url:str, title:str = "", content:str = ""):
        self.url = url #stores the url
        self.title = title #stores the title or name of the page
        self.content = content #stores the content of the website
        self.matched_keyword = [] #stores any keywords that match keywords found by the deepseek text-processor
    def to_dict(self):
        return {
            'Url:': self.url,
            'Title:' : self.title,
            'Content:' : self.content,
            'Matched Keywords:' : self.matched_keyword 
        }

#this class will be used to process the data that is found into a structured format. It must support CSV and JSON. 
class DataProcessor:
    def __init__(self, keywords = []):
        self.keywords = [word.lower() for word in keywords]
    #this rest of this class is up to Dylan. Any other datatypes are up to your discresion. Create any functions that you feel are fit
    def clean_text(self, text):
        pass
    def turn_to_csv(self, text):
        pass
    def turn_to_json(self, text):
        pass

#this is the web crawler class
class Keyword_HTML_Scrapper(scrapy.Spider):
    #this class is for Bhavik to build
    pass

#this class will manage all of the active crawlers. This is for anyone to do 
class Crawler_Manager:
    pass




    
    


        