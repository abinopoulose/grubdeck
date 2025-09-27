import webbrowser
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QStackedWidget,
                             QMessageBox, QApplication, QGridLayout, QLineEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSize

from constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, ERROR_NO_THEMES
from models import Theme
from ui_widgets import ThemeCard, ImageCarousel, InstallationProgressDialog
from theme_fetcher import ThemeFetcher, CarouselImageFetcher
from theme_installer import ThemeInstaller

class GrubThemeManagerApp(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(QSize(800, 600))
        
        self.current_theme: Theme = None
        self.installer_thread = None
        self.progress_dialog = None
        self.fetcher_thread = None
        self.carousel_fetcher_thread = None
        self.themes_data: list[Theme] = []
        
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
        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        self.header_h_layout = QHBoxLayout()
        self.header_h_layout.setContentsMargins(0, 0, 0, 0)
        self.header_h_layout.setSpacing(10)

        self.title_label = QLabel("GrubDeck")
        self.title_label.setFont(QFont("Arial", 28, QFont.Weight.ExtraBold))
        self.title_label.setStyleSheet("color: #333;")
        self.header_h_layout.addWidget(self.title_label)

        self.full_search_bar = QLineEdit()
        self.full_search_bar.setPlaceholderText("Search for themes...")
        self.full_search_bar.setStyleSheet("""
            QLineEdit { padding: 10px; border: 1px solid #ccc; border-radius: 12px; font-size: 16px; }
        """)
        self.full_search_bar.textChanged.connect(self.filter_themes)
        self.header_h_layout.addWidget(self.full_search_bar)

        self.search_icon_button = QPushButton("🔍")
        self.search_icon_button.setFixedSize(40, 40)
        self.search_icon_button.setStyleSheet("""
            QPushButton { border: none; border-radius: 20px; background-color: #f0f0f0; font-size: 18px; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.search_icon_button.clicked.connect(lambda: self.toggle_search_mode(True))
        self.header_h_layout.addWidget(self.search_icon_button)

        self.search_close_button = QPushButton("✕")
        self.search_close_button.setFixedSize(35, 35)
        self.search_close_button.setStyleSheet("""
            QPushButton { border: none; border-radius: 17px; background-color: transparent; font-size: 16px; color: #888; }
            QPushButton:hover { color: #333; }
        """)
        self.search_close_button.clicked.connect(lambda: self.toggle_search_mode(False))
        self.header_h_layout.addWidget(self.search_close_button)
        
        layout.addLayout(self.header_h_layout)

        self.theme_grid_layout = QGridLayout()
        self.theme_grid_layout.setSpacing(25) 
        self.theme_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.grid_container = QWidget()
        
        self.grid_wrapper_layout = QVBoxLayout(self.grid_container)
        self.grid_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        h_center_layout = QHBoxLayout()
        h_center_layout.setContentsMargins(0, 0, 0, 0)
        h_center_layout.addStretch(1)
        h_center_layout.addLayout(self.theme_grid_layout)
        h_center_layout.addStretch(1)
        
        self.grid_wrapper_layout.addLayout(h_center_layout)
        
        self.grid_wrapper_layout.addStretch(1) 

        self.scroll_area.setWidget(self.grid_container)
        
        layout.addWidget(self.scroll_area, 1) 
        
        self.toggle_search_mode(False)
    
    def toggle_search_mode(self, expanded):
        if expanded:
            self.search_icon_button.hide()
            self.title_label.setFixedWidth(200) 
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.full_search_bar.show()
            self.search_close_button.show()
            self.full_search_bar.setFocus()
            self.header_h_layout.setStretchFactor(self.title_label, 0)
            self.header_h_layout.setStretchFactor(self.full_search_bar, 1)
        else:
            self.full_search_bar.hide()
            self.search_close_button.hide()
            self.full_search_bar.clear()
            self.filter_themes()
            self.title_label.setFixedWidth(self.width() - 100) 
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.search_icon_button.show()
            self.header_h_layout.setStretchFactor(self.title_label, 1)
            self.header_h_layout.setStretchFactor(self.full_search_bar, 0)
        
        QApplication.processEvents()

    
    def setup_preview_page(self):
        layout = QVBoxLayout(self.preview_page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        header_h_layout = QHBoxLayout()
        header_h_layout.setContentsMargins(0, 0, 0, 0)
        header_h_layout.setSpacing(15)
        
        self.back_button = QPushButton("◀ Back")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; color: #007acc; font-size: 16px; text-align: left; padding: 5px 10px 5px 0px; }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.back_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.home_page))
        header_h_layout.addWidget(self.back_button)

        self.preview_name_label = QLabel()
        self.preview_name_label.setFont(QFont("Arial", 24, QFont.Weight.ExtraBold))
        self.preview_name_label.setStyleSheet("color: #333;")
        self.preview_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        header_h_layout.addWidget(self.preview_name_label, 1)

        layout.addLayout(header_h_layout)
        
        self.image_carousel = ImageCarousel()
        self.image_carousel.setMinimumHeight(400) 
        layout.addWidget(self.image_carousel)

        self.preview_author_label = QLabel()
        self.preview_author_label.setStyleSheet("color: #666; font-size: 16px; margin-top: 10px; margin-bottom: 5px;") 
        layout.addWidget(self.preview_author_label) 
        
        self.preview_description_label = QLabel()
        self.preview_description_label.setWordWrap(True)
        self.preview_description_label.setStyleSheet("font-size: 14px; color: #444; margin-bottom: 20px;")
        layout.addWidget(self.preview_description_label)
        
        button_h_layout = QHBoxLayout()
        button_h_layout.setSpacing(15) 
        
        self.repo_link_button = QPushButton("View on GitHub")
        self.repo_link_button.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border: none; border-radius: 8px; padding: 10px 20px; font-size: 14px; }
            QPushButton:hover { background-color: #555; }
        """)
        self.repo_link_button.clicked.connect(self.open_repo_link)
        button_h_layout.addWidget(self.repo_link_button, 1) 

        self.install_button = QPushButton("Install Theme")
        self.install_button.setStyleSheet("""
            QPushButton { background-color: #2e8b57; color: white; border: none; border-radius: 8px; padding: 10px 20px; font-size: 14px; }
            QPushButton:hover { background-color: #3cb371; }
        """)
        self.install_button.clicked.connect(self.install_theme)
        button_h_layout.addWidget(self.install_button, 1)

        layout.addLayout(button_h_layout)
        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.central_widget.currentWidget() == self.home_page and self.themes_data:
            self._repopulate_grid(self.themes_data)

    def _repopulate_grid(self, themes_to_display: list[Theme]):
        for i in reversed(range(self.theme_grid_layout.count())):
            item = self.theme_grid_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                self.theme_grid_layout.removeWidget(widget)
                widget.deleteLater()
            
        if not themes_to_display:
            no_themes_label = QLabel(ERROR_NO_THEMES)
            no_themes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.theme_grid_layout.addWidget(no_themes_label, 0, 0)
            return

        CARD_WIDTH = 250
        SPACING = 25 
        available_width = self.scroll_area.viewport().width() - 50

        if (CARD_WIDTH + SPACING) > 0:
            num_columns = int((available_width - 1 + SPACING) / (CARD_WIDTH + SPACING))
        else:
            num_columns = 2 
            
        final_num_columns = max(2, min(4, num_columns))
        
        col, row = 0, 0
        for theme in themes_to_display:
            card = ThemeCard(theme)
            card.mousePressEvent = lambda event, t=theme: self.show_theme_preview(t)
            self.theme_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= final_num_columns: 
                col = 0
                row += 1
        
        QApplication.processEvents()

    def start_theme_fetching(self):
        self.fetcher_thread = ThemeFetcher()
        self.fetcher_thread.themes_fetched.connect(self.populate_theme_grid)
        self.fetcher_thread.start()
    
    def populate_theme_grid(self, themes_data):
        self.themes_data = themes_data
        self._repopulate_grid(self.themes_data)
    
    def filter_themes(self):
        query = self.full_search_bar.text().lower()
        if query:
            filtered_themes = [
                t for t in self.themes_data
                if query in t.name.lower() or query in t.created_by.lower()
            ]
        else:
            filtered_themes = self.themes_data
        
        self._repopulate_grid(filtered_themes)

    def show_theme_preview(self, theme: Theme):
        self.current_theme = theme
        self.preview_name_label.setText(self.current_theme.name)
        self.preview_author_label.setText(f"By: {self.current_theme.created_by}")
        self.preview_description_label.setText(self.current_theme.description)

        self.image_carousel.show_loading()
        self.carousel_fetcher_thread = CarouselImageFetcher(self.current_theme.carousel_images)
        self.carousel_fetcher_thread.images_loaded.connect(self.image_carousel.load_images)
        self.carousel_fetcher_thread.error_occurred.connect(self.image_carousel.show_error_message)
        self.carousel_fetcher_thread.start()

        self.central_widget.setCurrentWidget(self.preview_page)

    def open_repo_link(self):
        if self.current_theme and self.current_theme.repo_link:
            webbrowser.open(self.current_theme.repo_link)

    def install_theme(self):
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
        if self.progress_dialog:
            self.progress_dialog.update_progress(percentage, message)
    
    def on_installation_completed(self, success, message):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.install_button.setEnabled(True)
        self.install_button.setText("Install Theme")
        
        if success:
            QMessageBox.information(self, "Installation Complete", message)
        else:
            QMessageBox.critical(self, "Installation Failed", message)
