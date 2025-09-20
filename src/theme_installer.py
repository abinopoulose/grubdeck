# Theme installation functionality for GrubDeck

import os
import shutil
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
from constants import (GRUB_CONFIG_PATH, GRUB_CONFIG_BACKUP_PATH, GRUB_THEMES_BASE_PATH, 
                       TEMP_THEME_DIR_PREFIX, GRUB_UPDATE_COMMANDS, ERROR_GRUB_UPDATE_FAILED)
from models import ThemeInstallationResult, InstallationProgress


class ThemeInstaller(QThread):
    """Thread for installing GRUB themes"""
    progress_updated = pyqtSignal(int, str)  # progress_percentage, status_message
    installation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, theme_name, repo_link):
        super().__init__()
        self.theme_name = theme_name
        self.repo_link = repo_link
        self.temp_dir = f"/tmp/{TEMP_THEME_DIR_PREFIX}/{theme_name}"
    
    def run(self):
        """Install the theme"""
        try:
            self.progress_updated.emit(10, "Preparing installation...")
            
            # Create temp directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
            
            self.progress_updated.emit(20, "Downloading theme from repository...")
            
            # Clone the repository
            clone_cmd = ["git", "clone", "--depth", "1", self.repo_link, self.temp_dir]
            result = subprocess.run(clone_cmd, capture_output=True, text=True, check=True)
            
            self.progress_updated.emit(50, "Installing theme files...")
            
            # Create themes directory and copy files
            theme_dir = f"{GRUB_THEMES_BASE_PATH}/{self.theme_name}"
            os.makedirs(theme_dir, exist_ok=True)
            
            theme_source = os.path.join(self.temp_dir, "theme")
            if os.path.exists(theme_source):
                shutil.copytree(theme_source, theme_dir, dirs_exist_ok=True)
            else:
                # If no theme folder, copy the entire repo
                for item in os.listdir(self.temp_dir):
                    src = os.path.join(self.temp_dir, item)
                    dst = os.path.join(theme_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            
            self.progress_updated.emit(70, "Updating GRUB configuration...")
            
            # Backup and update grub config
            self._update_grub_config(theme_dir)
            
            self.progress_updated.emit(85, "Updating GRUB bootloader...")
            
            # Update grub
            if not self._update_grub():
                self.installation_completed.emit(False, ERROR_GRUB_UPDATE_FAILED)
                return
            
            self.progress_updated.emit(95, "Cleaning up...")
            
            # Clean up temp directory
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            self.progress_updated.emit(100, "Installation completed successfully!")
            self.installation_completed.emit(True, f"Theme '{self.theme_name}' installed successfully!")
            
        except subprocess.CalledProcessError as e:
            self.installation_completed.emit(False, f"Installation failed: {e.stderr}")
        except Exception as e:
            self.installation_completed.emit(False, f"Installation failed: {str(e)}")
        finally:
            # Clean up temp directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _update_grub_config(self, theme_dir):
        """Update GRUB configuration file"""
        # Create backup
        subprocess.run(["sudo", "cp", GRUB_CONFIG_PATH, GRUB_CONFIG_BACKUP_PATH], check=True)
        
        # Remove existing GRUB_THEME line and add new one
        theme_path = f"{theme_dir}/theme.txt"
        
        # Read current config
        with open(GRUB_CONFIG_PATH, 'r') as f:
            lines = f.readlines()
        
        # Remove existing GRUB_THEME lines
        lines = [line for line in lines if not line.strip().startswith('GRUB_THEME=')]
        
        # Add new GRUB_THEME line
        lines.append(f'GRUB_THEME="{theme_path}"\n')
        
        # Write back to file
        with open(GRUB_CONFIG_PATH, 'w') as f:
            f.writelines(lines)
    
    def _update_grub(self):
        """Update GRUB bootloader using available commands"""
        grub_updated = False
        for cmd in GRUB_UPDATE_COMMANDS:
            try:
                subprocess.run(["sudo"] + cmd, check=True, capture_output=True)
                grub_updated = True
                break
            except subprocess.CalledProcessError:
                continue
        return grub_updated
