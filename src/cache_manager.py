import os
import time
import hashlib

class CacheManager:
    """A file-based caching system with Time-To-Live (TTL) expiration."""
    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.grubdeck/cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, url):
        # Hash the URL to create a safe, unique filename
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, url_hash)

    def get(self, url, max_age_seconds):
        """Retrieve data from cache if it exists and hasn't expired."""
        path = self._get_path(url)
        if os.path.exists(path):
            # Check if the file is younger than the max_age_seconds
            if time.time() - os.path.getmtime(path) < max_age_seconds:
                try:
                    with open(path, 'rb') as f:
                        return f.read()
                except Exception:
                    pass
        return None

    def set(self, url, data):
        """Write raw bytes to the cache."""
        path = self._get_path(url)
        try:
            with open(path, 'wb') as f:
                if isinstance(data, str):
                    f.write(data.encode('utf-8'))
                else:
                    f.write(data)
        except Exception:
            pass
