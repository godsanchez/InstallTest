#!/bin/bash

# Default Portal values
BLOB_PREFIX="44/4464b461-ed11-41f5-98b7-2f5c40b76c19/7/crcpackagemanager"
BLOB_NAME="44/4464b461-ed11-41f5-98b7-2f5c40b76c19/7/crcpackagemanager-0.1.4.tar.gz"
DOWNLOAD_PATH="."
STORAGE_ACCOUNT_URL="https://crcportalstoragedev.blob.core.windows.net"
CONTAINER_NAME="assets"

# Install uv tool for python package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Update path to point to uv
export PATH="$HOME/.local/bin:$PATH"

# Download cross-platform Python download script
wget "https://aka.ms/CPMDownload" -O ./downloadblob.py

# Download cpm package
uv run ./downloadblob.py --blob-name "$BLOB_NAME" --download-path "$DOWNLOAD_PATH" --account-url "$STORAGE_ACCOUNT_URL" --container-name "$CONTAINER_NAME"

# Find latest package in download path
PACKAGE_PATH=$(ls -t "$DOWNLOAD_PATH"/crcpackagemanager-* | head -n 1)

# Install the package using uv, with bytecode compilation for faster imports
uv tool install --compile-bytecode "$PACKAGE_PATH"
