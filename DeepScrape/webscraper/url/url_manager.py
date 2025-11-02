"""
URLManager:
- Simple queue + visited set (cap by max_urls).
"""
from collections import deque
class URLManager:
    def __init__(self, max_urls: int = 200):
        self.visited = set()
        self.queue = deque()
        self.max = max_urls
    def add_urls(self, urls):
        for u in urls:
            if u not in self.visited and len(self.queue) < self.max:
                self.queue.append(u)
    def get_next_url(self):
        return self.queue.popleft() if self.queue else None
    def mark_visited(self, u): self.visited.add(u)
    def should_visit(self, u): return (u not in self.visited) and (len(self.visited) < self.max)
