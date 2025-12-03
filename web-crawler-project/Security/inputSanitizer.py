import re
import time

class InputSanitizer:
    def __init__(self, secure_policy=None):
        self.secure_policy = secure_policy

        #regex patterns
        self.block_scripts = re.compile(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>",
                                        re.IGNORECASE | re.DOTALL)
        self.event_handlr = re.compile(r"\s+on[a-z]+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)",
                                       re.IGNORECASE)
        self.url_pattern = re.compile(r"""(\b(?:href|src)\s*=\s*)
                                          (["'])\s*javascript:[^"']*\2""",
                                      re.IGNORECASE | re.VERBOSE)
        self.change_iframes = re.compile(r"<\s*iframe\b[^>]*>.*?<\s*/\s*iframe\s*>",
                                         re.IGNORECASE | re.DOTALL)

        self.danger_patterns = [
            re.compile(r"<\s*object\b[^>]*>.*?<\s*/\s*object\s*>", re.IGNORECASE | re.DOTALL),
            re.compile(r"<\s*embed\b[^>]*>.*?<\s*/\s*embed\s*>", re.IGNORECASE | re.DOTALL),
        ]

    def check_limit(self, text: str):
        #give error if limit is exceeded
        if not self.secure_policy:
            return
        max_bytes = getattr(self.secure_policy, "max_input_bytes", None)
        if isinstance(max_bytes, int) and max_bytes > 0:
            if len(text.encode("utf-8", errors="ignore")) > max_bytes:
                raise ValueError(f"Input exceeds max_input_bytes={max_bytes}")

    def strip_scripts(self, html: str) -> str:
        self.check_limit(html)
        start = time.time()

        html = self.block_scripts.sub("", html)
        html = self.event_handlr.sub("", html)
        html = self.url_pattern.sub(r"\1\2#\2", html)

        for pat in self.danger_patterns:
            html = pat.sub("", html)

        if self.secure_policy:
            max_ms = getattr(self.secure_policy, "max_parse_ms", None)
            if isinstance(max_ms, int) and max_ms > 0:
                elapsed_ms = int((time.time() - start) * 1000)
                if elapsed_ms > max_ms:
                    raise TimeoutError(f"strip_scripts exceeded max_parse_ms={max_ms}")

        return html

    def remove_iframe(self, html: str) -> str:
        self.check_limit(html)
        start = time.time()

        html = self.change_iframes.sub("", html)

        if self.secure_policy:
            max_ms = getattr(self.secure_policy, "max_parse_ms", None)
            if isinstance(max_ms, int) and max_ms > 0:
                elapsed_ms = int((time.time() - start) * 1000)
                if elapsed_ms > max_ms:
                    raise TimeoutError(f"remove_iframe exceeded max_parse_ms={max_ms}")

        return html

    def clamp_size(self, text: str, max_bytes: int) -> str:
        if max_bytes is None or max_bytes <= 0:
            return text
        encoded = text.encode("utf-8", errors="ignore")
        if len(encoded) <= max_bytes:
            return text
        truncated = encoded[:max_bytes]
        return truncated.decode("utf-8", errors="ignore")

    def sanitize(self, html: str) -> str:
        sanitized = self.strip_scripts(html)
        sanitized = self.remove_iframe(sanitized)
        if self.secure_policy and isinstance(getattr(self.secure_policy, "max_input_bytes", None), int):
            sanitized = self.clamp_size(sanitized, self.secure_policy.max_input_bytes)
        return sanitized
