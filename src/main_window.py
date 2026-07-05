import webbrowser
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QStackedWidget,
                             QMessageBox, QApplication, QGridLayout, QLineEdit, QSizePolicy, QComboBox)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize, QObject, QEvent, QRect

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
        self.setMinimumSize(QSize(900, 700))
        
        self.current_theme = None
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

    def closeEvent(self, event):
        if hasattr(self, 'fetcher') and self.fetcher.isRunning():
            self.fetcher.terminate()
            self.fetcher.wait()
        if hasattr(self, 'carousel_fetcher') and getattr(self, 'carousel_fetcher').isRunning():
            self.carousel_fetcher.terminate()
            self.carousel_fetcher.wait()
        event.accept()

    def setup_home_page(self):
        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(40, 40, 40, 20)
        layout.setSpacing(25)

        # Header Area
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.title_label = QLabel("GrubDeck")
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #cdd6f4;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search themes...")
        self.search_bar.setFixedSize(300, 45)
        self.search_bar.setStyleSheet("""
            QLineEdit { background-color: #181825; border: 1px solid #313244; border-radius: 22px; padding: 0 20px; color: #cdd6f4; font-size: 15px; }
            QLineEdit:focus { border: 1px solid #89b4fa; }
        """)
        self.search_bar.textChanged.connect(self.filter_themes)
        header_layout.addWidget(self.search_bar)
        
        layout.addLayout(header_layout)

        # Grid Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area, 1)
    
    def setup_preview_page(self):
        layout = QVBoxLayout(self.preview_page)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        # Top Bar
        top_bar = QHBoxLayout()
        
        self.back_btn = QPushButton("◀ Back to Library")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("QPushButton { background: transparent; color: #89b4fa; font-size: 16px; font-weight: bold; border: none; text-align: left; } QPushButton:hover { color: #b4befe; text-decoration: underline; }")
        self.back_btn.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.home_page))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Title & Meta
        self.preview_title = QLabel()
        self.preview_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_title)

        self.preview_author = QLabel()
        self.preview_author.setStyleSheet("color: #a6adc8; font-size: 15px;")
        self.preview_author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_author)

        # Carousel
        self.carousel = ImageCarousel()
        layout.addWidget(self.carousel, 1)

        # Initialize the size selector dropdown
        self.size_selector = QComboBox()
        self.size_selector.setFixedHeight(40)
        self.size_selector.setStyleSheet("""
            QComboBox { 
                background-color: #181825; 
                color: #cdd6f4; 
                border: 1px solid #313244; 
                border-radius: 8px; 
                padding: 5px 15px;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #181825; 
                color: #cdd6f4; 
                selection-background-color: #313244; 
                border: 1px solid #313244;
            }
        """)
        layout.addWidget(self.size_selector)
        
        # Description
        self.preview_desc = QLabel()
        self.preview_desc.setWordWrap(True)
        self.preview_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_desc.setStyleSheet("color: #bac2de; font-size: 15px; margin: 10px 40px;")
        layout.addWidget(self.preview_desc)

        # Action Buttons (Centered cleanly)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.setSpacing(20)

        self.repo_btn = QPushButton("View Source")
        self.repo_btn.setFixedSize(180, 45)
        self.repo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repo_btn.setStyleSheet("QPushButton { background-color: #313244; color: #cdd6f4; border-radius: 22px; font-weight: bold; font-size: 15px; } QPushButton:hover { background-color: #45475a; }")
        self.repo_btn.clicked.connect(self.open_repo)
        btn_layout.addWidget(self.repo_btn)

        self.install_btn = QPushButton("Install Theme")
        self.install_btn.setFixedSize(180, 45)
        self.install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_btn.setStyleSheet("QPushButton { background-color: #a6e3a1; color: #11111b; border-radius: 22px; font-weight: bold; font-size: 15px; } QPushButton:hover { background-color: #94e2d5; }")
        self.install_btn.clicked.connect(self.install_theme)
        btn_layout.addWidget(self.install_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Force the grip to hover in the bottom right corner
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())
            self.size_grip.raise_()
            
        if self.central_widget.currentWidget() == self.home_page and self.themes_data:
            self._repopulate_grid(self.themes_data)

    def _repopulate_grid(self, themes):
        CARD_WIDTH = 280
        SPACING = 25 
        available_width = self.scroll_area.viewport().width() - 40
        num_columns = max(1, int(available_width // (CARD_WIDTH + SPACING)))
        
        current_theme_ids = [t.name for t in themes]
        if getattr(self, '_last_columns', 0) == num_columns and getattr(self, '_last_themes', []) == current_theme_ids:
            return
            
        self._last_columns = num_columns
        self._last_themes = current_theme_ids
        
        # Clean up old containers (handles both old and new architecture)
        if hasattr(self, 'wrapper_widget') and self.wrapper_widget:
            self.wrapper_widget.hide()
            self.wrapper_widget.deleteLater()
        elif hasattr(self, 'grid_container') and self.grid_container:
            self.grid_container.hide()
            self.grid_container.deleteLater()
            
        # THE FIX: A wrapper widget with stretching margins on both sides
        self.wrapper_widget = QWidget()
        self.wrapper_widget.setStyleSheet("background-color: transparent;")
        wrapper_layout = QHBoxLayout(self.wrapper_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(SPACING)
        # The cards stay left-aligned *inside* their block
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Squeeze the grid block into the exact center of the screen
        wrapper_layout.addStretch(1)
        wrapper_layout.addWidget(self.grid_container)
        wrapper_layout.addStretch(1)
        
        self.scroll_area.setWidget(self.wrapper_widget)
        
        if not themes:
            lbl = QLabel(ERROR_NO_THEMES)
            lbl.setStyleSheet("color: #a6adc8; font-size: 16px;")
            self.grid_layout.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for theme in themes:
            card = ThemeCard(theme)
            card.mousePressEvent = lambda e, t=theme: self.show_preview(t)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= num_columns:
                col = 0
                row += 1

    def start_theme_fetching(self):
        self.fetcher = ThemeFetcher()
        self.fetcher.themes_fetched.connect(self.populate_grid)
        self.fetcher.start()
        
    def populate_grid(self, themes):
        self.themes_data = themes
        self._repopulate_grid(self.themes_data)

    def filter_themes(self):
        query = self.search_bar.text().lower()
        filtered = [t for t in self.themes_data if query in t.name.lower() or query in t.created_by.lower()] if query else self.themes_data
        self._repopulate_grid(filtered)

    def show_preview(self, theme):
        self.current_theme = theme
        self.preview_title.setText(theme.name)
        self.preview_author.setText(f"Created by {theme.created_by.get('name', 'Unknown') if isinstance(theme.created_by, dict) else theme.created_by}")
        self.preview_desc.setText(theme.description)
        
        self.size_selector.clear()
        for opt in getattr(theme, 'size_options', []):
            self.size_selector.addItem(opt.get('name', 'Unknown Size'))
        
        self.carousel.show_loading()
        self.carousel_fetcher = CarouselImageFetcher(theme.carousel_images)
        self.carousel_fetcher.images_loaded.connect(self.carousel.load_images)
        self.carousel_fetcher.error_occurred.connect(self.carousel.show_error_message)
        self.carousel_fetcher.start()
        
        self.central_widget.setCurrentWidget(self.preview_page)

    def open_repo(self):
        if not self.current_theme: return
        
        selected_index = self.size_selector.currentIndex()
        if selected_index < 0: return # Safety check
        
        size_opt = self.current_theme.size_options[selected_index]
        repo_link = size_opt.get('repo_link')
        
        if repo_link:
            import webbrowser
            webbrowser.open(repo_link)

    def install_theme(self):
        if not self.current_theme: return
        
        selected_index = self.size_selector.currentIndex()
        if selected_index < 0: return # Safety check
        
        size_opt = self.current_theme.size_options[selected_index]
        
        self.install_btn.setEnabled(False)
        self.install_btn.setText("Installing...")
        
        self.progress_dialog = InstallationProgressDialog(self)
        self.progress_dialog.show()
        
        self.installer = ThemeInstaller(self.current_theme.name, size_opt['repo_link'], size_opt['branch_name'])
        self.installer.progress_updated.connect(self.progress_dialog.update_progress)
        self.installer.installation_completed.connect(self.on_install_done)
        self.installer.start()

    def on_install_done(self, success, message):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
        
        self.install_btn.setEnabled(True)
        self.install_btn.setText("Install Theme")
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
