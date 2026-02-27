# Default Portal values
$BLOB_PREFIX = "ganymedepackagemanager"
$DOWNLOAD_PATH = "."
$STORAGE_ACCOUNT_URL = "https://crcportalstoragedev.blob.core.windows.net"
$CONTAINER_NAME = "cpm"

# Install uv tool for python package management
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 

# Update user path to point to uv
$env:Path = "$HOME\.local\bin;$env:Path"

# Download cross-platform Python download script
Invoke-WebRequest -Uri "https://aka.ms/CPMDownload" -OutFile ./downloadblob.py

# Download cpm package
uv run .\downloadblob.py --blob-prefix $BLOB_PREFIX --download-path $DOWNLOAD_PATH --account-url $STORAGE_ACCOUNT_URL --container-name $CONTAINER_NAME

# Install the package using uv, with bytecode compilation for faster imports
uv tool install --compile-bytecode $DOWNLOAD_PATH
