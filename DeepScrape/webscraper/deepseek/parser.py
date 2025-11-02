"""
DeepSeekParser:
- Build prompts/schema hints for fields.
- Call adapter to return strict JSON.
- Retry/validation hooks (extend as needed).
"""
from webscraper.deepseek.adapter import DeepSeekAdapter

class DeepSeekParser:
    def __init__(self, model="deepseek-chat", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.adapter = DeepSeekAdapter()

    def parse_data(self, text: str, fields):
        return self.adapter.extract_json(text, fields=fields, hint={})
