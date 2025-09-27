import sys
from PyQt6.QtWidgets import QApplication
from main_window import GrubThemeManagerApp

if __name__ == "__main__":
    # Ensure requests library is available for HTTP communication
    try:
        import requests
    except ImportError:
        print("Error: The 'requests' library is required. Please install it with: pip install requests")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = GrubThemeManagerApp()
    window.show()
    sys.exit(app.exec())
