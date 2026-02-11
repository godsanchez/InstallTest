# Install uv tool for python package management
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 

# Download cpm package
Invoke-WebRequest -Uri "https://github.com/godsanchez/InstallTest/archive/refs/heads/main.zip"-OutFile ./main.zip

# Unzip the package
Expand-Archive -Path ./main.zip -DestinationPath ./CPMInstall

# Install the package using uv
uv tool install ./CPMInstall/InstallTest-main/src/CPM