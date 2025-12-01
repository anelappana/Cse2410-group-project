# Project Overview and How to Run It

This project is a Scrapy-based web crawler with three main spiders plus a Playwright-enabled JS spider. It supports AI enrichment (DeepSeek), resumable crawls, and bounded runs for quick tests.

## Spiders at a glance
- `keyword_html_crawler` (default): General-purpose HTML crawler (CrawlSpider rules). Supports keyword filtering, domain restriction overrides, DeepSeek AI, Playwright (optional), and start URLs (comma-separated).
- `keyword_js_crawler`: Playwright-first crawler for JavaScript-rendered pages. Manual link following; set `--use-playwright` to render JS.
- `simple_html_crawler`: Fetch specified URLs only (no link following), good for targeted grabs.
- `nhc_forecast_discussion`: Targets NHC archive pages, extracts discussions and forecast positions, ignores keyword filtering.

## Installation
```bash
cd /Users/anelappana/CS/cse2410/Cse2410-group-project/web-crawler-project
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional for JS sites:
python -m playwright install chromium
```

## Common runs
General HTML crawl:
```bash
python3 run_crawler.py --spider keyword_html_crawler \
  --start-url "https://example.com" --domain "example.com" \
  --max-depth 1 --no-keyword-filter --output-dir output
```

JS-rendered page:
```bash
python3 run_crawler.py --spider keyword_js_crawler \
  --start-url "http://quotes.toscrape.com/js/" --domain "quotes.toscrape.com" \
  --max-depth 1 --no-keyword-filter --use-playwright --output-dir output
```

NHC archive (bounded test, resumable):
```bash
python3 run_crawler.py --spider nhc_forecast_discussion --year 2025 \
  --output-dir output --close-pagecount 50 --close-timeout 60 \
  --jobdir jobstate/nhc_smoke
```
- Reuse the same `--jobdir` to resume; change it for a clean start.

## Bounding and resuming
- `--close-timeout N`: stop after N seconds.
- `--close-pagecount N`: stop after N pages.
- `--close-itemcount N`: stop after N items.
- `--jobdir PATH`: persist crawl state; rerun with the same jobdir to continue.

## Output
- Each run writes timestamped CSV/JSON to `output/`, e.g., `output/crawl_results_YYYYMMDD_HHMMSS.csv/json`.
- Fields include URL, title, content preview, keywords, word count, depth, crawl time; NHC spider adds `forecast_positions`.

## Flags you’ll use most
- `--no-keyword-filter`: keep all pages (no dropping on missing keywords).
- `--allow-all-domains`: follow off-site links (use carefully).
- `--use-playwright`: render JS via Playwright.
- `--use-deepseek --deepseek-api-key <key>`: enable AI enrichment (or set env `DEEPSEEK_API_KEY` and `--save-deepseek-key` once).

## Tests
```bash
python3 test_spider_parsing.py
python3 test_js_spider.py
```

## Troubleshooting
- Empty CSV: check for 404s or keyword drops; try `--no-keyword-filter`.
- Playwright errors: ensure `python -m playwright install chromium` and use `--use-playwright`.
- Resume does nothing: jobdir queue is empty; switch to a new `--jobdir` for a fresh crawl.
