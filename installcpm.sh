#!/bin/bash

# Default Portal values
BLOB_PREFIX="ganymedepackagemanager"
DOWNLOAD_PATH="."
STORAGE_ACCOUNT_URL="https://crcportalstoragedev.blob.core.windows.net"
CONTAINER_NAME="cpm"

# Install uv tool for python package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Update path to point to uv
export PATH="$HOME/.local/bin:$PATH"

# Download cross-platform Python download script
wget "https://aka.ms/CPMDownload" -O ./downloadblob.py

# Download cpm package
uv run ./downloadblob.py --blob-prefix "$BLOB_PREFIX" --download-path "$DOWNLOAD_PATH" --account-url "$STORAGE_ACCOUNT_URL" --container-name "$CONTAINER_NAME"

# Install the package using uv, with bytecode compilation for faster imports
uv tool install --compile-bytecode "$DOWNLOAD_PATH"
