"""
Minimal DeepSeek-backed scraper that fetches pages, cleans HTML, and produces
human-readable summaries while preserving source URLs.
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from HTMLCrawler.deepseek_parser import create_deepseek_parser


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)


def fetch_html(url: str, timeout: int = 20) -> str:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def clean_html(html: str, max_chars: int) -> Dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    # Drop non-content tags so the summary focuses on readable text
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = " ".join(soup.get_text(separator=" ", strip=True).split())
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + "..."
    return {"title": title, "text": text}


def summarize_page(parser, url: str, max_chars: int) -> Dict[str, Any]:
    raw_html = fetch_html(url)
    cleaned = clean_html(raw_html, max_chars)
    analysis = parser.parse_content(cleaned["text"], url=url, title=cleaned["title"])

    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "title": cleaned["title"],
        "raw_html_length": len(raw_html),
        "clean_text_preview": cleaned["text"][:500],
        "analysis": analysis,
    }


def run(urls: List[str], output_dir: str, max_chars: int) -> str:
    os.makedirs(output_dir, exist_ok=True)
    parser = create_deepseek_parser()

    results = []
    for url in urls:
        try:
            result = summarize_page(parser, url.strip(), max_chars)
            results.append(result)
        except Exception as exc:
            results.append(
                {
                    "url": url,
                    "error": str(exc),
                    "analysis": {"summary": "", "parser_used": "none"},
                }
            )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(output_dir, f"deepseek_readable_{timestamp}.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch pages and translate them to human-readable summaries with DeepSeek."
    )
    parser.add_argument(
        "--urls",
        required=True,
        help="Comma-separated list of URLs to scrape",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to write JSON results (default: output)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Trim cleaned text to this many characters before sending to DeepSeek (default: 4000)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    out_file = run(urls, args.output_dir, args.max_chars)
    print(f"Saved DeepSeek summaries for {len(urls)} page(s) to {out_file}")


if __name__ == "__main__":
    main()
