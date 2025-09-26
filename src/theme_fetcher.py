import json
import requests
import os
import shutil
import tempfile
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from models import Theme
from constants import THEME_INDEX_URL, ERROR_NO_COVER_IMAGE

class ThemeFetcher(QThread):
    """
    Thread for fetching the list of themes from a remote repository.
    """
    themes_fetched = pyqtSignal(list)

    def run(self):
        """
        Fetches the theme data from the remote URL and emits it.
        """
        try:
            response = requests.get(THEME_INDEX_URL)
            response.raise_for_status()
            
            themes_data = json.loads(response.text)
            
            themes = []
            for data in themes_data:
                # Create a Theme object, handling missing fields gracefully
                theme = Theme(
                    id=data.get('id'),
                    name=data.get('name'),
                    cover_image=data.get('cover_image'),
                    repo_link=data.get('repo_link'),
                    description=data.get('description', ''),
                    created_by=data.get('created_by', 'Unknown'),
                    carousel_images=data.get('carousel_images', [])
                )
                themes.append(theme)
            
            self.themes_fetched.emit(themes)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch themes: {e}")
            self.themes_fetched.emit([])
        except json.JSONDecodeError as e:
            print(f"Failed to parse theme data: {e}")
            self.themes_fetched.emit([])


class CoverImageFetcher(QThread):
    """
    Thread for fetching a single cover image from a URL.
    """
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_url: str):
        super().__init__()
        self.image_url = image_url

    def run(self):
        try:
            if not self.image_url:
                self.error_occurred.emit(ERROR_NO_COVER_IMAGE)
                return
            
            response = requests.get(self.image_url, stream=True)
            response.raise_for_status()
            
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            if pixmap.isNull():
                self.error_occurred.emit(f"Failed to load image from URL: {self.image_url}")
            else:
                self.image_loaded.emit(pixmap)
                
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Network error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")


class CarouselImageFetcher(QThread):
    """
    Thread for fetching multiple carousel images.
    """
    images_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_urls: list):
        super().__init__()
        self.image_urls = image_urls

    def run(self):
        pixmaps = []
        for url in self.image_urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                
                if not pixmap.isNull():
                    pixmaps.append(pixmap)
            except requests.exceptions.RequestException as e:
                print(f"Failed to load carousel image from URL {url}: {e}")
                continue # Try the next image

        if pixmaps:
            self.images_loaded.emit(pixmaps)
        else:
            self.error_occurred.emit("Failed to load any carousel images.")
