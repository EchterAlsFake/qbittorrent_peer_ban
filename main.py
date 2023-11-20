"""
Credits go to: https://recolic.net/blog/post/qbittorrent-ban-xunlei

Thanks a lot, mate


Copyright (C) 2023 Johannes Habel

Licensed under GPLv3
See: https://www.gnu.org/licenses/gpl-3.0.en.html
or: License file
"""

import requests
import time
import re
from datetime import datetime
from colorama import *
import sys

z = f"{Fore.LIGHTGREEN_EX}[+]"

# Configure your qBitTorrent API endpoint.
api_endpoint = "http://127.0.0.1:8080/api/v2"

# Customize the blacklist keywords.
blacklists = [
    "Xunlei",
    "XL00",
    "^7\.",
    "BitComet",
    "BC"
]

"""
You can remove BitComet from the blacklist. It's mostly the older versions that doesn't seed,
but I experienced a lot of 'leeching' and slow upload speeds from BitComet so I added it.
"""


def get_tasks():
    try:
        response = requests.get(f"{api_endpoint}/sync/maindata?rid=0")
        tasks = re.findall(r'"([0-9a-f]{40})"', response.text)
        return set(tasks)
    except requests.RequestException as e:
        print(f"Warning: Request failed with error {e}", file=sys.stderr)
        return set()


def get_peers(task):
    try:
        response = requests.get(f"{api_endpoint}/sync/torrentPeers?hash={task}&rid=0")
        peers = re.findall(r'"([^"]*)":{"client":"([^"]*)"', response.text)
        return peers
    except requests.RequestException as e:
        print(f"Warning: Request failed with error {e}", file=sys.stderr)
        return []


def ban_peer(addr):
    try:
        # For qBitTorrent 4.5.x. Should work for all versions.
        requests.post(f"{api_endpoint}/transfer/banPeers", data={"peers": addr})
        # For qBitTorrent 4.4.x, uncomment the next line and comment out the previous line
        # requests.get(f"{api_endpoint}/transfer/banPeers?peers={addr}")
    except requests.RequestException as e:
        print(f"Warning: Request failed with error {e}", file=sys.stderr)


print("Checking all peers every 5 seconds...")
while True:
    tasks = get_tasks()
    for task in tasks:
        peers = get_peers(task)
        for addr, ua in peers:
            if any(re.search(pattern, ua) for pattern in blacklists):
                print(f"{z}{Fore.RESET}[{datetime.now()}] Banning {addr} because of his client '{ua}'")
                ban_peer(addr)

    time.sleep(5)
