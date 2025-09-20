#!/usr/bin/env python3
"""
GrubDeck - GRUB Theme Manager
A PyQt6 application for managing GRUB themes
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the current directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import ensure_sudo_privileges
from ui_components import GrubThemeManagerApp


def main():
    """Main entry point for the application"""
    # Check for sudo privileges before starting the app
    ensure_sudo_privileges()
    
    # Create and run the application
    app = QApplication(sys.argv)
    window = GrubThemeManagerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()