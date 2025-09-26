import sys
import os
import shutil
import subprocess

# This script is designed to be executed with elevated privileges (e.g., via pkexec)
# It should ONLY perform the tasks necessary for theme installation and nothing else.

def report_progress(percentage, message):
    """Prints progress updates to stdout for the main application to read."""
    print(f"PROGRESS:{percentage}:{message}", flush=True)

def find_grub_config_and_update_command():
    """
    Identifies the correct GRUB config file and update command based on the system.
    Returns (config_path, update_command).
    """
    grub_config_path = "/etc/default/grub"
    grub_update_command = ["update-grub"]

    if os.path.exists("/boot/efi/EFI/fedora/grub.cfg"):
        grub_config_path = "/boot/efi/EFI/fedora/grub.cfg"
        grub_update_command = ["grub2-mkconfig", "-o", "/boot/efi/EFI/fedora/grub.cfg"]
    elif os.path.exists("/boot/grub2/grub.cfg"):
        grub_config_path = "/etc/default/grub"
        grub_update_command = ["grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"]
    elif os.path.exists("/boot/grub/grub.cfg"):
        grub_config_path = "/etc/default/grub"
        grub_update_command = ["update-grub"]

    return grub_config_path, grub_update_command

def run_installation():
    """
    Main function to handle the theme installation process.
    """
    # Check for correct number of arguments
    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments.")
        sys.exit(1)
        
    theme_name = sys.argv[1]
    repo_link = sys.argv[2]
    
    report_progress(5, f"Starting installation of '{theme_name}'...")

    try:
        # --- 1. Clone the theme repository ---
        report_progress(10, "Cloning theme repository...")
        temp_dir = "/tmp/grubdeck_theme_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # We need the full repository link, but only the last part for the directory name
        repo_dir_name = repo_link.split('/')[-1].replace('.git', '')
        
        subprocess.run(
            ['git', 'clone', '--depth=1', repo_link, temp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        report_progress(40, "Repository cloned successfully.")
        
        # --- 2. Move the theme to the GRUB themes directory ---
        report_progress(50, "Moving theme to GRUB directory...")
        grub_themes_path = "/boot/grub/themes"
        theme_destination = os.path.join(grub_themes_path, theme_name)
        
        if os.path.exists(theme_destination):
            shutil.rmtree(theme_destination)
            
        shutil.copytree(temp_dir, theme_destination)
        
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        
        report_progress(70, "Theme files copied.")

        # --- 3. Update the GRUB configuration ---
        report_progress(80, "Updating GRUB configuration...")
        
        grub_config_path, grub_update_command = find_grub_config_and_update_command()

        with open(grub_config_path, 'r') as f:
            lines = f.readlines()
        
        with open(grub_config_path, 'w') as f:
            for line in lines:
                if line.startswith("GRUB_THEME="):
                    f.write(f'GRUB_THEME="/boot/grub/themes/{theme_name}/theme.txt"\n')
                else:
                    f.write(line)
            
            # Add GRUB_THEME if it wasn't found
            if not any(line.startswith("GRUB_THEME=") for line in lines):
                f.write(f'GRUB_THEME="/boot/grub/themes/{theme_name}/theme.txt"\n')
        
        report_progress(90, "GRUB configuration updated.")

        # --- 4. Run GRUB update command to apply changes ---
        report_progress(95, "Applying changes with update-grub...")
        subprocess.run(
            grub_update_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        report_progress(100, "Installation complete.")
        sys.exit(0) # Success
        
    except FileNotFoundError as e:
        print(f"Error: A required command was not found: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}. Output: {e.stderr}", file=sys.stderr)
        # Check for GRUB update failure specifically
        if 'grub-mkconfig' in e.cmd[0] or 'update-grub' in e.cmd[0]:
            sys.exit(2) # Specific code for GRUB update failure
        else:
            sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_installation()
