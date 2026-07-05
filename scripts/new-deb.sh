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

PACKAGE_NAME="${APP_NAME}-${VERSION}-${ARCHITECTURE}.deb"

echo "[*] Removing existing installation of ${APP_NAME}..."
sudo apt remove -y "${APP_NAME}" || true

echo "[*] Deleting old package file..."
rm -f "${PACKAGE_NAME}"

echo "[*] Building new package..."
./scripts/build-deb.sh

echo "[*] Installing new package..."
sudo apt install -y "./${PACKAGE_NAME}"

echo "[*] Reinstall complete!"
