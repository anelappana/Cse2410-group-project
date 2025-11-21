"""
DeepSeek Parser Integration Module

This module provides DeepSeek AI-powered parsing capabilities for the web crawler.
It can analyze, summarize, and extract structured information from crawled content.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from datetime import datetime
import logging


class DeepSeekParser:
    """
    DeepSeek-powered content parser for intelligent web content analysis.
    
    Features:
    - Content summarization
    - Entity extraction
    - Topic classification
    - Sentiment analysis
    - Structured data extraction
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        """
        Initialize DeepSeek parser
        
        Args:
            api_key: DeepSeek API key (if None, will look for DEEPSEEK_API_KEY env var)
            base_url: DeepSeek API base URL
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logging.warning("DeepSeek API key not found. Parser will run in fallback mode.")
    
    def is_enabled(self) -> bool:
        """Check if DeepSeek parsing is enabled"""
        return self.enabled
    
    def parse_content(self, content: str, url: str = "", title: str = "") -> Dict[str, Any]:
        """
        Parse content using DeepSeek AI for intelligent analysis
        
        Args:
            content: Raw text content to parse
            url: Source URL (optional)
            title: Page title (optional)
            
        Returns:
            Dictionary containing parsed information
        """
        if not self.enabled:
            return self._fallback_parse(content, url, title)
        
        try:
            # Prepare content for analysis
            analysis_prompt = self._build_analysis_prompt(content, url, title)
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert content analyzer. Provide structured analysis of web content."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            parsed_data = self._parse_ai_response(analysis_text)
            
            return {
                'summary': parsed_data.get('summary', ''),
                'entities': parsed_data.get('entities', []),
                'topics': parsed_data.get('topics', []),
                'sentiment': parsed_data.get('sentiment', 'neutral'),
                'key_points': parsed_data.get('key_points', []),
                'structured_data': parsed_data.get('structured_data', {}),
                'analysis_timestamp': datetime.now().isoformat(),
                'parser_used': 'deepseek'
            }
            
        except Exception as e:
            logging.error(f"DeepSeek parsing failed: {e}")
            return self._fallback_parse(content, url, title)
    
    def _build_analysis_prompt(self, content: str, url: str, title: str) -> str:
        """Build analysis prompt for DeepSeek"""
        # Truncate content if too long
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""
Analyze the following web content and provide a structured response in JSON format:

URL: {url}
Title: {title}

Content:
{content}

Please provide analysis in this JSON structure:
{{
    "summary": "Brief 2-3 sentence summary of the content",
    "entities": ["list", "of", "key", "entities", "people", "organizations"],
    "topics": ["main", "topics", "covered"],
    "sentiment": "positive/neutral/negative",
    "key_points": ["bullet", "point", "list", "of", "main", "points"],
    "structured_data": {{
        "category": "content category",
        "difficulty_level": "beginner/intermediate/advanced",
        "content_type": "article/tutorial/news/documentation/etc"
    }}
}}

Focus on accuracy and relevance. Extract only information that is clearly present in the content.
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback: try to parse structured text
        return self._parse_structured_text(response_text)
    
    def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        result = {
            'summary': '',
            'entities': [],
            'topics': [],
            'sentiment': 'neutral',
            'key_points': [],
            'structured_data': {}
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if 'summary:' in line.lower():
                result['summary'] = line.split(':', 1)[1].strip()
            elif 'sentiment:' in line.lower():
                result['sentiment'] = line.split(':', 1)[1].strip().lower()
        
        return result
    
    def _fallback_parse(self, content: str, url: str, title: str) -> Dict[str, Any]:
        """Fallback parsing when DeepSeek is not available"""
        # Simple rule-based parsing
        word_count = len(content.split())
        
        # Basic sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'disappointing']
        
        pos_count = sum(1 for word in positive_words if word in content.lower())
        neg_count = sum(1 for word in negative_words if word in content.lower())
        
        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Extract potential entities (capitalized words)
        entities = list(set(re.findall(r'\b[A-Z][a-z]+\b', content)))[:10]
        
        # Basic summary (first sentence or first 200 chars)
        sentences = re.split(r'[.!?]+', content)
        summary = sentences[0][:200] + "..." if sentences and len(sentences[0]) > 200 else sentences[0] if sentences else ""
        
        return {
            'summary': summary.strip(),
            'entities': entities,
            'topics': [],
            'sentiment': sentiment,
            'key_points': [],
            'structured_data': {
                'word_count': word_count,
                'content_type': 'webpage',
                'parser_used': 'fallback'
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'parser_used': 'fallback'
        }
    
    def extract_keywords_ai(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords using DeepSeek AI"""
        if not self.enabled:
            return self._extract_keywords_fallback(content, max_keywords)
        
        try:
            prompt = f"""
Extract the most important keywords from this text. Return only a JSON list of keywords.

Text: {content[:2000]}

Return format: ["keyword1", "keyword2", "keyword3", ...]
Maximum {max_keywords} keywords.
"""
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a keyword extraction expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            keywords_text = response.choices[0].message.content
            # Extract JSON array
            json_match = re.search(r'\[.*\]', keywords_text)
            if json_match:
                keywords = json.loads(json_match.group(0))
                return keywords[:max_keywords]
                
        except Exception as e:
            logging.error(f"AI keyword extraction failed: {e}")
        
        return self._extract_keywords_fallback(content, max_keywords)
    
    def _extract_keywords_fallback(self, content: str, max_keywords: int) -> List[str]:
        """Fallback keyword extraction using simple frequency analysis"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'this', 'that', 'these',
                     'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
                     'her', 'us', 'them'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]


class DeepSeekParserConfig:
    """Configuration class for DeepSeek parser"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.enable_summarization = True
        self.enable_entity_extraction = True
        self.enable_sentiment_analysis = True
        self.enable_keyword_extraction = True
        self.max_content_length = 5000
        self.max_keywords = 10
    
    def load_from_file(self, config_path: str):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except FileNotFoundError:
            logging.warning(f"Config file {config_path} not found, using defaults")
        except Exception as e:
            logging.error(f"Error loading config: {e}")
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        config_data = {
            'base_url': self.base_url,
            'enable_summarization': self.enable_summarization,
            'enable_entity_extraction': self.enable_entity_extraction,
            'enable_sentiment_analysis': self.enable_sentiment_analysis,
            'enable_keyword_extraction': self.enable_keyword_extraction,
            'max_content_length': self.max_content_length,
            'max_keywords': self.max_keywords
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)


# Factory function for easy initialization
def create_deepseek_parser(config_path: Optional[str] = None) -> DeepSeekParser:
    """
    Factory function to create a configured DeepSeek parser
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configured DeepSeekParser instance
    """
    config = DeepSeekParserConfig()
    
    if config_path:
        config.load_from_file(config_path)
    
    return DeepSeekParser(
        api_key=config.api_key,
        base_url=config.base_url
    )