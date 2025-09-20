# Configuration constants for GrubDeck

# GitHub API URLs
GITHUB_THEMES_INDEX_URL = "https://raw.githubusercontent.com/abinopoulose/grubdeck/refs/heads/be-index/index.json"
GITHUB_API_BASE_URL = "https://api.github.com/repos"

# File paths
GRUB_CONFIG_PATH = "/etc/default/grub"
GRUB_CONFIG_BACKUP_PATH = "/etc/default/grub.bak"
GRUB_THEMES_BASE_PATH = "/boot/grub/themes"
TEMP_DIR_PREFIX = "grub_carousel_"
TEMP_THEME_DIR_PREFIX = "grub-themes"

# GRUB update commands (different distributions may use different commands)
GRUB_UPDATE_COMMANDS = [
    ["update-grub"],
    ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
    ["grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"],
    ["grub2-mkconfig", "-o", "/boot/efi/EFI/fedora/grub.cfg"]
]

# UI Configuration
WINDOW_TITLE = "GRUB Theme Manager"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
THEME_LIST_WIDTH = 250
CAROUSEL_MIN_HEIGHT = 400
PROGRESS_DIALOG_WIDTH = 400
PROGRESS_DIALOG_HEIGHT = 150

# Image file extensions
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

# Error messages
ERROR_NO_SUDO = "This application requires sudo privileges to install GRUB themes. Please run with sudo."
ERROR_NO_THEMES = "No themes available"
ERROR_NO_IMAGES = "No images found in view folder"
ERROR_INSTALLATION_FAILED = "Installation failed"
ERROR_GRUB_UPDATE_FAILED = "Theme installed but failed to update GRUB. Please run 'sudo update-grub' manually."
