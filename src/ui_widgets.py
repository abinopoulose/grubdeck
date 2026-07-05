from PyQt6.QtWidgets import (QDialog, QProgressBar, QLabel, QPushButton, 
                             QFrame, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout,
                             QGraphicsDropShadowEffect, QApplication)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize, QMargins

from constants import PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT, ERROR_NO_COVER_IMAGE
from models import Theme
from theme_fetcher import CoverImageFetcher

class InstallationProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Installing Theme")
        self.setModal(True)
        self.setFixedSize(PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT)
        self.setStyleSheet("QDialog { background-color: #181825; border: 1px solid #313244; border-radius: 12px; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton { background-color: #313244; color: #cdd6f4; border: none; border-radius: 6px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_progress(self, percentage, message):
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        QApplication.processEvents()

class ThemeCard(QFrame):
    _active_fetchers = []
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ThemeCard")
        self.setFixedSize(280, 240)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            #ThemeCard {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 14px;
            }
            #ThemeCard:hover {
                border: 1px solid #89b4fa;
                background-color: #1e1e2e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image Container
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(280, 160)
        self.image_label.setStyleSheet("color: #6c7086; background-color: #11111b; border-top-left-radius: 14px; border-top-right-radius: 14px; border-bottom: 1px solid #313244;")
        layout.addWidget(self.image_label)
        
        # Content Container
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 12, 15, 12)
        content_layout.setSpacing(4)

        self.name_label = QLabel(self.theme.name)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        content_layout.addWidget(self.name_label)

        author_name = self.theme.created_by.get("name", "Unknown") if isinstance(self.theme.created_by, dict) else self.theme.created_by
        self.author_label = QLabel(f"By: {author_name}")
        self.author_label.setStyleSheet("color: #a6adc8; font-size: 13px; border: none; background: transparent;")
        content_layout.addWidget(self.author_label)
        
        content_layout.addStretch()
        layout.addWidget(content)

        self.image_fetcher = CoverImageFetcher(self.theme.cover_image)
        ThemeCard._active_fetchers.append(self.image_fetcher)
        self.image_fetcher.image_loaded.connect(self.on_image_loaded)
        self.image_fetcher.error_occurred.connect(self.on_image_error)
        self.image_fetcher.finished.connect(lambda f=self.image_fetcher: ThemeCard._active_fetchers.remove(f) if f in ThemeCard._active_fetchers else None)
        self.image_fetcher.start()

    def on_image_loaded(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")

    def on_image_error(self, message):
        self.image_label.setText(ERROR_NO_COVER_IMAGE)
        self.image_label.setPixmap(QPixmap())

class ImageCarousel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_image_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(15)

        self.carousel_widget = QStackedWidget()
        self.carousel_widget.setMinimumSize(800, 450)
        self.carousel_widget.setStyleSheet("border-radius: 12px; background-color: #11111b; border: 1px solid #313244;")
        
        btn_style = """
            QPushButton { background-color: #313244; border: none; border-radius: 20px; font-size: 18px; color: #cdd6f4; min-width: 40px; min-height: 40px; }
            QPushButton:hover { background-color: #45475a; color: #ffffff; }
            QPushButton:disabled { background-color: transparent; color: transparent; }
        """

        self.prev_button = QPushButton("◀")
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.setStyleSheet(btn_style)
        self.prev_button.clicked.connect(self.previous_image)
        
        self.next_button = QPushButton("▶")
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setStyleSheet(btn_style)
        self.next_button.clicked.connect(self.next_image)
        
        nav_layout.addWidget(self.prev_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        nav_layout.addWidget(self.carousel_widget, 1) 
        nav_layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        main_layout.addLayout(nav_layout, 1)

        self.image_counter = QLabel("0 / 0")
        self.image_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_counter.setStyleSheet("font-size: 14px; color: #a6adc8; padding-top: 10px;")
        main_layout.addWidget(self.image_counter)

    def load_images(self, images_data):
        self.clear_carousel()
        pixmaps = []
        for data in (images_data or []):
            p = QPixmap()
            p.loadFromData(data)
            if not p.isNull(): pixmaps.append(p)
            
        if not pixmaps:
            self.show_error_message("No images available.")
            return
            
        for pixmap in pixmaps:
            scaled = pixmap.scaled(self.carousel_widget.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            label = QLabel()
            label.setPixmap(scaled)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.carousel_widget.addWidget(label)
        
        self.current_images = pixmaps
        self.current_image_index = 0
        self.update_navigation()
        self.carousel_widget.setCurrentIndex(0)
    
    def show_loading(self):
        self.clear_carousel()
        lbl = QLabel("Loading images...")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #a6adc8;")
        self.carousel_widget.addWidget(lbl)
        self.update_navigation()
    
    def show_error_message(self, message):
        self.clear_carousel()
        lbl = QLabel(message)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 14px; color: #f38ba8;")
        self.carousel_widget.addWidget(lbl)
        self.update_navigation()
    
    def clear_carousel(self):
        while self.carousel_widget.count() > 0:
            w = self.carousel_widget.widget(0)
            self.carousel_widget.removeWidget(w)
            w.deleteLater()
        self.current_images = []
        self.current_image_index = 0
    
    def update_navigation(self):
        total = len(self.current_images)
        if total <= 1:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.image_counter.setText(f"{total} / {total}" if total else "")
        else:
            self.prev_button.setEnabled(self.current_image_index > 0)
            self.next_button.setEnabled(self.current_image_index < total - 1)
            self.image_counter.setText(f"{self.current_image_index + 1} / {total}")
            
    def previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()
            
    def next_image(self):
        if self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.carousel_widget.setCurrentIndex(self.current_image_index)
            self.update_navigation()
