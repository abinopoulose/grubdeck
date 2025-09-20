#!/bin/bash

set -e

# --- Configuration ---
APP_NAME="grubdeck"
VERSION="1.0.0"
ARCHITECTURE="all"
MAINTAINER="abino <abino@envyy>"
DESCRIPTION="A grub theme customizer for Debian-based systems."
DEB_BUILD_DIR="${APP_NAME}-${VERSION}-${ARCHITECTURE}"
SOURCE_DIR="./src"
ICON_SOURCE="./grubdeck-logo.png"
DISPLAY_NAME="Grub Deck"

# --- Dependencies ---
DEPENDENCIES="python3, python3-pyqt5, python3-tk, python3-pil"


echo "Starting Debian package creation for ${APP_NAME}..."

# 1. Create the temporary build directory structure
echo "Creating directory structure..."
rm -rf "${DEB_BUILD_DIR}"
mkdir -p "${DEB_BUILD_DIR}/DEBIAN"
mkdir -p "${DEB_BUILD_DIR}/usr/bin"
mkdir -p "${DEB_BUILD_DIR}/usr/share/${APP_NAME}"
mkdir -p "${DEB_BUILD_DIR}/usr/share/applications"
mkdir -p "${DEB_BUILD_DIR}/usr/share/pixmaps"

# 2. Copy application files and logo
echo "Copying application files..."
cp -r "${SOURCE_DIR}/." "${DEB_BUILD_DIR}/usr/share/${APP_NAME}/"
cp "${ICON_SOURCE}" "${DEB_BUILD_DIR}/usr/share/pixmaps/${APP_NAME}.png"

# 3. Create the control file
echo "Creating DEBIAN/control file..."
cat > "${DEB_BUILD_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Maintainer: ${MAINTAINER}
Architecture: ${ARCHITECTURE}
Depends: ${DEPENDENCIES}
Homepage: <Your Project Homepage URL>
Description: ${DESCRIPTION}
 This package installs a graphical tool for customizing GRUB themes.
 It provides a user-friendly interface to browse, preview, and install themes,
 making it easy to personalize the GRUB boot menu.
EOF

# 4. Create the application wrapper script
echo "Creating wrapper script for /usr/bin..."
# Using printf is more resilient to shell environment issues than a here-document
# for creating simple files like this.
printf '#!/bin/bash\npkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY /usr/bin/python3 /usr/share/%s/main.py\n' "${APP_NAME}" > "${DEB_BUILD_DIR}/usr/bin/${APP_NAME}"

# 5. Create the Desktop Entry file
echo "Creating desktop entry file..."
cat > "${DEB_BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=${DISPLAY_NAME}
Comment=A GRUB theme customizer
Exec=${APP_NAME}
Icon=${APP_NAME}.png
Terminal=false
Type=Application
Categories=System;Settings;Utility;
EOF

# 6. Create post-installation and pre-removal scripts
echo "Creating postinst and prerm scripts..."
cat > "${DEB_BUILD_DIR}/DEBIAN/postinst" << EOF
#!/bin/bash
# Post-installation script

# Update the desktop database
update-desktop-database > /dev/null 2>&1
exit 0
EOF

cat > "${DEB_BUILD_DIR}/DEBIAN/prerm" << EOF
#!/bin/bash
# Pre-removal script

# Remove __pycache__ directories to prevent the dpkg warning
rm -rf /usr/share/${APP_NAME}/__pycache__

# Update the desktop database
update-desktop-database > /dev/null 2>&1
exit 0
EOF

# 7. Set correct permissions for the scripts
echo "Setting file permissions..."
chmod 0755 "${DEB_BUILD_DIR}/DEBIAN/postinst"
chmod 0755 "${DEB_BUILD_DIR}/DEBIAN/prerm"
chmod 0755 "${DEB_BUILD_DIR}/usr/bin/${APP_NAME}"

# 8. Build the .deb package
echo "Building the .deb package..."
dpkg-deb --build "${DEB_BUILD_DIR}"

echo "Package creation complete!"
echo "Your Debian package is ready: ${DEB_BUILD_DIR}.deb"

# 9. Clean up the temporary directory..."
echo "Cleaning up temporary directory..."
rm -rf "${DEB_BUILD_DIR}"

echo "Done."
