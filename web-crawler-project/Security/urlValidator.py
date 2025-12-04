class URLValidator:
    def __init__(self, policy):
        self.policy = policy  

    def is_safe(self, url: str) -> bool:
        #use securityPolicy to enforce
        #enforce HTTPS
        if self.policy.force_https and not url.lower().startswith("https://"):
            print(f"[BLOCKED] Non-HTTPS URL: {url}")
            return False

        #block dangerous domains
        for blocked in self.policy.blocked_domains:
            if blocked in url.lower():
                print(f"[BLOCKED] Domain in blacklist: {url}")
                return False

        #check input length 
        if len(url) > self.policy.max_input_bytes:
            print(f"[BLOCKED] URL too long: {url}")
            return False

        #make sure sanitized
        if not url.startswith(("http://", "https://")):
            print(f"[BLOCKED] Invalid scheme: {url}")
            return False

        #pass all requirements 
        return True
