# UI components and dialogs for GrubDeck

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QLabel, QPushButton, QScrollArea,
                             QProgressBar, QMessageBox, QDialog, QVBoxLayout as QDialogVBoxLayout,
                             QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from constants import (WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, THEME_LIST_WIDTH,
                       PROGRESS_DIALOG_WIDTH, PROGRESS_DIALOG_HEIGHT, ERROR_NO_THEMES)
from image_carousel import ImageCarousel


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


class GrubThemeManagerApp(QMainWindow):
    """Main application window for GRUB Theme Manager"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.current_theme = None
        self.installer_thread = None
        self.progress_dialog = None
        self.image_fetcher = None
        self.fetcher_thread = None
        self.themes_data = []
        
        self.setup_ui()
        self.start_theme_fetching()
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left pane for theme list
        self.theme_list_widget = QListWidget()
        self.theme_list_widget.setFixedWidth(THEME_LIST_WIDTH)
        main_layout.addWidget(self.theme_list_widget)
        self.theme_list_widget.itemSelectionChanged.connect(self.display_theme_details)
        
        # Add loading indicator for theme list
        self.theme_loading_label = QLabel("Loading themes...")
        self.theme_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_loading_label.setStyleSheet("font-size: 14px; color: #666; padding: 20px;")
        self.theme_list_widget.addItem("Loading themes...")

        # Right pane for theme details and carousel
        self.details_pane = QWidget()
        details_layout = QVBoxLayout(self.details_pane)
        main_layout.addWidget(self.details_pane)

        self.theme_name_label = QLabel("Select a theme")
        self.theme_name_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        details_layout.addWidget(self.theme_name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Image carousel
        self.image_carousel = ImageCarousel()
        details_layout.addWidget(self.image_carousel)

        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        details_layout.addWidget(self.description_label)

        self.install_button = QPushButton("Install Theme")
        self.install_button.setEnabled(False)
        self.install_button.clicked.connect(self.install_theme)
        details_layout.addWidget(self.install_button)
    
    def start_theme_fetching(self):
        """Start fetching themes from the repository"""
        from theme_fetcher import ThemeFetcher
        self.fetcher_thread = ThemeFetcher()
        self.fetcher_thread.themes_fetched.connect(self.populate_theme_list)
        self.fetcher_thread.start()
    
    def populate_theme_list(self, themes_data):
        """Populate the theme list with fetched data"""
        self.themes_data = themes_data
        # Clear the loading message
        self.theme_list_widget.clear()
        
        if themes_data:
            for theme in themes_data:
                self.theme_list_widget.addItem(theme.name)
        else:
            self.theme_list_widget.addItem(ERROR_NO_THEMES)

    def display_theme_details(self):
        """Display details for the selected theme"""
        selected_item = self.theme_list_widget.currentItem()
        if not selected_item:
            return

        theme_name = selected_item.text()
        
        # Skip if it's a loading or error message
        if theme_name in ["Loading themes...", ERROR_NO_THEMES]:
            return
            
        self.current_theme = next((theme for theme in self.themes_data if theme.name == theme_name), None)

        if self.current_theme:
            # Show loading state for theme details
            self.theme_name_label.setText(f"Loading {self.current_theme.name}...")
            self.description_label.setText("Fetching theme details and previews...")
            self.install_button.setEnabled(False)
            self.install_button.setText("Loading...")
            
            # Update carousel with loading state
            self.update_carousel(self.current_theme.repo_link)

    def update_carousel(self, repo_link):
        """Update the image carousel with images from the theme repository"""
        # Show loading message
        self.image_carousel.show_loading()
        
        # Start fetching images
        from theme_fetcher import CarouselImageFetcher
        self.image_fetcher = CarouselImageFetcher(repo_link)
        self.image_fetcher.images_loaded.connect(self.on_images_loaded)
        self.image_fetcher.error_occurred.connect(self.on_image_error)
        self.image_fetcher.start()

    def on_images_loaded(self, image_paths, temp_dir):
        """Handle successful image loading"""
        self.image_carousel.load_images(image_paths, temp_dir)
        
        # Update UI with theme details now that images are loaded
        if self.current_theme:
            self.theme_name_label.setText(self.current_theme.name)
            self.description_label.setText(self.current_theme.description)
            self.install_button.setEnabled(True)
            self.install_button.setText("Install Theme")

    def on_image_error(self, error_message):
        """Handle image loading error"""
        self.image_carousel.show_error_message(f"Error loading images: {error_message}")
        
        # Still update UI with theme details even if images failed
        if self.current_theme:
            self.theme_name_label.setText(self.current_theme.name)
            self.description_label.setText(self.current_theme.description)
            self.install_button.setEnabled(True)
            self.install_button.setText("Install Theme")

    def install_theme(self):
        """Install the selected theme"""
        if not self.current_theme:
            return

        # Disable install button during installation
        self.install_button.setEnabled(False)
        self.install_button.setText("Installing...")
        
        # Create and show progress dialog
        self.progress_dialog = InstallationProgressDialog(self)
        self.progress_dialog.show()
        
        # Create and start installer thread
        from theme_installer import ThemeInstaller
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
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Re-enable install button
        self.install_button.setEnabled(True)
        self.install_button.setText("Install Theme")
        
        # Show result message
        if success:
            QMessageBox.information(self, "Installation Complete", message)
        else:
            QMessageBox.critical(self, "Installation Failed", message)

    def closeEvent(self, event):
        """Clean up when the application is closed"""
        self.image_carousel.cleanup_temp_dirs()
        event.accept()
