"""
URLValidator:
- Enforce HTTPS-only + domain allow-list (extend with SecurityPolicy).
"""
from urllib.parse import urlparse
class URLValidator:
    def is_safe(self, url: str, policy) -> bool:
        p = urlparse(url)
        if getattr(policy, "https_only", True) and p.scheme != "https":
            return False
        blocked = set(getattr(policy, "blocked_domains", []))
        if p.netloc in blocked:
            return False
        return True
