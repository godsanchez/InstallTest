# CRC Package Manager values
$CPM_GUID = "4464b461-ed11-41f5-98b7-2f5c40b76c19"
$DOWNLOAD_PATH = "./"

Function Exit-WithError
{
    Param
    (
        [string] $Message,
        [string] $ExceptionMessage
    )

    Write-Host ""
    Write-Host $Message -ForegroundColor Red
    Write-Host $ExceptionMessage -ForegroundColor Red
    Exit 1
}

Write-Host "Starting CRC Package Manager installation..." -ForegroundColor Green
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Green


# Download cross-platform Python download script
Try
{
    Invoke-WebRequest -Uri "https://aka.ms/CPMDownload-dev" -OutFile ./downloadblob-dev.py  -TimeoutSec 10
}
Catch
{
    Exit-WithError -Message "Failed to download dependency installer script:" -ExceptionMessage $_.Exception.Message
}


# Install uv tool for python package management
Try
{
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex | Out-Null" 

    # Update user path to point to uv
    $env:Path = "$HOME\.local\bin;$env:Path"
    $env:AZURE_TOKEN_CREDENTIALS = "AzureCliCredential"
}
Catch
{
    Exit-WithError -Message "Failed to install uv tool for python package management:" -ExceptionMessage $_.Exception.Message
}


Write-Host "Dependencies installed." -ForegroundColor Green
Write-Host ""
Write-Host "Installing CRC Package Manager..." -ForegroundColor Green


# Download cpm package
Try
{
    uv run .\downloadblob-dev.py --package-guid $CPM_GUID --download-path $DOWNLOAD_PATH

    # Find latest package in download path
    $PACKAGE_PATH = Get-ChildItem -Path $DOWNLOAD_PATH -Filter "crcpackagemanager-*" | Sort-Object -Descending | Select-Object -First 1
}
Catch
{
    Exit-WithError -Message "Failed to download CRC Package Manager:" -ExceptionMessage $_.Exception.Message
}

# Install the package using uv
Try
{
    uv tool install $PACKAGE_PATH
}
Catch
{
    Exit-WithError -Message "Failed to install CRC Package Manager:" -ExceptionMessage $_.Exception.Message
}

# Cleanup - remove the downloaded package and scripts
Try
{
    Remove-Item -Path $PACKAGE_PATH
    Remove-Item -Path "$DOWNLOAD_PATH/downloadblob-dev.py"
    Remove-Item -Path $MyInvocation.MyCommand.Path
}
Catch
{
    Exit-WithError -Message "Failed to clean up temporary files:" -ExceptionMessage $_.Exception.Message
}


Write-Host ""
Write-Host "CRC Package Manager installed. Please type the following to see available commands:" -ForegroundColor Green
Write-Host ""
Write-Host "crc --help" -ForegroundColor Blue
Write-Host ""
