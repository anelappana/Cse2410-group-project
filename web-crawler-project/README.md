# Web Crawler Project

A comprehensive web crawler built using Scrapy framework, designed to extract data from web pages based on specified keywords. The project includes advanced functionality for processing crawled data, keyword matching, and exporting results in multiple formats (CSV, JSON).

## 🚀 Features

- **Keyword-based crawling**: Extract pages containing specific keywords
- **🤖 DeepSeek AI Integration**: Advanced AI-powered content analysis and parsing
- **Multiple spider types**: Choose between comprehensive crawling or simple page extraction  
- **Data export**: Export results to CSV and JSON formats with timestamps
- **Configurable depth**: Control how deep the crawler should go
- **Link extraction**: Automatically discover and follow links
- **Content cleaning**: Intelligent text processing and cleaning
- **Duplicate filtering**: Avoid processing the same URLs multiple times
- **Performance metrics**: Track loading times and crawl statistics

### 🤖 AI-Powered Features (DeepSeek Integration)

- **Content Summarization**: Automatic generation of concise summaries
- **Entity Extraction**: Identify people, organizations, and key concepts
- **Sentiment Analysis**: Determine the emotional tone of content
- **Topic Classification**: Categorize content into relevant topics
- **Enhanced Keyword Extraction**: AI-driven keyword discovery
- **Structured Data Analysis**: Extract meaningful insights from web content

## 📁 Project Structure

```
web-crawler-project/
├── HTMLCrawler/                    # Main Scrapy project
│   ├── __init__.py
│   ├── settings.py                 # Scrapy settings and configuration
│   ├── items.py                    # Data structure definitions
│   ├── pipelines.py                # Data processing pipelines
│   └── spiders/                    # Spider implementations
│       ├── __init__.py
│       └── html_crawler.py         # Main crawling logic
├── scrapy.cfg                      # Scrapy project configuration
├── requirements.txt                # Python dependencies
├── run_crawler.py                  # Command-line interface
├── test_crawler.py                 # Testing and validation script
└── README.md                       # This file
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Navigate to project directory**:
   ```bash
   cd web-crawler-project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python test_crawler.py --test-config
   ```

4. **🤖 (Optional) Set up DeepSeek AI Integration**:
   ```bash
   # Get your API key from https://platform.deepseek.com/
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   
   # Test DeepSeek integration
   python test_deepseek_integration.py
   ```

## 🎯 Usage

### Quick Start

1. **Run with default settings** (crawls quotes.toscrape.com):
   ```bash
   scrapy crawl keyword_html_crawler
   ```

2. **Run with custom keywords**:
   ```bash
   scrapy crawl keyword_html_crawler -a keywords="python,web,data"
   ```

3. **Run with custom domain and URL**:
   ```bash
   scrapy crawl keyword_html_crawler -a target_domain="example.com" -a start_url="http://example.com"
   ```

### Using the Command Line Interface

The project includes a user-friendly CLI script (`run_crawler.py`):

```bash
# Basic usage with default settings
python run_crawler.py

# Custom keywords and domain
python run_crawler.py --keywords "machine learning,AI,python" --domain "example.com"

# 🤖 Enable DeepSeek AI analysis
python run_crawler.py --use-deepseek --deepseek-api-key "your-api-key" --keywords "AI,technology"

# 🤖 AI-enhanced keyword extraction
python run_crawler.py --use-deepseek --ai-keywords --keywords "web development"

# Simple crawler for specific URLs
python run_crawler.py --spider simple_html_crawler --urls "http://example.com,http://test.com"

# Control crawl depth
python run_crawler.py --max-depth 2 --keywords "web scraping"

# Custom output directory
python run_crawler.py --output-dir "my_results" --keywords "data science"
```

### Available Spiders

1. **`keyword_html_crawler`** (default):
   - Follows links and crawls multiple pages
   - Filters content based on keywords
   - Respects robots.txt and crawl delays
   - Configurable maximum depth

2. **`simple_html_crawler`**:
   - Crawls specific URLs without following links
   - Good for targeted extraction
   - Faster for single-page analysis

## 📊 Output Formats

The crawler generates results in two formats:

### CSV Output (`crawl_results_TIMESTAMP.csv`)
```csv
url,title,content_preview,matched_keywords,links_count,depth,crawl_time,ai_summary,ai_sentiment,ai_topics,ai_entities,ai_keywords
http://example.com,Page Title,Content preview...,python,web,5,0,2023-11-06T10:30:00,AI-generated summary...,positive,"tech,programming","Python,AI","machine learning,neural networks"
```

### JSON Output (`crawl_results_TIMESTAMP.json`) - Enhanced with AI Analysis
```json
[
  {
    "url": "http://example.com",
    "title": "Page Title",
    "content": "Full page content...",
    "matched_keywords": ["python", "web"],
    "links_found": ["http://example.com/link1", "http://example.com/link2"],
    "depth": 0,
    "crawl_time": "2023-11-06T10:30:00.123456",
    "loading_time": 0.85,
    "ai_summary": "AI-generated summary of the content...",
    "ai_entities": ["Python", "Machine Learning", "OpenAI"],
    "ai_topics": ["technology", "programming", "artificial intelligence"],
    "ai_sentiment": "positive",
    "ai_key_points": ["Key insight 1", "Key insight 2"],
    "ai_keywords": ["neural networks", "deep learning", "AI models"],
    "enhanced_keywords": ["python", "web", "neural networks", "deep learning"]
  }
]
```

## ⚙️ Configuration

### Spider Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `keywords` | Comma-separated keywords to search for | `python,web,scrapy,data` | `"AI,machine learning"` |
| `target_domain` | Domain to restrict crawling to | `quotes.toscrape.com` | `example.com` |
| `start_url` | Starting URL for crawling | `http://quotes.toscrape.com` | `http://example.com` |
| `max_depth` | Maximum crawl depth | `3` | `5` |
| `filter_by_keywords` | Only keep pages with matching keywords | `True` | `False` |

### Settings Configuration

Key settings in `HTMLCrawler/settings.py`:

```python
# Crawling behavior
DOWNLOAD_DELAY = 1              # Delay between requests (seconds)
DEPTH_LIMIT = 3                 # Maximum crawl depth
CONCURRENT_REQUESTS = 32        # Concurrent requests limit

# Politeness
ROBOTSTXT_OBEY = True          # Respect robots.txt
AUTOTHROTTLE_ENABLED = True    # Auto-adjust delay based on latency

# Data processing
ITEM_PIPELINES = {
    'HTMLCrawler.pipelines.KeywordMatchingPipeline': 300,
    'HTMLCrawler.pipelines.DataExportPipeline': 400,
}
```

## 🧪 Testing

The project includes comprehensive testing capabilities:

```bash
# Run all tests and demonstrations
python test_crawler.py

# Validate project structure
python test_crawler.py --validate-project

# Check dependencies
python test_crawler.py --test-config

# Check Scrapy installation
python test_crawler.py --check-scrapy

# Run demonstration with sample data
python test_crawler.py --demo
```

## 🔍 Advanced Usage

### Custom Keyword Processing

```python
# Example: Using the DataProcessor for custom processing
from HTMLCrawler.spiders.html_crawler import DataProcessor

processor = DataProcessor(keywords=['python', 'web', 'scrapy'])
clean_text = processor.clean_text("  Raw   text   with   extra   spaces  ")
# Output: "Raw text with extra spaces"
```

### Pipeline Customization

The project uses Scrapy pipelines for data processing:

1. **KeywordMatchingPipeline**: Matches keywords and filters items
2. **DataExportPipeline**: Exports data to CSV and JSON
3. **DuplicateFilterPipeline**: Removes duplicate URLs

### Multiple Spider Management

```python
from HTMLCrawler.spiders.html_crawler import CrawlerManager

manager = CrawlerManager()
manager.add_crawler_config('keyword_html_crawler', keywords='python,web')
manager.add_crawler_config('simple_html_crawler', urls='http://example.com')

configs = manager.get_crawler_configs()
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission errors**: Check robots.txt compliance
   ```python
   ROBOTSTXT_OBEY = True  # In settings.py
   ```

3. **Slow crawling**: Adjust concurrent requests and delays
   ```python
   CONCURRENT_REQUESTS = 16
   DOWNLOAD_DELAY = 0.5
   ```

4. **Memory issues with large crawls**: Enable data streaming
   ```python
   ITEM_PIPELINES = {
       'HTMLCrawler.pipelines.DataExportPipeline': 400,
   }
   ```

### Debug Mode

Enable verbose logging:
```bash
scrapy crawl keyword_html_crawler -L DEBUG
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python test_crawler.py`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions and classes
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For questions and support:

1. Check the troubleshooting section above
2. Run the test script to validate your setup: `python test_crawler.py`
3. Review Scrapy documentation: https://docs.scrapy.org/
4. Open an issue for bugs or feature requests

## 🔄 Version History

- **v1.0.0**: Initial release with basic crawling functionality
- **v1.1.0**: Added keyword matching and export pipelines
- **v1.2.0**: Enhanced CLI interface and testing framework
- **v1.3.0**: Added multiple spider support and advanced configuration