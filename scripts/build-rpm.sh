#!/bin/bash
# Navigate to the project root directory
cd "$(dirname "$0")/.."

set -e

# Load variables from .env
if [ -f .env ]; then
    set -a; source .env; set +a
else
    echo "Error: .env file not found!" >&2
    exit 1
fi

STAGING_DIR="./staging"
SOURCE_DIR="./src"
PACKAGE_NAME="grubdeck.rpm"

echo "Starting RPM package creation for ${APP_NAME} v${VERSION}..."

echo "Removing old package file (if it exists)"
rm -f "${APP_NAME}"*.rpm

if ! command -v fpm &> /dev/null
then
    echo "Error: fpm (Effing Package Management) is not installed." >&2
    exit 1
fi

echo "Creating staging directory structure..."
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/usr/lib/${APP_NAME}"
mkdir -p "${STAGING_DIR}/usr/bin"
mkdir -p "${STAGING_DIR}/usr/share/applications"
mkdir -p "${STAGING_DIR}/usr/share/pixmaps"

echo "Copying application files..."
cp -r "${SOURCE_DIR}/." "${STAGING_DIR}/usr/lib/${APP_NAME}/"
cp "${ICON_SOURCE}" "${STAGING_DIR}/usr/share/pixmaps/${APP_NAME}.png"

echo "Creating wrapper script for /usr/bin..."
printf '#!/bin/bash\n/usr/bin/python3 /usr/lib/%s/main.py\n' "${APP_NAME}" > "${STAGING_DIR}/usr/bin/${APP_NAME}"
chmod 0755 "${STAGING_DIR}/usr/bin/${APP_NAME}"

echo "Creating desktop entry file..."
cat > "${STAGING_DIR}/usr/share/applications/${APP_NAME}.desktop" << EODESKTOP
[Desktop Entry]
Name=${DISPLAY_NAME}
Comment=A GRUB theme customizer
Exec=${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Type=Application
Categories=System;Settings;Utility;
EODESKTOP

# Parse comma-separated RPM dependencies into FPM arguments
FPM_DEPENDS=()
IFS=',' read -ra DEPS <<< "$RPM_DEPENDENCIES"
for dep in "${DEPS[@]}"; do
    # Trim whitespace and append
    clean_dep=$(echo "$dep" | xargs)
    FPM_DEPENDS+=("--depends" "$clean_dep")
done

echo "Building the .rpm package..."
fpm -s dir -t rpm \
    -n "${APP_NAME}" \
    -v "${VERSION}" \
    --iteration 1 \
    --rpm-os linux \
    --license "MIT" \
    --category "System" \
    --url "${PROJECT_URL}" \
    --maintainer "${MAINTAINER}" \
    --description "${RPM_DESCRIPTION}" \
    "${FPM_DEPENDS[@]}" \
    --chdir "${STAGING_DIR}" \
    -p "${PACKAGE_NAME}" \
    . 

echo "Cleaning up temporary directory..."
rm -rf "${STAGING_DIR}"

echo "✅ RPM package is ready: ${PACKAGE_NAME}"
