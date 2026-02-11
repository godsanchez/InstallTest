#!/bin/bash

# Install uv tool for python package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Download cpm package
wget "https://github.com/godsanchez/InstallTest/archive/refs/heads/main.zip" -O ./main.zip

# Unzip the package
unzip ./main.zip -d ./CPMInstall

# Install the package using uv
uv tool install ./CPMInstall/InstallTest-main/src/CPM

