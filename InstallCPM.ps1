# Install uv tool for python package management
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 

# Update user path to point to uv
$env:Path = "$HOME\.local\bin;$env:Path"

# Download cross-platform Python download script
Invoke-WebRequest -Uri "https://aka.ms/CPMDownload" -OutFile ./downloadcpm.py

# Download cpm package
uv run .\downloadcpm.py

# Install the package using uv
uv tool install ./ganymedepackagemanager-0.1.0.tar.gz
