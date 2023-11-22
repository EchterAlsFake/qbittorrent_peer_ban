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
import sys
import qbittorrentapi
import getpass

from datetime import datetime
from colorama import *

z = f"{Fore.LIGHTGREEN_EX}[+]"

# Configure your qBitTorrent API endpoint. (Only relevant for Legacy usage)
api_endpoint = "http://127.0.0.1:8080/api/v2"

# Customize the blacklist keywords. (Only relevant for Legacy usage)
blacklists = ["Xunlei", "XL00", r"^7\.", "BitComet", "BC", "Unknown"]

# !!! The V2 uses a different blacklist, so don't get confused. You can change it in settings!

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
        logger_error(e)
        return set()


def get_peers(task):
    try:
        response = requests.get(f"{api_endpoint}/sync/torrentPeers?hash={task}&rid=0")
        peers = re.findall(r'"([^"]*)":{"client":"([^"]*)"', response.text)
        return peers

    except requests.RequestException as e:
        logger_error(e)
        return []


def ban_peer(addr):
    try:
        # For qBitTorrent 4.5.x. Should work for all versions.
        requests.post(f"{api_endpoint}/transfer/banPeers", data={"peers": addr})
        # For qBitTorrent 4.4.x, uncomment the next line and comment out the previous line
        # requests.get(f"{api_endpoint}/transfer/banPeers?peers={addr}")

    except requests.RequestException as e:
        logger_error(e)


def logger_error(e):
    print(f"{Fore.LIGHTWHITE_EX}{datetime.now()}  {Fore.LIGHTRED_EX}ERROR: {Fore.RESET}{e}")


def logger_debug(e):
    print(f"{Fore.LIGHTWHITE_EX}{datetime.now()}  {Fore.LIGHTBLUE_EX}DEBUG: {Fore.RESET}{e}")


class Legacy():
    """
    This is the legacy version of the script (v1.0).
    Use that if you have any problems with the new version.

    """

    def __init__(self):
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


class V2():
    """
    This is the V2 version of the Peer ban script using the qbittorrent Python library. This is a lot more robust,
    stable and future-proof. I recommend using this method, but if you have any issues with it, go with the Legacy
    version.
    """

    def __init__(self):

        self.conn_info = None
        self.ban_by_country = False
        self.country_codes = None
        if self.authentication():

            self.menu()

            self.get_peers()



    def menu(self):
        options = input(f"""
1) Settings
2) Start
3) Exit
---------------------->:""")

        if options == "1":
            self.settings()

        elif options == "2":
            self.start()

        elif options == "3":
            print(f"{z}Exiting...")
            sys.exit()

        else:
            print(f"Wrong option. Please try again.")
            self.menu()

    def settings(self):
        ""

    def configuration(self):
        print(f"""
--------------------------------INFORMATION--------------------------------------------

You will be prompted to configure your credentials for the WebUI, you've configured in the qBittorrent Client.
If you have enabled 'Bypass Authentication for localhost', just press enter when you get asked for Username and Password

Your WebUi will be probably at Localhost at Port 8080, so you can also just press enter if you left it on default.




""")

        username = input(f"Please enter your username [Enter to skip authentication]: ")
        password = getpass.getpass("Please enter your password [None]: ")
        host_input = input(f"Please enter webUI host [localhost]: ")
        port_input = input(f"Please enter webUI port [8080]: ")
        host = host_input if host_input else "localhost"
        port = port_input if port_input else "8080"

        self.conn_info = dict(
            host=host,
            port=port,
            username=username,
            password=password)

    def authentication(self):

        try:
            self.client = qbittorrentapi.Client(**self.conn_info)
            print(f"Successfully authenticated!")
            return True

        except qbittorrentapi.LoginFailed as e:
            print(f"Login failed: {e}")
            self.authentication()

    def start(self):
        print(f"{z}Searching for peers every 5 seconds...")

        while True:
            torrents = self.client.torrents_info()
            for idx, torrent in enumerate(torrents):
                peer_info = self.client.sync_torrent_peers(torrent_hash=torrent.hash)
                for peer in peer_info.get("peers", {}).values():
                    client_name = peer.get("client", "")
                    ip = peer.get("ip", "")
                    port = peer.get("port", "")
                    country_code = peer.get("country_code", "")

                    """
                    Enable this for debugging...
                    
                    if len(client_name) >= 1:
                        print(client_name)
                    """

                    for item in blacklists:
                        if item in client_name:
                            peer = f"{ip}:{port}"
                            print(f"{Fore.LIGHTGREEN_EX}Banning {peer} because of his client '{client_name}{Fore.RESET}'")
                            self.client.transfer_ban_peers(peer)

                    if self.ban_by_country:
                        for country_code_ in self.country_codes:
                            peer = f"{ip}:{port}"
                            if country_code_ == country_code:
                                print(f"{Fore.LIGHTGREEN_EX}Banning {peer} because of his country: {country_code_}")
                                self.client.transfer_ban_peers(peer)

            time.sleep(5)


'''version = input(f"""
{Fore.LIGHTWHITE_EX}Which Version do you want to use?

{Fore.LIGHTMAGENTA_EX}1) Legacy V1.0 

{Fore.LIGHTRED_EX}- No authentication support
{Fore.LIGHTYELLOW_EX}- Uses web requests to do stuff
{Fore.LIGHTGREEN_EX}- simpler, more lightweight



{Fore.LIGHTCYAN_EX}2) New V2.0

{Fore.LIGHTGREEN_EX}- Authentication support (Username, Password)
{Fore.LIGHTGREEN_EX}- Uses qbittorrent Python library
{Fore.LIGHTGREEN_EX}- more robust, stable and future-proof
{Fore.LIGHTGREEN_EX}- Ban peers by country code
{Fore.LIGHTGREEN_EX}- Settings and persistent configuration
{Fore.LIGHTRED_EX}- maybe less lightweight

---------------[2]--->:
""")'''

Legacy()


# V2 is still in development!
