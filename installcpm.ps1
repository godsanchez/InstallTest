# CRC Package Manager values
$CPM_GUID = "51cebd40-e56d-4c90-9dbb-c58e1e64b2c7"
$DOWNLOAD_FOLDER = "./cpm-install"

# Download cross-platform Python download script
Invoke-WebRequest -Uri "https://aka.ms/CPMDownload" -OutFile ./downloadblob.py

# Download cpm package
uv run .\downloadblob.py --package-guid $CPM_GUID --download-path $DOWNLOAD_FOLDER

# Find latest package in download path
$PACKAGE_PATH = Get-ChildItem -Path $DOWNLOAD_FOLDER -Filter "crcpackagemanager-*" | Sort-Object -Descending | Select-Object -First 1

# Install uv tool for python package management
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex | Out-Null" 

# Update user path to point to uv
$env:Path = "$HOME\.local\bin;$env:Path"
$env:AZURE_TOKEN_CREDENTIALS = "AzureCliCredential"

# Install the package using uv
uv tool install $PACKAGE_PATH

# Cleanup - remove the downloaded package and scripts
Remove-Item -Path $DOWNLOAD_FOLDER -Recurse -Force
Remove-Item -Path $MyInvocation.MyCommand.Path
