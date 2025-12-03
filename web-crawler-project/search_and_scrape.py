"""
Search a topic on the web, fetch top result pages, and summarize them with DeepSeek.

Flow:
- User provides a topic (search query).
- We query DuckDuckGo's HTML endpoint (no API key required).
- We fetch/scrape the top N result pages.
- We run DeepSeekParser to generate readable summaries (falls back if no key).

Outputs a JSON file with search metadata and per-URL summaries.
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from simple_deepseek_scraper import (
    summarize_page,
    create_deepseek_parser,
    USER_AGENT,
)


SEARCH_ENGINE = "duckduckgo_html"
# Static HTML endpoint (no JS) so we can parse results without a browser
SEARCH_URL = "https://html.duckduckgo.com/html/"


def search_duckduckgo(query: str, max_results: int = 5) -> List[str]:
    """
    Perform a basic DuckDuckGo HTML search and return result URLs.
    """
    data = {"q": query}
    headers = {"User-Agent": USER_AGENT}
    # POST gives consistent responses on the HTML endpoint
    resp = requests.post(SEARCH_URL, data=data, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    urls: List[str] = []
    for a in soup.select("a.result__a"):
        href = a.get("href")
        if href and href.startswith("http"):
            urls.append(href)
        if len(urls) >= max_results:
            break
    return urls


def run_search_and_scrape(topic: str, max_results: int, max_chars: int, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    parser = create_deepseek_parser()
    urls = search_duckduckgo(topic, max_results=max_results)

    results: List[Dict] = []
    for idx, url in enumerate(urls, start=1):
        try:
            summary = summarize_page(parser, url, max_chars)
            summary["rank"] = idx
            results.append(summary)
        except Exception as exc:
            results.append(
                {
                    "url": url,
                    "rank": idx,
                    "error": str(exc),
                    "analysis": {"summary": "", "parser_used": "none"},
                }
            )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(output_dir, f"topic_search_summary_{timestamp}.json")
    payload = {
        "topic": topic,
        "search_engine": SEARCH_ENGINE,
        "result_count": len(results),
        "timestamp": timestamp,
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search the web for a topic and summarize the top results with DeepSeek."
    )
    parser.add_argument("--topic", required=True, help="Topic or search query text.")
    parser.add_argument(
        "--results",
        type=int,
        default=5,
        help="Number of search results to scrape (default: 5).",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Trim cleaned page text to this many characters before sending to DeepSeek (default: 4000).",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to write JSON results (default: output).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out_file = run_search_and_scrape(
        topic=args.topic,
        max_results=args.results,
        max_chars=args.max_chars,
        output_dir=args.output_dir,
    )
    print(f"Saved search summaries to {out_file}")


if __name__ == "__main__":
    main()
