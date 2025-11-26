# Web Crawler Quick Guide for Teammates

This is a fast-start guide to install deps, run common scrapes, keep runs short, and resume where you left off.

## 1) Install dependencies
```bash
cd /Users/anelappana/CS/cse2410/Cse2410-group-project/web-crawler-project
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional for JS-heavy sites:
python -m playwright install chromium
```

## 2) Basic keyword crawler (single URL)
```bash
python3 run_crawler.py --spider keyword_html_crawler \
  --start-url "https://example.com" \
  --domain "example.com" \
  --max-depth 1 \
  --no-keyword-filter \
  --use-deepseek \
  --output-dir output
```
- Use `--no-keyword-filter` to keep pages even if they don’t match keywords.
- Add `--allow-all-domains` to follow off-site links (use carefully).
- Add `--use-playwright` for JS-rendered pages (requires Playwright install).

## 3) Multiple pages (simple spider)
```bash
python3 run_crawler.py --spider simple_html_crawler \
  --urls "https://site1.com/page,https://site2.com/page" \
  --no-keyword-filter --use-deepseek --output-dir output
```

## 4) NHC forecast discussions (targeted spider)
```bash
python3 run_crawler.py --spider nhc_forecast_discussion --year 2025 \
  --output-dir output \
  --close-timeout 60 --close-pagecount 50 \
  --jobdir jobstate/nhc_test_run1
```
- Uses a single archive year; follows only NHC pages for that year.
- `--close-timeout`/`--close-pagecount` bound the run.
- `--jobdir` saves state; rerun with the same jobdir to resume. Change jobdir for a fresh run.
- Add `--use-playwright` if needed.

## 5) Resuming a crawl
- Rerun the same command with the same `--jobdir` to continue where you stopped.
- To start clean, delete the jobdir or point `--jobdir` to a new path.

## 6) Where results go
- Each run writes timestamped CSV/JSON under `output/`, e.g., `output/crawl_results_YYYYMMDD_HHMMSS.csv/json`.
- Fields include URL, title, content preview, matched keywords, word count, depth, and (for NHC) `forecast_positions`.

## 7) Handy flags
- `--no-keyword-filter`: keep all pages (no dropping on missing keywords).
- `--allow-all-domains`: follow off-site links.
- `--use-playwright`: render JS (requires Playwright install).
- `--close-timeout N`: stop after N seconds.
- `--close-pagecount N`: stop after N pages.
- `--close-itemcount N`: stop after N items.
- `--jobdir PATH`: save/restore crawl state for resume.

## 8) Quick examples
- Short NHC test with resume:
  ```bash
  python3 run_crawler.py --spider nhc_forecast_discussion --year 2025 \
    --output-dir output --close-pagecount 30 --jobdir jobstate/nhc_smoke
  ```
- JS-heavy page with Playwright:
  ```bash
  python3 run_crawler.py --spider keyword_html_crawler \
    --start-url "https://www.brevardclerk.us/case-search" \
    --domain "brevardclerk.us" --max-depth 0 \
    --no-keyword-filter --use-playwright --output-dir output
  ```

## 9) Troubleshooting
- Empty CSV: check logs for drops (keyword filtering) or 404s; try `--no-keyword-filter`.
- Playwright errors: ensure `python -m playwright install chromium` and rerun with `--use-playwright`.
- Resume doing nothing: your jobdir queue may be exhausted; use a new `--jobdir` or delete the old one.
