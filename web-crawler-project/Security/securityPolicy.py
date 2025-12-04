from typing import List

class SecurityPolicy:
    def __init__(self,
                 force_https: bool = True,
                 blocked_domains: List[str] = None,
                 max_input_bytes: int = 5_000_000,
                 parse_t_limit: int = 2000):

        self.force_https = force_https
        self.blocked_domains = blocked_domains or []
        self.max_input_bytes = max_input_bytes
        self.parse_t_limit = parse_t_limit

    def block_danger_domain(self, target_domain: str) -> bool:
        #check domain
        return target_domain in self.blocked_domains

    def https_only(self, url: str) -> bool:
        #check url
        if not self.force_https:
            return True
        return url.lower().startswith("https://")

    def limit_input(self, payload_size: int) -> bool:
        #check input size
        return payload_size <= self.max_input_bytes

    def limit_parse_time(self, parse_time: int) -> bool:
        #check parsing time
        return parse_time <= self.parse_t_limit
