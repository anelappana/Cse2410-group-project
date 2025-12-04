#!/usr/bin/env python3
"""
DeepSeek Integration Test Script

This script tests the DeepSeek AI parser integration with the web crawler.
"""

import sys
import os
from datetime import datetime

# Add project to path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_deepseek_import():
    """Test if DeepSeek parser can be imported"""
    print("Testing DeepSeek parser import...")
    try:
        from HTMLCrawler.deepseek_parser import DeepSeekParser, create_deepseek_parser
        print("✅ DeepSeek parser import successful")
        return True
    except ImportError as e:
        print(f"❌ DeepSeek parser import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing DeepSeek parser: {e}")
        return False

def test_deepseek_fallback():
    """Test DeepSeek parser in fallback mode (no API key)"""
    print("\nTesting DeepSeek parser fallback mode...")
    try:
        from HTMLCrawler.deepseek_parser import DeepSeekParser
        
        # Create parser without API key
        parser = DeepSeekParser(api_key=None)
        
        if not parser.is_enabled():
            print("✅ Parser correctly detected missing API key")
        else:
            print("❌ Parser should be disabled without API key")
            return False
        
        # Test fallback parsing
        test_content = "This is a test article about Python web development using Scrapy framework."
        result = parser.parse_content(test_content, "http://example.com", "Test Article")
        
        expected_fields = ['summary', 'entities', 'topics', 'sentiment', 'key_points', 'structured_data']
        for field in expected_fields:
            if field not in result:
                print(f"❌ Missing field '{field}' in fallback result")
                return False
        
        print("✅ Fallback parsing successful")
        print(f"   Summary: {result['summary'][:100]}...")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Entities: {result['entities'][:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback parsing test failed: {e}")
        return False

def test_pipeline_integration():
    """Test DeepSeek pipeline integration"""
    print("\nTesting pipeline integration...")
    try:
        from HTMLCrawler.pipelines import DeepSeekAnalysisPipeline
        from HTMLCrawler.items import CrawlItem
        
        # Create mock item
        item = CrawlItem()
        item['url'] = 'http://example.com/test'
        item['title'] = 'Test Article'
        item['content'] = 'This is test content about Python programming and web development.'
        item['matched_keywords'] = ['python', 'web']
        
        # Create pipeline
        pipeline = DeepSeekAnalysisPipeline()
        
        # Mock spider
        class MockSpider:
            def __init__(self):
                self.logger = MockLogger()
        
        class MockLogger:
            def info(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass
        
        spider = MockSpider()
        
        # Initialize pipeline
        pipeline.open_spider(spider)
        
        # Process item
        processed_item = pipeline.process_item(item, spider)
        
        print("✅ Pipeline integration successful")
        print(f"   AI analysis enabled: {pipeline.enabled}")
        
        if pipeline.enabled:
            print(f"   AI summary field added: {'ai_summary' in processed_item}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline integration test failed: {e}")
        return False

def test_enhanced_export():
    """Test enhanced export pipeline"""
    print("\nTesting enhanced export pipeline...")
    try:
        from HTMLCrawler.pipelines import EnhancedDataExportPipeline
        from HTMLCrawler.items import CrawlItem
        import tempfile
        import os
        
        # Create temporary directory for test output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock item with AI data
            item = CrawlItem()
            item['url'] = 'http://example.com/test'
            item['title'] = 'Test Article'
            item['content'] = 'Test content'
            item['ai_summary'] = 'Test summary'
            item['ai_sentiment'] = 'positive'
            item['ai_topics'] = ['technology', 'programming']
            item['ai_entities'] = ['Python', 'Scrapy']
            item['ai_keywords'] = ['web', 'development']
            
            # Mock spider
            class MockSpider:
                output_dir = temp_dir
            
            spider = MockSpider()
            
            # Create and test pipeline
            pipeline = EnhancedDataExportPipeline()
            pipeline.open_spider(spider)
            pipeline.process_item(item, spider)
            pipeline.close_spider(spider)
            
            # Check if files were created
            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
            json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
            
            if csv_files and json_files:
                print("✅ Enhanced export successful")
                print(f"   CSV file created: {csv_files[0]}")
                print(f"   JSON file created: {json_files[0]}")
                return True
            else:
                print("❌ Enhanced export failed - no files created")
                return False
                
    except Exception as e:
        print(f"❌ Enhanced export test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from HTMLCrawler.deepseek_parser import DeepSeekParserConfig
        
        config = DeepSeekParserConfig()
        
        # Check default values
        if hasattr(config, 'enable_summarization') and hasattr(config, 'max_keywords'):
            print("✅ Configuration class working")
            print(f"   Summarization enabled: {config.enable_summarization}")
            print(f"   Max keywords: {config.max_keywords}")
            return True
        else:
            print("❌ Configuration class missing attributes")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all DeepSeek integration tests"""
    print("=" * 60)
    print("DEEPSEEK INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_deepseek_import,
        test_deepseek_fallback,
        test_pipeline_integration,
        test_enhanced_export,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All DeepSeek integration tests passed!")
        print("\nTo use DeepSeek AI analysis:")
        print("1. Set your API key: export DEEPSEEK_API_KEY='your-api-key'")
        print("2. Run crawler with AI: python run_crawler.py --use-deepseek --ai-keywords")
    else:
        print("❌ Some tests failed")
        print("\nThe basic functionality works, but DeepSeek integration may have issues.")
    
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())