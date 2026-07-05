import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from models import Theme
from constants import THEME_INDEX_URL, ERROR_NO_COVER_IMAGE
from cache_manager import CacheManager

# Initialize the global cache instance
cache = CacheManager()

class ThemeFetcher(QThread):
    themes_fetched = pyqtSignal(list)

    def run(self):
        try:
            import os
            # 1. Determine if the URL is actually a local file path
            is_local = False
            local_path = THEME_INDEX_URL
            
            if THEME_INDEX_URL.startswith("file://"):
                local_path = THEME_INDEX_URL.replace("file://", "")
                is_local = True
            elif THEME_INDEX_URL.startswith("/") or THEME_INDEX_URL.startswith("./") or THEME_INDEX_URL.startswith("~/"):
                local_path = os.path.expanduser(THEME_INDEX_URL)
                is_local = True

            # 2. Fetch the data
            if is_local and os.path.exists(local_path):
                # Bypass cache entirely for local files for instant dev feedback
                with open(local_path, 'r', encoding='utf-8') as f:
                    themes_data = json.load(f)
            else:
                # Standard network fetching with cache
                cached_data = cache.get(THEME_INDEX_URL, max_age_seconds=3600)
                if cached_data:
                    themes_data = json.loads(cached_data.decode('utf-8'))
                else:
                    response = requests.get(THEME_INDEX_URL, timeout=15)
                    response.raise_for_status()
                    cache.set(THEME_INDEX_URL, response.content)
                    themes_data = json.loads(response.text)
            
            themes = []
            for data in themes_data:
                theme = Theme(data)
                themes.append(theme)
            self.themes_fetched.emit(themes)
        except Exception as e:
            print(f"Failed to fetch themes: {e}")
            self.themes_fetched.emit([])


class CoverImageFetcher(QThread):
    image_loaded = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_url: str):
        super().__init__()
        self.image_url = image_url

    def run(self):
        try:
            if not self.image_url:
                self.error_occurred.emit(ERROR_NO_COVER_IMAGE)
                return
            
            # Check cache first (Expires in 7 Days / 604800 seconds)
            cached_image = cache.get(self.image_url, max_age_seconds=604800)
            if cached_image:
                self.image_loaded.emit(cached_image)
                return

            response = requests.get(self.image_url, stream=True, timeout=10)
            response.raise_for_status()
            # Save the new image to cache
            cache.set(self.image_url, response.content)
            self.image_loaded.emit(response.content)
        except Exception as e:
            self.error_occurred.emit(f"Network error: {e}")


class CarouselImageFetcher(QThread):
    images_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_urls: list):
        super().__init__()
        self.image_urls = image_urls

    def run(self):
        image_bytes_list = []
        for url in self.image_urls:
            try:
                # Check cache first (Expires in 7 Days / 604800 seconds)
                cached_image = cache.get(url, max_age_seconds=604800)
                if cached_image:
                    image_bytes_list.append(cached_image)
                else:
                    response = requests.get(url, stream=True, timeout=10)
                    response.raise_for_status()
                    cache.set(url, response.content)
                    image_bytes_list.append(response.content)
            except Exception as e:
                print(f"Failed to load carousel image {url}: {e}")
                
        if image_bytes_list:
            self.images_loaded.emit(image_bytes_list)
        else:
            self.error_occurred.emit("Failed to load any carousel images.")
