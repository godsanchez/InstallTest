# CRC Package Manager values
$CPM_GUID = "51cebd40-e56d-4c90-9dbb-c58e1e64b2c7"
$DOWNLOAD_PATH = "./"

Write-Host "Starting CRC Package Manager installation..." -ForegroundColor Green
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Green


# Download cross-platform Python download script
try
{
    Invoke-WebRequest -Uri "https://aka.ms/CPMDownload" -OutFile ./downloadblob.py  -TimeoutSec 10
}
catch
{
    Write-Host ""
    Write-Host "Failed to download dependency installer script:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit 1
}

# Install uv tool for python package management
try
{
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex | Out-Null" 

    # Update user path to point to uv
    $env:Path = "$HOME\.local\bin;$env:Path"
    $env:AZURE_TOKEN_CREDENTIALS = "AzureCliCredential"
}
catch
{
    Write-Host ""
    Write-Host "Failed to install uv tool for python package management:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit 1
}


Write-Host "Dependencies installed." -ForegroundColor Green
Write-Host ""
Write-Host "Installing CRC Package Manager..." -ForegroundColor Green


# Download cpm package
try
{
    uv run .\downloadblob.py --package-guid $CPM_GUID --download-path $DOWNLOAD_PATH

    # Find latest package in download path
    $PACKAGE_PATH = Get-ChildItem -Path $DOWNLOAD_PATH -Filter "crcpackagemanager-*" | Sort-Object -Descending | Select-Object -First 1
}
catch
{
    Write-Host ""
    Write-Host "Failed to download CRC Package Manager:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit 1
}

# Install the package using uv
try
{
uv tool install $PACKAGE_PATH
}
catch
{
    Write-Host ""
    Write-Host "Failed to install CRC Package Manager:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit 1
}

# Cleanup - remove the downloaded package and scripts
try
{
Remove-Item -Path $PACKAGE_PATH
Remove-Item -Path "$DOWNLOAD_PATH/downloadblob.py"
Remove-Item -Path $MyInvocation.MyCommand.Path
}
catch
{
    Write-Host ""
    Write-Host "Failed to clean up temporary files:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit 1
}


Write-Host ""
Write-Host "CRC Package Manager installed. Please type the following to see available commands:" -ForegroundColor Green
Write-Host ""
Write-Host "crc --help" -ForegroundColor Blue
Write-Host ""
