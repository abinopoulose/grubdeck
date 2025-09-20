# Image carousel functionality for GrubDeck

import os
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, 
                             QLabel, QPushButton)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class ImageCarousel(QWidget):
    """Widget for displaying a carousel of images"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_image_index = 0
        self.temp_dirs = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the carousel UI"""
        layout = QVBoxLayout(self)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.previous_image)
        nav_layout.addWidget(self.prev_button)
        
        self.image_counter_label = QLabel("0 / 0")
        self.image_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.image_counter_label)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_image)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)

        # Image display area
        self.carousel_widget = QStackedWidget()
        self.carousel_widget.setMinimumHeight(400)
        self.carousel_widget.setStyleSheet("border: 2px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.carousel_widget)
    
    def load_images(self, image_paths, temp_dir):
        """Load images into the carousel"""
        # Clean up previous temp directory
        self.cleanup_temp_dirs()
        
        # Track new temp directory
        self.temp_dirs.append(temp_dir)
        
        if not image_paths:
            self.show_error_message("No images found")
            return
        
        # Clear existing content
        self.clear_carousel()
        
        # Create image widgets
        loaded_images = []
        for img_path in image_paths:
            try:
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    # Scale image to fit carousel while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(600, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    
                    image_label = QLabel()
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.setStyleSheet("background-color: white;")
                    
                    self.carousel_widget.addWidget(image_label)
                    loaded_images.append(img_path)
                else:
                    print(f"Failed to load image: {img_path}")
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
        
        # Set current images to only successfully loaded ones
        self.current_images = loaded_images
        self.current_image_index = 0
        
        # Update navigation and show first image
        self.update_navigation()
        if len(self.current_images) > 0:
            self.carousel_widget.setCurrentIndex(0)
    
    def show_loading(self):
        """Show loading message with spinner"""
        self.clear_carousel()
        
        # Create loading container
        loading_container = QWidget()
        loading_layout = QVBoxLayout(loading_container)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add spinner (animated dots)
        spinner_label = QLabel("⏳")
        spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner_label.setStyleSheet("font-size: 48px; color: #007acc;")
        loading_layout.addWidget(spinner_label)
        
        # Add loading text
        loading_label = QLabel("Loading images...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("font-size: 18px; color: #666; font-weight: bold; margin-top: 10px;")
        loading_layout.addWidget(loading_label)
        
        # Add progress indicator
        progress_label = QLabel("Please wait while we fetch theme previews")
        progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_label.setStyleSheet("font-size: 14px; color: #888; margin-top: 5px;")
        loading_layout.addWidget(progress_label)
        
        self.carousel_widget.addWidget(loading_container)
        self.carousel_widget.setCurrentIndex(0)
    
    def show_error_message(self, message):
        """Show error message in carousel"""
        self.clear_carousel()
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("font-size: 14px; color: #d32f2f; padding: 20px;")
        self.carousel_widget.addWidget(error_label)
        self.carousel_widget.setCurrentIndex(0)
    
    def clear_carousel(self):
        """Clear all widgets from carousel"""
        while self.carousel_widget.count() > 0:
            widget = self.carousel_widget.widget(0)
            self.carousel_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Reset navigation
        self.current_images = []
        self.current_image_index = 0
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.image_counter_label.setText("0 / 0")
    
    def update_navigation(self):
        """Update navigation button states and counter"""
        total_images = len(self.current_images)
        
        if total_images == 0:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.image_counter_label.setText("0 / 0")
        elif total_images == 1:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.image_counter_label.setText("1 / 1")
        else:
            # Multiple images - enable navigation
            self.prev_button.setEnabled(self.current_image_index > 0)
            self.next_button.setEnabled(self.current_image_index < total_images - 1)
            self.image_counter_label.setText(f"{self.current_image_index + 1} / {total_images}")
    
    def previous_image(self):
        """Go to previous image"""
        if self.current_images and self.current_image_index > 0:
            self.current_image_index -= 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()
    
    def next_image(self):
        """Go to next image"""
        if self.current_images and self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()
    
    def cleanup_temp_dirs(self):
        """Clean up temporary directories created for carousel images"""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp directory {temp_dir}: {e}")
        self.temp_dirs.clear()
    
    def closeEvent(self, event):
        """Clean up when the widget is closed"""
        self.cleanup_temp_dirs()
        event.accept()
