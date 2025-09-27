from PyQt6.QtWidgets import (QDialog, QProgressBar, QLabel, QPushButton, 
                             QFrame, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout,
                             QGraphicsDropShadowEffect, QApplication)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize, QRect

from constants import PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT, ERROR_NO_COVER_IMAGE
from models import Theme
from theme_fetcher import CoverImageFetcher

class InstallationProgressDialog(QDialog):
    """Dialog for showing installation progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Installing Theme")
        self.setModal(True)
        self.setFixedSize(PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT)
        
        layout = QVBoxLayout(self)
        
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
    """A clickable card widget to display a theme preview with modern styling."""
    
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # --- MODERN CARD STYLING (Shadow Effect) ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20) 
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(0, 5) 
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QFrame {
                border: none; 
                border-radius: 16px;
                background-color: #ffffff; 
                margin: 10px; 
            }
            QFrame:hover {
                background-color: #f7f7f7; 
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)

        # Image Label (The container for the image)
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(250, 150) 
        
        # --- Clipping Implementation ---
        self.image_wrapper = QWidget()
        wrapper_layout = QVBoxLayout(self.image_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0) # CRITICAL: No margins on layout
        wrapper_layout.setSpacing(0)
        
        wrapper_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_wrapper.setFixedSize(250, 150)
        
        # Style for the image wrapper to clip the image to the top rounded corners
        self.image_wrapper.setStyleSheet("""
            QWidget {
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                background-color: #e0e0e0; 
                border: none; 
            }
            QLabel {
                background-color: #e0e0e0;
                color: #555;
                font-size: 14px;
                border: none;
            }
        """)
        
        layout.addWidget(self.image_wrapper, alignment=Qt.AlignmentFlag.AlignCenter)
        # --- End Clipping Implementation ---
        
        # Content Container (for padding and text)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(5)

        self.name_label = QLabel(self.theme.name)
        self.name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #2c3e50;")
        content_layout.addWidget(self.name_label)

        self.author_label = QLabel(f"By: {self.theme.created_by}")
        self.author_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        content_layout.addWidget(self.author_label)
        
        content_layout.addStretch()
        layout.addWidget(content_container)
        
        # Fetch the cover image
        self.image_fetcher = CoverImageFetcher(self.theme.cover_image)
        self.image_fetcher.image_loaded.connect(self.on_image_loaded)
        self.image_fetcher.error_occurred.connect(self.on_image_error)
        self.image_fetcher.start()

    def on_image_loaded(self, pixmap):
        """Display the loaded image on the card, scaling/cropping it to fit."""
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("") # Clear loading text
        self.image_label.setStyleSheet("border: none;") 

    def on_image_error(self, message):
        """Display a placeholder if image fails to load"""
        self.image_label.setText(ERROR_NO_COVER_IMAGE)
        self.image_label.setPixmap(QPixmap()) 
        self.image_label.setStyleSheet("font-size: 14px; color: #d32f2f; background-color: #e0e0e0; border: none;")


class ImageCarousel(QWidget):
    """Widget for displaying a carousel of images"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_image_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the carousel UI with full-height navigation buttons"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        image_and_nav_layout = QHBoxLayout()
        image_and_nav_layout.setContentsMargins(0, 0, 0, 0)
        image_and_nav_layout.setSpacing(5)

        self.carousel_widget = QStackedWidget()
        self.carousel_widget.setMinimumSize(600, 450)
        self.carousel_widget.setStyleSheet("border-radius: 12px; background-color: #f0f0f0;")
        
        button_style = """
            QPushButton {
                background-color: rgba(0, 0, 0, 0.05); 
                border: none;
                border-radius: 12px;
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px 5px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.15);
                color: #000;
            }
            QPushButton:disabled {
                color: #bbb;
            }
        """

        self.prev_button = QPushButton("◀")
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet(button_style)
        self.prev_button.clicked.connect(self.previous_image)
        
        self.next_button = QPushButton("▶")
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet(button_style)
        self.next_button.clicked.connect(self.next_image)
        
        image_and_nav_layout.addWidget(self.prev_button)
        image_and_nav_layout.addWidget(self.carousel_widget, 1) 
        image_and_nav_layout.addWidget(self.next_button)
        
        main_layout.addLayout(image_and_nav_layout, 1)

        self.image_counter_label = QLabel("0 / 0")
        self.image_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_counter_label.setStyleSheet("font-size: 14px; color: #666; padding: 10px 0;")
        
        main_layout.addWidget(self.image_counter_label)
    
    def load_images(self, pixmaps):
        """Load QPixmap images into the carousel"""
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
