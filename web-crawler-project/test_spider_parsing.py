import time
import unittest

from scrapy.http import HtmlResponse, Request

from HTMLCrawler.spiders.html_crawler import KeywordHTMLCrawler, NHCForecastDiscussionSpider


class SpiderParsingTests(unittest.TestCase):
    def test_keyword_crawler_parses_basic_page(self):
        html = """
        <html>
          <head>
            <title>Test Page</title>
            <link rel="canonical" href="http://example.com/test"/>
          </head>
          <body>
            <article>
              <p>web content here with keyword match.</p>
            </article>
            <a href="/next">Next</a>
          </body>
        </html>
        """
        request = Request(
            url="http://example.com/test",
            meta={"start_time": time.time(), "depth": 0},
        )
        response = HtmlResponse(
            url=request.url,
            body=html.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        spider = KeywordHTMLCrawler(
            keywords="web",
            filter_by_keywords="false",
            use_deepseek="false",
            use_ai_keywords="false",
            allow_all_domains="true",
        )

        items = list(spider.parse_item(response))
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["title"], "Test Page")
        self.assertIn("web content here", item["content"])
        self.assertEqual(item["canonical_url"], "http://example.com/test")
        self.assertEqual(item["source_domain"], "example.com")
        self.assertGreaterEqual(len(item["links_found"]), 1)

    def test_extract_forecast_positions_block(self):
        text = """
        FORECAST DISCUSSION
        Some intro text.
        FORECAST POSITIONS AND MAX WINDS
        INIT  24/1500Z 36.6N  48.9W   35 KT  40 MPH
        12H  25/0000Z 37.9N  46.3W   35 KT  40 MPH
        24H  25/1200Z 39.6N  41.5W   30 KT  35 MPH...POST-   TROP/REMNT LOW
        36H  26/0000Z...DISSIPATED
        NEXT ADVISORY
        """
        spider = NHCForecastDiscussionSpider(archive_url="https://www.nhc.noaa.gov/archive/2025/", year="2025")
        block = spider.extract_forecast_positions(text)
        self.assertIn("FORECAST POSITIONS AND MAX WINDS", block)
        self.assertIn("INIT  24/1500Z", block)
        self.assertIn("36H  26/0000Z", block)


if __name__ == "__main__":
    unittest.main()
