> [!IMPORTANT]
> Although I haven't updated anything here the last months, this whole project **still works**.

# qBitTorrent Peer Ban Script

# Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Downloads](#downloads)
- [Building from source](#building-from-source)
- [Different qBittorrent versions](#notes-on-qbittorrent-versions)
- [License](#license)
- [Credits](#credits)

# Features

- Ban Peers by their client name
- Ban Peers by their country code
- (optional) VPN detection to prevent false positives
- Authentication support
- Nice and easy configuration menu
- persistent settings



## Prerequisites
- Python 3.x
- `requests` library in Python (install via `pip install requests`)
- `colorama` library in Python (install via `pip install colorama`)
- `qbittorrent-api` library in Python (install via `pip install qbittorrent-api`)
- `hue_shift` library in Python (install via `pip install hue_shift`)
- qBitTorrent with the Web UI enabled

## Configuration
The script will ask you for everything and explain everything. <br>If you still have questions, feel free to use the discussion tab.
## Usage
1. Ensure qBitTorrent's Web UI is enabled and configured.
2. Run the script: `python path/to/main.py`
3. The script will check all peers every 5 seconds and ban those matching the blacklist / country codes.

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

> Only for Legacy usage! The v2 supports both versions.


- The script is set up for qBitTorrent 4.5.x and later versions. If you are using qBitTorrent version 4.4.x, you need to modify the `ban_peer` function in the script.
  - Uncomment the line for 4.4.x and comment out the line for 4.5.x in the `ban_peer` function.
- Ensure that 'bypass authentication for clients on localhost' is enabled in qBitTorrent's Web UI settings if you don't want to set up authentication for the API.

## License
This script is licensed under GPLv3. See: https://www.gnu.org/licenses/gpl-3.0.en.html

## Credits
Original concept by: https://recolic.net/blog/post/qbittorrent-ban-xunlei
Adapted and expanded by: Johannes Habel
<br>Additional help by [ChatGPT](https://chat.openai.com)
