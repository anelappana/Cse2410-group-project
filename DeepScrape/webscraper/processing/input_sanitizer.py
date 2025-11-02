"""
InputSanitizer:
- Remove <script>/<iframe> blocks.
- Clamp size to prevent resource abuse.
"""
import re
class InputSanitizer:
    TAG_RE = re.compile(r"(?is)<(script|iframe)[^>]*>.*?</\\1>")
    def strip_scripts(self, html_or_text: str) -> str:
        return self.TAG_RE.sub("", html_or_text)
    def remove_iframes(self, html_or_text: str) -> str:
        return self.TAG_RE.sub("", html_or_text)
    def clamp_size(self, text: str, max_bytes: int = 800000) -> str:
        return text.encode()[:max_bytes].decode(errors="ignore")
