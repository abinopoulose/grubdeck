import os

# Application settings
WINDOW_TITLE = "Grub Deck - Modern GRUB Theme Manager"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

PROGRESS_DIALOG_WIDTH = 400
PROGRESS_DIALOG_HEIGHT = 150

# URL for the theme index
# This URL points to the correct JSON index file in the GitHub repository
THEME_INDEX_URL = "https://raw.githubusercontent.com/abinopoulose/grubdeck/refs/heads/be-index/index.json"

# GRUB configuration paths (for installer script)
GRUB_CONFIG_PATH = "/etc/default/grub"
GRUB_THEMES_DIR = "/boot/grub/themes"

# Error messages
ERROR_NO_THEMES = "No themes found. Please check your internet connection."
ERROR_NO_COVER_IMAGE = "Image not available."
ERROR_INSTALLATION_FAILED = "Theme installation failed. Please check the logs."
ERROR_GRUB_UPDATE_FAILED = "GRUB configuration updated, but `update-grub` failed. Please run it manually."
