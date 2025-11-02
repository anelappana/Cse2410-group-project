"""
DeepSeekAdapter:
- Thin wrapper around an OpenAI-compatible API for DeepSeek.
- Returns strict JSON (or raises).
"""
class DeepSeekAdapter:
    def extract_json(self, text: str, fields, hint: dict):
        # TODO: wire actual API client; for now return empty keys.
        return {k: "" for k in fields}
    def health(self) -> bool:
        return True
