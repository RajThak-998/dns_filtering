import time

class DNSCache:
    def __init__(self):
        self.store = {}
        self.hits = 0
        self.misses = 0

    def get(self, key, now):
        if key in self.store:
            entry = self.store[key]
            if entry["expires_at"] > now:
                self.hits += 1
                return entry["record"]
            else:
                del self.store[key]
        # Don't increment misses here - do it in server.py
        return None

    def set(self, key, record, ttl, now):
        if ttl > 0:
            self.store[key] = {
                "record": record,
                "expires_at": now + ttl
            }
