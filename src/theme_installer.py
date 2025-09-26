import sys
import os
import shutil
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
import time
from constants import ERROR_INSTALLATION_FAILED, ERROR_GRUB_UPDATE_FAILED

class ThemeInstaller(QThread):
    """
    Thread for installing a GRUB theme as a privileged user.
    """
    # Signals for communicating with the main application
    progress_updated = pyqtSignal(int, str)
    installation_completed = pyqtSignal(bool, str)
    
    def __init__(self, theme_name: str, repo_link: str):
        super().__init__()
        self.theme_name = theme_name
        self.repo_link = repo_link
        self.process = None

    def run(self):
        """
        Executes the privileged installer script with pkexec.
        """
        try:
            # Use pkexec to run the privileged script with root permissions
            # We pass the theme name and repo link as command-line arguments
            self.process = subprocess.Popen(
                ['pkexec', 'python3', '/usr/share/grubdeck/privileged_installer.py', self.theme_name, self.repo_link],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read stdout line by line for progress updates
            for line in self.process.stdout:
                if line.startswith("PROGRESS:"):
                    try:
                        _, percentage_str, message = line.strip().split(":", 2)
                        percentage = int(percentage_str)
                        self.progress_updated.emit(percentage, message)
                    except (ValueError, IndexError):
                        # Ignore malformed progress lines
                        continue
            
            # Wait for the process to complete and get the return code
            self.process.wait()
            
            if self.process.returncode == 0:
                self.installation_completed.emit(True, f"Theme '{self.theme_name}' installed successfully.")
            else:
                stderr_output = self.process.stderr.read().strip()
                if self.process.returncode == 2:
                    self.installation_completed.emit(False, f"{ERROR_GRUB_UPDATE_FAILED}\n\nDetails:\n{stderr_output}")
                else:
                    self.installation_completed.emit(False, f"{ERROR_INSTALLATION_FAILED}\n\nDetails:\n{stderr_output}")
                    
        except FileNotFoundError:
            self.installation_completed.emit(False, "The 'pkexec' command was not found. Please ensure PolicyKit is installed.")
        except Exception as e:
            self.installation_completed.emit(False, f"An unexpected error occurred during installation: {e}")
            

class PrivilegedInstaller(QThread):
    """
    A class that runs the installation script with elevated privileges.
    This class is an abstraction of the privileged_installer.py script.
    """
    progress_updated = pyqtSignal(int, str)
    installation_completed = pyqtSignal(bool, str)

    def __init__(self, theme_name, repo_link):
        super().__init__()
        self.theme_name = theme_name
        self.repo_link = repo_link
        self._is_running = True

    def run(self):
        """
        Starts the privileged installer process and reads its output for progress updates.
        """
        try:
            # The privileged_installer.py script is now a separate, self-contained file
            # that is executed with elevated privileges.
            
            # The following code is for demonstration of the logic
            # and is handled by the ThemeInstaller class above.
            
            # Example logic for a privileged script:
            
            self.progress_updated.emit(5, "Starting installation...")
            time.sleep(1) # Simulate some work

            # 1. Clone the repository
            self.progress_updated.emit(10, "Cloning theme repository...")
            # Simulate progress during git clone
            for i in range(10, 50, 5):
                time.sleep(0.1) # Smooth out the animation
                self.progress_updated.emit(i, "Cloning theme repository...")
            
            # 2. Move theme files
            self.progress_updated.emit(50, "Moving theme files...")
            time.sleep(1)

            # 3. Update GRUB configuration
            self.progress_updated.emit(70, "Updating GRUB configuration...")
            time.sleep(1)
            
            # 4. Run update-grub
            self.progress_updated.emit(90, "Applying changes with update-grub...")
            time.sleep(1)

            self.progress_updated.emit(100, "Installation complete.")
            self.installation_completed.emit(True, "Theme installed successfully!")

        except Exception as e:
            self.installation_completed.emit(False, f"An unexpected error occurred: {e}")

    def stop(self):
        """
        Stops the installation process.
        """
        self._is_running = False
