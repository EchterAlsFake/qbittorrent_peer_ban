# qBitTorrent Peer Ban Script

# Table of Contents

[Prerequisites](#prerequisites)
[Configuration](#configuration)
[Usage](#usage)
[Downloads](#downloads)
[Building from source]
[Different qBittorrent versions](#notes-on-qbittorrent-versions)
[License](#license)
[Credits](#credits)

## Overview
This Python script is designed to automatically ban peers in qBitTorrent who are using specific torrent clients that are known for leeching behavior (downloading without fair sharing). It periodically checks all peers and bans those with user-agent strings matching the specified blacklist.

## Prerequisites
- Python 3.x
- `requests` library in Python (install via `pip install requests`)
- `colorama` library in Python (install via `pip install colorama`)
- qBitTorrent with the Web UI enabled

## Configuration
1. **API Endpoint**: Set the qBitTorrent API endpoint in the script. By default, it's set to `http://127.0.0.1:8080/api/v2`. (You don't need to change anything if you leave it on default)
2. **Authentication**: Enable Authentication for clients on the localhost in the Webinterface settings
3. **Blacklist Keywords**: Customize the blacklist in the script to add or remove client identifiers. The default blacklist includes "Xunlei", "XL00", "^7\.", "BitComet", and "BC".
   - Note: BitComet is included due to observed leeching behavior, but this is mostly with older versions. Adjust the blacklist as needed.

## Usage
1. Ensure qBitTorrent's Web UI is enabled and configured.
2. Run the script: `python path/to/main.py`
3. The script will check all peers every 5 seconds and ban those matching the blacklist.

# Downloads

The script is also available in binary for x64 Linux / Windows and can be downloaded in the [releases](https://github.com/EchterAlsFake/qbittorrent_peer_ban/releases/tag/1.0)

# Building from Source

### **Supported Platforms**

* Windows
* Linux

### **Build requirements**

* Python3
* git

## **Scripts**

**Windows**:
<br>``` Invoke-Expression (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/EchterAlsFake/qbittorrent_peer_ban/master/build_windows.ps1" -UseBasicParsing).Content```

<br>**Linux**: ```curl -sL "https://raw.githubusercontent.com/EchterAlsFake/qbittorrent_peer_ban/master/build_linux.sh" | bash```





## Notes on qBitTorrent Versions
- The script is set up for qBitTorrent 4.5.x and later versions. If you are using qBitTorrent version 4.4.x, you need to modify the `ban_peer` function in the script.
  - Uncomment the line for 4.4.x and comment out the line for 4.5.x in the `ban_peer` function.
- Ensure that 'bypass authentication for clients on localhost' is enabled in qBitTorrent's Web UI settings if you don't want to set up authentication for the API.

## License
This script is licensed under GPLv3. See: https://www.gnu.org/licenses/gpl-3.0.en.html

## Credits
Original concept by: https://recolic.net/blog/post/qbittorrent-ban-xunlei
Adapted and expanded by: Johannes Habel
<br>Additional help by [ChatGPT](https://chat.openai.com)