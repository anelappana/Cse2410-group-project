# 🚀 Quick Start Guide

Welcome to the Web Crawler Project! This guide will get you up and running in just a few minutes.

## ⚡ 1-Minute Setup

### Windows Users
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```cmd
   cd path\to\web-crawler-project
   ```
3. Run the setup:
   ```cmd
   run_crawler.bat install
   ```
4. Test the installation:
   ```cmd
   run_crawler.bat test
   ```

### Linux/Mac Users
1. Open terminal
2. Navigate to the project folder:
   ```bash
   cd path/to/web-crawler-project
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Test the installation:
   ```bash
   python test_crawler.py
   ```

## 🎯 First Crawl

### Option 1: Use the Windows Batch Script
```cmd
run_crawler.bat crawl "python,web,data"
```

### Option 2: Use Python Directly
```bash
python run_crawler.py --keywords "python,web,data"
```

### Option 3: Use Scrapy Directly
```bash
scrapy crawl keyword_html_crawler -a keywords="python,web,data"
```

## 📁 Check Your Results

After running a crawl, check the `output` directory for:
- `crawl_results_TIMESTAMP.csv` - Spreadsheet-friendly format
- `crawl_results_TIMESTAMP.json` - Complete data with all details

## 🎛️ Common Commands

### Basic Crawling
```bash
# Default crawl (uses quotes.toscrape.com)
python run_crawler.py

# Custom keywords
python run_crawler.py --keywords "machine learning,AI,neural networks"

# Specific website
python run_crawler.py --domain "example.com" --start-url "https://example.com"

# Control depth
python run_crawler.py --max-depth 2 --keywords "web scraping"
```

### Simple Single-Page Crawling
```bash
# Crawl specific URLs without following links
python run_crawler.py --spider simple_html_crawler --urls "http://example.com,http://test.com"
```

## 🔧 Troubleshooting

### Problem: "scrapy command not found"
**Solution**: Install Scrapy
```bash
pip install scrapy
```

### Problem: "Permission denied" or robots.txt errors
**Solution**: The crawler respects robots.txt by default. Try a different website or disable robots.txt checking in `HTMLCrawler/settings.py`:
```python
ROBOTSTXT_OBEY = False  # Use with caution
```

### Problem: Slow crawling
**Solution**: Adjust settings in `HTMLCrawler/settings.py`:
```python
DOWNLOAD_DELAY = 0.5  # Reduce delay
CONCURRENT_REQUESTS = 32  # Increase concurrent requests
```

### Problem: No results found
**Solution**: 
1. Check if your keywords are too specific
2. Try broader keywords like "web", "content", "information"
3. Disable keyword filtering: add `-a filter_by_keywords=false` to your command

## 💡 Pro Tips

### 1. Test First
Always run the test suite before starting a big crawl:
```bash
python test_crawler.py
```

### 2. Start Small
Begin with a shallow depth and increase gradually:
```bash
python run_crawler.py --max-depth 1 --keywords "your,keywords"
```

### 3. Monitor Output
Watch the terminal output for errors or warnings. The crawler will tell you what it's doing.

### 4. Respect Websites
- Always check a website's robots.txt: `http://example.com/robots.txt`
- Use reasonable delays between requests
- Don't overload small websites

### 5. Customize Configuration
Edit `crawler_config.ini` to set your preferred defaults for:
- Keywords
- Output directory
- Crawl depth
- Delays

## 📖 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Customize the spiders** in `HTMLCrawler/spiders/html_crawler.py`
3. **Add custom pipelines** in `HTMLCrawler/pipelines.py`
4. **Modify settings** in `HTMLCrawler/settings.py`

## 🆘 Need Help?

1. **Check the troubleshooting section** in README.md
2. **Run diagnostics**: `python test_crawler.py --test-config`
3. **Validate setup**: `python test_crawler.py --validate-project`
4. **Check Scrapy documentation**: https://docs.scrapy.org/

## 📊 Example Output

After a successful crawl, your CSV will look like:
```csv
url,title,content_preview,matched_keywords,links_count,depth,crawl_time
http://example.com,Python Tutorial,Learn Python programming...,python,5,0,2023-11-06T10:30:00
```

And your JSON will contain complete data:
```json
{
  "url": "http://example.com",
  "title": "Python Tutorial", 
  "content": "Complete page content here...",
  "matched_keywords": ["python"],
  "links_found": ["http://example.com/link1", "http://example.com/link2"],
  "depth": 0,
  "crawl_time": "2023-11-06T10:30:00",
  "loading_time": 0.85
}
```

---

**Happy Crawling! 🕷️**