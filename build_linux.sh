git clone https://github.com/EchterAlsFake/qbittorrent_peer_ban
cd qbittorrent_peer_ban
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller -F main.py
cd dist
chmod +x main
echo "qBittorrent Peer Ban executable is now in $(pwd)"