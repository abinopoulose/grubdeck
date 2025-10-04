#!/bin/bash

set -e

# --- Configuration ---
APP_NAME="grubdeck"
VERSION="1.0.0"
ARCHITECTURE="all"
MAINTAINER="abino <abino@envyy>"
DESCRIPTION="A grub theme customizer for RPM-based systems."
STAGING_DIR="./staging"
SOURCE_DIR="./src"
ICON_SOURCE="./grubdeck-logo.png"
DISPLAY_NAME="Grub Deck"
DEPENDENCIES="python3, python3-qt6, git"

echo "Starting RPM package creation for ${APP_NAME}..."

# 1. Cleanup old package file
echo "Removing old package file (if it exists)..."
rm -f "${APP_NAME}.rpm"

# 2. Check for fpm (required dependency)
if ! command -v fpm &> /dev/null
then
    echo "Error: fpm (Effing Package Management) is not installed." >&2
    exit 1
fi

# 3. Create the temporary staging directory structure
echo "Creating staging directory structure..."
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/usr/lib/${APP_NAME}"
mkdir -p "${STAGING_DIR}/usr/bin"
mkdir -p "${STAGING_DIR}/usr/share/applications"
mkdir -p "${STAGING_DIR}/usr/share/pixmaps"

# 4. Copy application files and logo
echo "Copying application files..."
cp -r "${SOURCE_DIR}/." "${STAGING_DIR}/usr/lib/${APP_NAME}/"
cp "${ICON_SOURCE}" "${STAGING_DIR}/usr/share/pixmaps/${APP_NAME}.png"

# 5. Create the application wrapper script
echo "Creating wrapper script for /usr/bin..."
# The wrapper script launches the python app.
printf '#!/bin/bash\n/usr/bin/python3 /usr/lib/%s/main.py\n' "${APP_NAME}" > "${STAGING_DIR}/usr/bin/${APP_NAME}"
chmod 0755 "${STAGING_DIR}/usr/bin/${APP_NAME}"

# 6. Create the Desktop Entry file
echo "Creating desktop entry file..."
cat > "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=${DISPLAY_NAME}
Comment=A GRUB theme customizer
Exec=${APP_NAME}
Icon=${APP_NAME}.png
Terminal=false
Type=Application
Categories=System;Settings;Utility;
EOF

# 7. Build the .rpm package using fpm
echo "Building the .rpm package..."
fpm -s dir -t rpm \
    -n "${APP_NAME}" \
    -v "${VERSION}" \
    --iteration 1 \
    --rpm-os linux \
    --license "MIT" \
    --category "System" \
    --url "https://github.com/abinopoulose/grubdeck" \
    --maintainer "${MAINTAINER}" \
    --description "${DESCRIPTION}" \
    --depends "python3" \
    --depends "python3-qt6" \
    --depends "git" \
    --chdir "${STAGING_DIR}" \
    -p "${APP_NAME}.rpm" \
    . # Build everything in the staging directory

echo "Package creation complete!"
echo "Your RPM package is ready: ${APP_NAME}.rpm"

# 8. Clean up the temporary directory..."
echo "Cleaning up temporary directory..."
rm -rf "${STAGING_DIR}"

echo "Done."
