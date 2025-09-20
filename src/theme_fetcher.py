# Theme fetching functionality for GrubDeck

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from constants import GITHUB_THEMES_INDEX_URL
from models import Theme


class ThemeFetcher(QThread):
    """Thread for fetching themes from GitHub repository"""
    themes_fetched = pyqtSignal(list)
    
    def run(self):
        """Fetch themes from the GitHub repository"""
        try:
            response = requests.get(GITHUB_THEMES_INDEX_URL)
            response.raise_for_status()
            themes_data = response.json()
            
            # Convert to Theme objects
            themes = []
            for theme_data in themes_data:
                try:
                    theme = Theme(
                        name=theme_data.get('name', ''),
                        description=theme_data.get('description', ''),
                        repo_link=theme_data.get('repo_link', ''),
                        author=theme_data.get('author'),
                        version=theme_data.get('version')
                    )
                    themes.append(theme)
                except ValueError as e:
                    print(f"Invalid theme data: {e}")
                    continue
            
            self.themes_fetched.emit(themes)
        except Exception as e:
            print(f"Error fetching themes: {e}")
            self.themes_fetched.emit([])


class CarouselImageFetcher(QThread):
    """Thread for fetching carousel images from a theme repository"""
    images_loaded = pyqtSignal(list, str)  # image_paths, temp_dir
    error_occurred = pyqtSignal(str)

    def __init__(self, repo_link):
        super().__init__()
        self.repo_link = repo_link

    def run(self):
        """Fetch images from the theme repository's view folder"""
        try:
            # Extract owner and repo name from GitHub URL
            if "github.com" in self.repo_link:
                parts = self.repo_link.rstrip('/').split('/')
                owner = parts[-2]
                repo = parts[-1]
                
                # Get contents of view folder
                from constants import GITHUB_API_BASE_URL
                api_url = f"{GITHUB_API_BASE_URL}/{owner}/{repo}/contents/view"
                response = requests.get(api_url)
                response.raise_for_status()
                
                files = response.json()
                from constants import IMAGE_EXTENSIONS
                image_files = [f for f in files if f['name'].lower().endswith(IMAGE_EXTENSIONS)]
                
                if not image_files:
                    self.error_occurred.emit("No images found in view folder")
                    return
                
                # Download images to temporary directory
                import tempfile
                import os
                from constants import TEMP_DIR_PREFIX
                
                temp_dir = tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX)
                downloaded_images = []
                
                for file_info in image_files:
                    try:
                        # Download image
                        img_response = requests.get(file_info['download_url'])
                        img_response.raise_for_status()
                        
                        # Save to temp directory
                        img_path = os.path.join(temp_dir, file_info['name'])
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded_images.append(img_path)
                    except Exception as e:
                        print(f"Error downloading {file_info['name']}: {e}")
                        continue
                
                if downloaded_images:
                    self.images_loaded.emit(downloaded_images, temp_dir)
                else:
                    self.error_occurred.emit("Failed to download any images")
                    
        except Exception as e:
            self.error_occurred.emit(f"Error fetching images: {e}")
