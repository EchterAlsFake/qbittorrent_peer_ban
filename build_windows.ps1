# Cloning the repository
git clone https://github.com/EchterAlsFake/qbittorrent_peer_ban
cd qbittorrent_peer_ban

# Creating a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installing dependencies
pip install -r requirements.txt
pip install pyinstaller

# Creating a standalone executable
pyinstaller -F main.py

# Navigating to the 'dist' directory
cd dist

# Making the file executable is not needed in Windows

# Displaying the current directory
Write-Host "qBittorrent Peer Ban executable is now in $(Get-Location)"
