"""
DataProcessor:
- clean_text(): sanitize HTML/text.
- filter_by_keywords(): quick boolean filter.
- calculate_relevance_score(): heuristic scoring.
- process_item(): main pipeline; optionally calls DeepSeek.
"""
from webscraper.processing.input_sanitizer import InputSanitizer
from webscraper.processing.schema_validator import SchemaValidator
from webscraper.deepseek.parser import DeepSeekParser

class DataProcessor:
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.validator = SchemaValidator()
        self.deepseek = DeepSeekParser()

    def clean_text(self, text: str) -> str:
        return self.sanitizer.strip_scripts(self.sanitizer.remove_iframes(text))

    def filter_by_keywords(self, content: str, keywords) -> bool:
        if not keywords:
            return True
        c = content.lower()
        return any(k.lower() in c for k in keywords)

    def calculate_relevance_score(self, content: str) -> float:
        return min(1.0, len(content) / 5000.0)

    def process_item(self, item, fields):
        item.content = self.clean_text(item.content)
        try:
            data = self.deepseek.parse_data(item.content, fields=fields)
            if self.validator.validate(data, required=fields):
                return item
        except Exception:
            return None
        return item
