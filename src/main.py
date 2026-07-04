import sys
import traceback
import os
from datetime import datetime

def local_crash_report(exctype, value, tb):
    # Grab the error trace
    crash_log = "".join(traceback.format_exception(exctype, value, tb))
    
    # Still print to terminal so you can see it live
    print(crash_log, file=sys.stderr)
    
    try:
        # Create a safe, dedicated logs folder in the user's home directory
        log_dir = os.path.expanduser("~/.grubdeck/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"crash_{timestamp}.log")
        
        # Write the crash log to the new file
        with open(log_file, "w") as f:
            f.write("GrubDeck Crash Report\n")
            f.write("=====================\n")
            f.write(f"Time: {timestamp}\n\n")
            f.write(crash_log)
            
        print(f"\n✅ Fatal error caught. Log saved to: {log_file}")
    except Exception as e:
        print(f"\n❌ Failed to write crash log to disk: {e}")

sys.excepthook = local_crash_report


import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from main_window import GrubThemeManagerApp

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Error: The 'requests' library is required.")
        sys.exit(1)

    # Force dark window decorations on GTK/GNOME and Qt environments
    # Let the native Window Manager handle decorations and scaling
    # Force native OS window manager to draw the title bar
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Deep Dark Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#181825"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#313244"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#313244"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#89b4fa"))
    app.setPalette(palette)

    # Global Stylesheet
    app.setStyleSheet("""
        QMainWindow, QDialog { background-color: #1e1e2e; }
        QWidget { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        QScrollArea, QScrollArea > QWidget > QWidget, QStackedWidget { background-color: transparent; border: none; }
        QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0px; }
        QScrollBar::handle:vertical { background: #45475a; border-radius: 4px; min-height: 30px; }
        QScrollBar::handle:vertical:hover { background: #585b70; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QProgressBar { border: none; border-radius: 4px; background-color: #313244; color: transparent; height: 8px; }
        QProgressBar::chunk { background-color: #a6e3a1; border-radius: 4px; }
    """)

    window = GrubThemeManagerApp()
    window.show()
    sys.exit(app.exec())
