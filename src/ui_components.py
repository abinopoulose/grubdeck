import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QLabel, QPushButton, QScrollArea, QStackedWidget,
                             QProgressBar, QMessageBox, QDialog, QVBoxLayout as QDialogVBoxLayout,
                             QApplication, QGridLayout, QFrame, QLineEdit)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize
from constants import (WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
                       PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT, ERROR_NO_THEMES, ERROR_NO_COVER_IMAGE)
from models import Theme
from theme_fetcher import ThemeFetcher, CoverImageFetcher, CarouselImageFetcher
from theme_installer import ThemeInstaller


class InstallationProgressDialog(QDialog):
    """Dialog for showing installation progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Installing Theme")
        self.setModal(True)
        self.setFixedSize(PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT)
        
        layout = QDialogVBoxLayout(self)
        
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
    
    def update_progress(self, percentage, message):
        """Update progress bar and status message"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        QApplication.processEvents()  # Update UI immediately


class ThemeCard(QFrame):
    """A clickable card widget to display a theme preview"""
    
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Replaced 'box-shadow' with a valid PyQt alternative
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                margin: 5px; /* Adds space for a shadow-like effect */
            }
            QFrame:hover {
                background-color: #f5f5f5;
                border: 1px solid #c0c0c0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Loading placeholder for image
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(250, 150)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        layout.addWidget(self.image_label)
        
        # Fetch the cover image
        self.image_fetcher = CoverImageFetcher(self.theme.cover_image)
        self.image_fetcher.image_loaded.connect(self.on_image_loaded)
        self.image_fetcher.error_occurred.connect(self.on_image_error)
        self.image_fetcher.start()

        self.name_label = QLabel(self.theme.name)
        self.name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.name_label)

        self.author_label = QLabel(f"By: {self.theme.created_by}")
        self.author_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.author_label)
        
        layout.addStretch()
        
    def on_image_loaded(self, pixmap):
        """Display the loaded image on the card"""
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("") # Clear loading text

    def on_image_error(self, message):
        """Display a placeholder if image fails to load"""
        print(f"Error loading image for {self.theme.name}: {message}")
        self.image_label.setText(ERROR_NO_COVER_IMAGE)
        self.image_label.setPixmap(QPixmap()) # Clear any potential invalid pixmap


class ImageCarousel(QWidget):
    """Widget for displaying a carousel of images"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_image_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the carousel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image display area
        self.carousel_widget = QStackedWidget()
        self.carousel_widget.setMinimumHeight(450)
        self.carousel_widget.setStyleSheet("border-radius: 12px; background-color: #f0f0f0;")
        layout.addWidget(self.carousel_widget)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀")
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.previous_image)
        nav_layout.addWidget(self.prev_button)
        
        self.image_counter_label = QLabel("0 / 0")
        self.image_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.image_counter_label)
        
        self.next_button = QPushButton("▶")
        self.next_button.setFixedSize(40, 40)
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_image)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
    
    def load_images(self, pixmaps):
        """Load QPixmap images into the carousel"""
        # Clear existing content
        self.clear_carousel()
        
        if not pixmaps:
            self.show_error_message("No images available for this theme.")
            return
        
        for pixmap in pixmaps:
            scaled_pixmap = pixmap.scaled(
                self.carousel_widget.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.carousel_widget.addWidget(image_label)
        
        self.current_images = pixmaps
        self.current_image_index = 0
        self.update_navigation()
        self.carousel_widget.setCurrentIndex(0)
    
    def show_loading(self):
        """Show loading message"""
        self.clear_carousel()
        loading_label = QLabel("Loading images...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("font-size: 18px; color: #666; font-weight: bold;")
        self.carousel_widget.addWidget(loading_label)
        self.carousel_widget.setCurrentIndex(0)
        self.update_navigation()
    
    def show_error_message(self, message):
        """Show error message in carousel"""
        self.clear_carousel()
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("font-size: 14px; color: #d32f2f; padding: 20px;")
        self.carousel_widget.addWidget(error_label)
        self.carousel_widget.setCurrentIndex(0)
        self.update_navigation()
    
    def clear_carousel(self):
        """Clear all widgets from carousel"""
        while self.carousel_widget.count() > 0:
            widget = self.carousel_widget.widget(0)
            self.carousel_widget.removeWidget(widget)
            widget.deleteLater()
        
        self.current_images = []
        self.current_image_index = 0
    
    def update_navigation(self):
        """Update navigation button states and counter"""
        total_images = len(self.current_images)
        
        if total_images <= 1:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.image_counter_label.setText(f"{total_images} / {total_images}")
        else:
            self.prev_button.setEnabled(self.current_image_index > 0)
            self.next_button.setEnabled(self.current_image_index < total_images - 1)
            self.image_counter_label.setText(f"{self.current_image_index + 1} / {total_images}")
    
    def previous_image(self):
        """Go to previous image"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()
    
    def next_image(self):
        """Go to next image"""
        if self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()


class GrubThemeManagerApp(QMainWindow):
    """Main application window for GRUB Theme Manager"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        
        # --- FIX: Changed setGeometry to resize and added setMinimumSize ---
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # Ensure resizability by setting a minimum practical size
        self.setMinimumSize(QSize(800, 600))
        # --- END FIX ---
        
        self.current_theme = None
        self.installer_thread = None
        self.progress_dialog = None
        self.fetcher_thread = None
        self.carousel_fetcher_thread = None
        self.themes_data = []
        
        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.home_page = QWidget()
        self.preview_page = QWidget()
        
        self.setup_home_page()
        self.setup_preview_page()
        
        self.central_widget.addWidget(self.home_page)
        self.central_widget.addWidget(self.preview_page)
        
        self.start_theme_fetching()
    
    def setup_home_page(self):
        """Setup the home page with search and theme grid"""
        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(25, 25, 25, 25)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for themes...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 12px;
                font-size: 16px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_themes)
        layout.addWidget(self.search_bar)
        
        # Theme grid
        self.theme_grid_layout = QGridLayout()
        self.theme_grid_layout.setSpacing(20)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.grid_container = QWidget()
        self.grid_container.setLayout(self.theme_grid_layout)
        self.scroll_area.setWidget(self.grid_container)
        
        layout.addWidget(self.scroll_area)
    
    def setup_preview_page(self):
        """Setup the theme preview page"""
        layout = QVBoxLayout(self.preview_page)
        layout.setContentsMargins(25, 25, 25, 25)

        # Back button
        self.back_button = QPushButton("◀ Back to Themes")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #007acc;
                font-size: 16px;
                text-align: left;
                padding: 5px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.back_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.home_page))
        layout.addWidget(self.back_button)

        # Image Carousel
        self.image_carousel = ImageCarousel()
        layout.addWidget(self.image_carousel)

        # Details
        self.preview_name_label = QLabel()
        self.preview_name_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(self.preview_name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.preview_author_label = QLabel()
        self.preview_author_label.setStyleSheet("color: #666; font-size: 16px; margin-bottom: 20px;")
        layout.addWidget(self.preview_author_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.preview_description_label = QLabel()
        self.preview_description_label.setWordWrap(True)
        self.preview_description_label.setStyleSheet("font-size: 14px; color: #444;")
        layout.addWidget(self.preview_description_label)
        
        self.repo_link_button = QPushButton("View on GitHub")
        self.repo_link_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.repo_link_button.clicked.connect(self.open_repo_link)
        layout.addWidget(self.repo_link_button)

        self.install_button = QPushButton("Install Theme")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #2e8b57;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3cb371;
            }
        """)
        self.install_button.clicked.connect(self.install_theme)
        layout.addWidget(self.install_button)

        layout.addStretch()

    def start_theme_fetching(self):
        """Start fetching themes from the repository"""
        self.fetcher_thread = ThemeFetcher()
        self.fetcher_thread.themes_fetched.connect(self.populate_theme_grid)
        self.fetcher_thread.start()
    
    def populate_theme_grid(self, themes_data):
        """Populate the theme grid with fetched data"""
        self.themes_data = themes_data
        
        # Clear existing cards
        for i in reversed(range(self.theme_grid_layout.count())):
            widget = self.theme_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        if not themes_data:
            no_themes_label = QLabel(ERROR_NO_THEMES)
            no_themes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.theme_grid_layout.addWidget(no_themes_label, 0, 0)
            return

        col, row = 0, 0
        for theme in themes_data:
            card = ThemeCard(theme)
            card.mousePressEvent = lambda event, t=theme: self.show_theme_preview(t)
            self.theme_grid_layout.addWidget(card, row, col)
            col += 1
            if col > 2: # 3 cards per row
                col = 0
                row += 1
    
    def filter_themes(self):
        """Filter themes based on search bar text"""
        query = self.search_bar.text().lower()
        if query:
            filtered_themes = [
                t for t in self.themes_data
                if query in t.name.lower() or query in t.created_by.lower()
            ]
        else:
            filtered_themes = self.themes_data
        
        self.populate_theme_grid(filtered_themes)

    def show_theme_preview(self, theme: Theme):
        """Display the selected theme's details on the preview page"""
        self.current_theme = theme
        self.preview_name_label.setText(self.current_theme.name)
        self.preview_author_label.setText(f"By: {self.current_theme.created_by}")
        self.preview_description_label.setText(self.current_theme.description)

        # Show loading for the carousel images
        self.image_carousel.show_loading()
        self.carousel_fetcher_thread = CarouselImageFetcher(self.current_theme.carousel_images)
        self.carousel_fetcher_thread.images_loaded.connect(self.image_carousel.load_images)
        self.carousel_fetcher_thread.error_occurred.connect(self.image_carousel.show_error_message)
        self.carousel_fetcher_thread.start()

        self.central_widget.setCurrentWidget(self.preview_page)

    def open_repo_link(self):
        """Open the theme's GitHub repository link"""
        import webbrowser
        if self.current_theme and self.current_theme.repo_link:
            webbrowser.open(self.current_theme.repo_link)

    def install_theme(self):
        """Install the selected theme"""
        if not self.current_theme:
            return

        self.install_button.setEnabled(False)
        self.install_button.setText("Installing...")
        
        self.progress_dialog = InstallationProgressDialog(self)
        self.progress_dialog.show()
        
        self.installer_thread = ThemeInstaller(self.current_theme.name, self.current_theme.repo_link)
        self.installer_thread.progress_updated.connect(self.on_installation_progress)
        self.installer_thread.installation_completed.connect(self.on_installation_completed)
        self.installer_thread.start()
    
    def on_installation_progress(self, percentage, message):
        """Handle installation progress updates"""
        if self.progress_dialog:
            self.progress_dialog.update_progress(percentage, message)
    
    def on_installation_completed(self, success, message):
        """Handle installation completion"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.install_button.setEnabled(True)
        self.install_button.setText("Install Theme")
        
        if success:
            QMessageBox.information(self, "Installation Complete", message)
        else:
            QMessageBox.critical(self, "Installation Failed", message)
