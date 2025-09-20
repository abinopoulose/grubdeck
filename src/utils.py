# Utility functions for GrubDeck

import os
import sys
from PyQt6.QtWidgets import QMessageBox, QApplication
from constants import ERROR_NO_SUDO


def check_sudo_privileges():
    """Check if the application is running with sudo privileges"""
    return os.geteuid() == 0


def show_sudo_error_and_exit():
    """Show sudo error message and exit the application"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Permission Error")
    msg_box.setText(ERROR_NO_SUDO)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
    
    sys.exit(1)


def ensure_sudo_privileges():
    """Ensure the application has sudo privileges, exit if not"""
    if not check_sudo_privileges():
        show_sudo_error_and_exit()
