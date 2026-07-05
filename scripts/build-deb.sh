#!/bin/bash
# Navigate to the project root directory
cd "$(dirname "$0")/.."

set -e

# Load variables from .env
if [ -f .env ]; then
    set -a; source .env; set +a
else
    echo "Error: .env file not found! Please create it at the root." >&2
    exit 1
fi

DEB_BUILD_DIR="${APP_NAME}-${VERSION}-${ARCHITECTURE}"
SOURCE_DIR="./src"
PACKAGE_NAME="grubdeck.deb"

echo "Starting Debian package creation for ${APP_NAME} v${VERSION}..."

echo "Creating directory structure..."
rm -rf "${DEB_BUILD_DIR}"
mkdir -p "${DEB_BUILD_DIR}/DEBIAN"
mkdir -p "${DEB_BUILD_DIR}/usr/bin"
mkdir -p "${DEB_BUILD_DIR}/usr/share/${APP_NAME}"
mkdir -p "${DEB_BUILD_DIR}/usr/share/applications"
mkdir -p "${DEB_BUILD_DIR}/usr/share/pixmaps"

echo "Copying application files..."
cp -r "${SOURCE_DIR}/." "${DEB_BUILD_DIR}/usr/share/${APP_NAME}/"
cp "${SOURCE_DIR}/privileged_installer.py" "${DEB_BUILD_DIR}/usr/share/${APP_NAME}/"
cp "${ICON_SOURCE}" "${DEB_BUILD_DIR}/usr/share/pixmaps/${APP_NAME}.png"

echo "Creating DEBIAN/control file..."
cat > "${DEB_BUILD_DIR}/DEBIAN/control" << EOCONTROL
Package: ${APP_NAME}
Version: ${VERSION}
Maintainer: ${MAINTAINER}
Architecture: ${ARCHITECTURE}
Depends: ${DEB_DEPENDENCIES}
Homepage: ${PROJECT_URL}
Description: ${DEB_DESCRIPTION}
 This package installs a graphical tool for customizing GRUB themes.
 It provides a user-friendly interface to browse, preview, and install themes,
 making it easy to personalize the GRUB boot menu.
EOCONTROL

echo "Creating wrapper script for /usr/bin..."
printf '#!/bin/bash\n/usr/bin/python3 /usr/share/%s/main.py\n' "${APP_NAME}" > "${DEB_BUILD_DIR}/usr/bin/${APP_NAME}"

echo "Creating desktop entry file..."
cat > "${DEB_BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop" << EODESKTOP
[Desktop Entry]
Name=${DISPLAY_NAME}
Comment=A GRUB theme customizer
Exec=${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Type=Application
Categories=System;Settings;Utility;
EODESKTOP

echo "Creating postinst and prerm scripts..."
cat > "${DEB_BUILD_DIR}/DEBIAN/postinst" << 'EOPOST'
#!/bin/bash
update-desktop-database > /dev/null 2>&1
exit 0
EOPOST

cat > "${DEB_BUILD_DIR}/DEBIAN/prerm" << EOPRERM
#!/bin/bash
rm -rf /usr/share/${APP_NAME}/__pycache__
update-desktop-database > /dev/null 2>&1
exit 0
EOPRERM

echo "Setting file permissions..."
chmod 0755 "${DEB_BUILD_DIR}/DEBIAN/postinst"
chmod 0755 "${DEB_BUILD_DIR}/DEBIAN/prerm"
chmod 0755 "${DEB_BUILD_DIR}/usr/bin/${APP_NAME}"

echo "Building the .deb package..."
dpkg-deb --build "${DEB_BUILD_DIR}" "${PACKAGE_NAME}"

echo "Cleaning up temporary directory..."
rm -rf "${DEB_BUILD_DIR}"

echo "✅ Debian package is ready: ${PACKAGE_NAME}"
