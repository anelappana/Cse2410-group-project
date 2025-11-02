#!/usr/bin/env python
"""
CLI entry to kick off a crawl.
Inputs: --urls, --keywords, --fields
Output: CSV/JSON/Parquet via StorageManager.
"""
import argparse
from webscraper.app import WebScraperApp

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", type=str, required=True, help="Comma-separated seed URLs")
    ap.add_argument("--keywords", type=str, default="", help="Comma-separated keywords")
    ap.add_argument("--fields", type=str, default="title,url", help="Comma-separated field names")
    args = ap.parse_args()

    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    fields = [f.strip() for f in args.fields.split(",") if f.strip()]

    app = WebScraperApp()
    app.run(urls=urls, keywords=keywords, fields=fields)

if __name__ == "__main__":
    main()
