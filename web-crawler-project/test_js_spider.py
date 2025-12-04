import asyncio
import time
import unittest

from scrapy.http import HtmlResponse, Request

from HTMLCrawler.spiders.javascript_crawler import KeywordJSCrawler


class KeywordJSCrawlerTests(unittest.TestCase):
    def test_parse_item_basic_html(self):
        html = """
        <html>
          <head>
            <title>JS Test</title>
          </head>
          <body>
            <div class="content">
              <p>Rendered JS content with keyword web.</p>
            </div>
            <a href="/next">Next</a>
          </body>
        </html>
        """

        request = Request(
            url="http://example.com/test-js",
            meta={"start_time": time.time(), "depth": 1},
        )
        response = HtmlResponse(
            url=request.url,
            body=html.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        spider = KeywordJSCrawler(
            keywords="web",
            filter_by_keywords="false",
            use_deepseek="false",
            use_ai_keywords="false",
            use_playwright="false",
            max_depth=1,
            allow_all_domains="true",
        )

        async def run_parse():
            results = []
            async for r in spider.parse_item(response):
                results.append(r)
            return results

        results = asyncio.run(run_parse())
        # Only one item because depth == max_depth
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertEqual(item["title"], "JS Test")
        self.assertIn("Rendered JS content", item["content"])
        self.assertEqual(item["source_domain"], "example.com")
        self.assertGreaterEqual(item["word_count"], 5)


if __name__ == "__main__":
    unittest.main()
