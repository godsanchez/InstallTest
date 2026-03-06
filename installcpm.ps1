# Default Portal values
$BLOB_PREFIX = "44/4464b461-ed11-41f5-98b7-2f5c40b76c19/8/crcpackagemanager"
$BLOB_NAME = "44/4464b461-ed11-41f5-98b7-2f5c40b76c19/8/crcpackagemanager-0.1.4.tar.gz"
$DOWNLOAD_PATH = "."
$STORAGE_ACCOUNT_URL = "https://crcportalstoragedev.blob.core.windows.net"
$CONTAINER_NAME = "assets"

# Install uv tool for python package management
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 

# Update user path to point to uv
$env:Path = "$HOME\.local\bin;$env:Path"

# Download cross-platform Python download script
Invoke-WebRequest -Uri "https://aka.ms/CPMDownload" -OutFile ./downloadblob.py

# Download cpm package
uv run .\downloadblob.py --blob-name $BLOB_NAME --download-path $DOWNLOAD_PATH --account-url $STORAGE_ACCOUNT_URL --container-name $CONTAINER_NAME

# Find latest package in download path
$PACKAGE_PATH = Get-ChildItem -Path $DOWNLOAD_PATH -Filter "crcpackagemanager-*" | Sort-Object -Descending | Select-Object -First 1

# Install the package using uv, with bytecode compilation for faster imports
uv tool install --compile-bytecode $PACKAGE_PATH
