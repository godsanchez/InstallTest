#!/bin/bash

# Function to print error messages and exit
error_exit() {
    echo ""
    echo -e "\033[0;31m$1\033[0m"
    exit 1
}

# CRC Package Manager values
CPM_GUID="51cebd40-e56d-4c90-9dbb-c58e1e64b2c7"
DOWNLOAD_PATH="."

echo -e "\033[0;32mStarting CRC Package Manager installation...\033[0m"
echo ""
echo -e "\033[0;32mInstalling dependencies...\033[0m"

# Download cross-platform Python download script
wget --timeout=10 "https://aka.ms/CPMDownload" -O ./downloadblob.py || error_exit "Failed to download dependency installer script."

# Install uv tool for python package management
curl -LsSf https://astral.sh/uv/install.sh | sh || error_exit "Failed to install uv tool for python package management."

# Update path to point to uv
export PATH="$HOME/.local/bin:$PATH"
export AZURE_TOKEN_CREDENTIALS="AzureCliCredential"

echo -e "\033[0;32mDependencies installed.\033[0m"
echo ""
echo -e "\033[0;32mInstalling CRC Package Manager...\033[0m"

# Download cpm package
uv run ./downloadblob.py --package-guid "$CPM_GUID" --download-path "$DOWNLOAD_PATH" || error_exit "Failed to download CRC Package Manager."

# Find latest package in download path
PACKAGE_PATH=$(ls -t "$DOWNLOAD_PATH"/crcpackagemanager-* | head -n 1)
if [ -z "$PACKAGE_PATH" ]; then
    error_exit "Could not find downloaded package."
fi

# Install the package using uv
uv tool install "$PACKAGE_PATH" || error_exit "Failed to install CRC Package Manager."

# Cleanup - remove the downloaded package and scripts
rm "$PACKAGE_PATH" || error_exit "Failed to clean up temporary package file."
rm "$DOWNLOAD_PATH/downloadblob.py" || error_exit "Failed to clean up temporary script file."
rm -- "$0" || echo -e "\033[0;33mWarning: Failed to remove installation script.\033[0m"


echo ""
echo -e "\033[0;32mCRC Package Manager installed. Please type the following to see available commands:\033[0m"
echo ""
echo -e "\033[0;34mcrc --help\033[0m"
echo ""
