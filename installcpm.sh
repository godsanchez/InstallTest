#!/bin/bash

# Install uv tool for python package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Update path to point to uv
export PATH="$HOME/.local/bin:$PATH"

# Download cross-platform Python download script
wget "https://aka.ms/CPMDownload" -O ./downloadcpm.py

# Download cpm package
uv run ./downloadcpm.py

# Install the package using uv
uv tool install ./ganymedepackagemanager-0.1.0.tar.gz
