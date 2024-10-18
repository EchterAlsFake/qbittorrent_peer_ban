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
import os
import argparse
from configparser_override import ConfigParserOverride

from configparser import ConfigParser
from datetime import datetime
from colorama import *
from hue_shift import return_color, reset

z = f"{Fore.LIGHTGREEN_EX}[+]{Fore.RESET}"

# Configure your qBitTorrent API endpoint. (Only relevant for Legacy usage)
api_endpoint = "http://127.0.0.1:8080/api/v2"

# Customize the blacklist keywords. (Only relevant for Legacy usage)
blacklists_legacy = ["Xunlei", "XL00", r"^7\.", "BitComet", "BC", "Unknown"]

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


def check_config_integrity():
    sections = ["WebUi", "Blacklist", "Country"]
    options_web_ui = ["username", "password", "host", "port"]
    options_blacklist = ["blacklist"]
    options_country = ["country"]

    config_file = "config.ini"

    if os.path.isfile(config_file):
        config_object = ConfigParser()
        config_object.read("config.ini")

        try:
            for idx, section in enumerate(sections):
                if config_object.has_section(section) and idx == 0:
                    for option in options_web_ui:
                        if not config_object.has_option(section=section, option=option):
                            return False

                if config_object.has_section(section) and idx == 1:
                    for option in options_blacklist:
                        if not config_object.has_option(section=section, option=option):
                            return False

                if config_object.has_section(section) and idx == 2:
                    for option in options_country:
                        if not config_object.has_option(section=section, option=option):
                            return False

        except Exception as e:
            return [bool(False), str(e)]

        else:
            return True

    else:
        return False

def create_config_file():

    data = """
[APP]
first_run = true
    
[WebUi]
username = 
password =
host =
port =

[Blacklist]
blacklist =
enabled = true

[Country]
country =
vpn_detection = false
enabled = false
api_key =
"""

    try:
        with open("config.ini", "w") as config_file:
            config_file.write(data)
            return True

    except PermissionError:
        logger_error("Permission Error:  Couldn't create the configuration file...")
        return False

    except Exception as e:
        logger_error(f"Tried to create configuration file with error: {e}")
        return False



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
                    if any(re.search(pattern, ua) for pattern in blacklists_legacy):
                        print(f"{z}{Fore.RESET}[{datetime.now()}] Banning {addr} because of his client '{ua}'")
                        ban_peer(addr)

            time.sleep(5)


class V2():
    """
    This is the V2 version of the Peer ban script using the qbittorrent Python library. This is a lot more robust,
    stable and future-proof. I recommend using this method, but if you have any issues with it, go with the Legacy
    version.
    """

    def __init__(self, start=False):

        try:
            if not check_config_integrity():
                if not create_config_file():
                    logger_error(f"Fatal error, when trying to use the configuration file!, please report that!")
                    exit()

        finally:
            self.conn_info = None
            self.vpn_detection = None
            self.country_codes = None
            self.parser = ConfigParserOverride(env_prefix="QPB_")
            self.parser.read("config.ini")
            self.parser.apply_overrides()
            self.conf = self.parser.config
            self.load_user_settings()

            if self.authentication():
                if start:
                    self.start()
                else:
                    while True:
                        self.menu()

    def menu(self):
        options = input(f"""
{return_color()}1) Settings
{return_color()}2) Start
{return_color()}3) Exit
{return_color()}---------------------->:{reset()}""")

        if options == "1":
            self.settings()

        elif options == "2":
            self.start()

        elif options == "3":
            print(f"{z}Exiting...")
            sys.exit()

        else:
            print(f"{Fore.LIGHTRED_EX}Wrong option. Please try again.")
            self.menu()

    def settings(self):
        settings_options = input(f"""
{return_color()}1) Change WebUi Access configuration (username, password etc.)
{return_color()}2) Change Blacklist
{return_color()}3) Change ban by country
{return_color()}4) Back to man menu
{return_color()}--------------------------=>:{reset()}""")

        if settings_options == "1":
            self.settings_web_ui_configuration()

        elif settings_options == "2":
            self.settings_blacklist()

        elif settings_options == "3":
            self.settings_ban_by_country()

        elif settings_options == "4":
            self.menu()

        else:
            print(f"Wrong O")

    def settings_web_ui_configuration(self):

        host = self.conf["WebUi"]["host"]
        port = self.conf["WebUi"]["port"]
        username = self.conf["WebUi"]["username"]
        password = self.conf["WebUi"]["password"]

        password_length = len(password)
        masked_password = '*' * password_length

        options = input(f"""
{Fore.LIGHTGREEN_EX}1) Change Host              {return_color()}[{host}]{reset()}
{Fore.LIGHTCYAN_EX}2) Change Port              {return_color()}[{port}]{reset()}
{Fore.LIGHTMAGENTA_EX}3) Change Username          {return_color()}[{username}]{reset()}
{Fore.LIGHTYELLOW_EX}4) Change Password          {return_color()}[{masked_password}]{reset()}
{Fore.LIGHTRED_EX}5) Change ALL
{Fore.LIGHTWHITE_EX}6) Go back
{return_color()}-------------------=>:{reset()}""")

        try:
            if options == "1":
                self.settings_host()

            elif options == "2":
                self.settings_port()

            elif options == "3":
                self.settings_username()

            elif options == "4":
                self.settings_password()

            elif options == "5":
                self.settings_host()
                self.settings_port()
                self.settings_username()
                self.settings_password()

        finally:
            if not options == "6":
                with open("config.ini", "w") as config_file:
                    self.conf.write(config_file)

    def settings_host(self):
        host_input = input(f"{z}Please enter webUI host [localhost]: ")
        host = host_input if host_input else "localhost"
        self.conf.set("WebUi", "host", host)

    def settings_port(self):
        port_input = input(f"{z}Please enter webUI port [8080]: ")
        port = port_input if port_input else "8080"
        self.conf.set("WebUi", "port", port)

    def settings_username(self):
        username = input(f"{z}Please enter your username [Enter to skip authentication]: ")
        self.conf.set("WebUi", "username", username)

    def settings_password(self):
        password = getpass.getpass("Please enter your password [None]: ")
        self.conf.set("WebUi", "password", password)

    def settings_blacklist(self):
        blacklist = self.conf["Blacklist"]["blacklist"]
        blacklist_list = blacklist.split(",")

        while True:
            print("Current Blacklist:")
            for idx, item in enumerate(blacklist_list):
                print(f"{idx}): {item}")

            change = input(f"""
{Fore.LIGHTWHITE_EX}Enter one of the given numbers to remove the string from the Blacklist, or type a new word
to append to the blacklist. (Separate new words with a comma) Type 'exit' to abort the process!

{return_color()}-------------=>:{reset()}""")

            if change.lower() == 'exit':
                break

            try:
                change_index = int(change)
                if 0 <= change_index < len(blacklist_list):
                    blacklist_list.pop(change_index)
                else:
                    print("Invalid index. Please enter a valid number or 'exit'.")
            except ValueError:
                # Assuming new words to add are separated by commas
                new_words = change.split(',')
                blacklist_list.extend(word.strip() for word in new_words if word.strip())

            # Update the blacklist in the configuration
            updated_blacklist = ','.join(blacklist_list)
            self.conf.set("Blacklist", "blacklist", updated_blacklist)

            with open("config.ini", "w") as config_file:
                self.conf.write(config_file)

    def settings_ban_by_country(self):

        options = input(f"""
{return_color()}1) Update Country blacklist
{return_color()}2) Disable Country banning
{return_color()}3) Enable Country banning
{return_color()}4) Enable VPN detection
{return_color()}5) Disable VPN detection
{return_color()}6) Configure iphub.info API key
{return_color()}7) Back
{return_color()}------------------------------=>:{reset()}""")

        try:
            if options == "1":
                countrys = input(f"{z}Please enter country codes separated with , (e.g zn,de,ru) -----=>;")
                country_list = countrys.split(",")
                updated_country_list = ",".join(country_list)
                self.conf.set("Country", "country", updated_country_list)
                with open("config.ini", "w") as config_file:
                    self.conf.write(config_file)

            elif options == "2":
                self.conf.set("Country", "enabled", "false")

            elif options == "3":
                self.conf.set("Country", "enabled", "true")

            elif options == "4":
                self.conf.set("Country", "vpn_detection", "true")

            elif options == "5":
                self.conf.set("Country", "vpn_detection", "false")

            elif options == "6":
                api_key = input(f"{z}Please enter your iphub.info API key --=>:")
                self.conf.set("Country", "api_key", api_key)

            elif options == "7":
                self.settings()

            else:
                print(f"Wrong option. Please try again.")
                self.settings()

        finally:
            if not options == "7":
                with open("config.ini", "w") as config_file:
                    self.conf.write(config_file)

    def configuration(self):

        print(f"""
{Fore.LIGHTWHITE_EX}--------------------------------{Fore.LIGHTYELLOW_EX}ONE TIME SETUP{Fore.LIGHTWHITE_EX}--------------------------------------------

You will be prompted to configure your credentials for the WebUI, you've configured in the qBittorrent Client.
If you have enabled 'Bypass Authentication for localhost', just press enter when you get asked for Username and Password

Your WebUi will be probably at Localhost at Port 8080, so you can also just press enter if you left it on default.

""")

        username = input(f"{z}Please enter your username [Enter to skip authentication]: ")
        password = getpass.getpass("Please enter your password [None]: ")
        host_input = input(f"{z}Please enter webUI host [localhost]: ")
        port_input = input(f"{z}Please enter webUI port [8080]: ")
        host = host_input if host_input else "localhost"
        port = port_input if port_input else "8080"

        blacklist_input = input(f"""
Please enter client names to be blacklisted e.g Xunlei, qBittorrent 

Separate names with comma. Leave blank, if you want to disable it. You can change everything later in settings...

{return_color()}-------------=>:{reset()}""")

        blacklist = blacklist_input if blacklist_input else ""
        country_input = input(f"""
Please enter country codes separated with, (e.g cn,de,nl)

Leave blank to disable it. You can change everything later in settings...

{return_color()}-------------=>:{reset()}""")

        country = country_input if country_input else ""

        if len(country) >= 1:
            self.conf.set("Country", "enabled", "true")

        if len(blacklist) >= 1:
            self.conf.set("Blacklist", "enabled", "true")

        vpn_detection_input = input(f"""
Do you want to enable VPN detection?        

If you use the Ban by country feature, you can enable checking by VPN. This will prevent peers from being banned, if they
are connected to a VPN, because they are not really in the country and they are just spoofing their location.

This will require an API key from iphub.info. You can get 1000 requests a day for free.

(This is not 100% accurate)

{Fore.LIGHTRED_EX}1) Yes
{Fore.LIGHTGREEN_EX}2) No

(I recommend turning this OFF. It's only for special use cases!!!)

{return_color()}---------------=>:{reset()}""")

        if vpn_detection_input == "1":
            api_key = input(f"Please enter your iphub.info API key --=>:")

            self.conf.set("Country", "api_key", api_key)
            self.conf.set("Country", "vpn_detection", "true")

        else:
            self.conf.set("Country", "vpn_detection", "false")

        self.conf.set("Blacklist", "blacklist", blacklist)
        self.conf.set("Country", "country", country)
        self.conf.set("APP", "first_run", "false")
        self.conf.set("WebUi", "username", username)
        self.conf.set("WebUi", "password", password)
        self.conf.set("WebUi", "host", host)
        self.conf.set("WebUi", "port", port)
        with open("config.ini", "w") as config_file:
            self.conf.write(config_file)

        print(f"{z}{return_color()}Successfully configured!{reset()}")
        time.sleep(1)

    def authentication(self):

        try:
            self.client = qbittorrentapi.Client(**self.conn_info)
            print(f"{z}{return_color()}Successfully authenticated!{reset()}")
            return True

        except qbittorrentapi.LoginFailed as e:
            logger_error(f"{z}Login Failed: {e}{reset()}")
            self.authentication()

    def start(self):
        print(f"{z}{return_color()}Searching for peers every 5 seconds...{reset()}")
        print(f"{z}{return_color()}Blacklist: {self.conf['Blacklist']['blacklist']}{reset()}")
        print(f"{z}{return_color()}Countries: {self.conf['Country']['country']}{reset()}")
        ignored_ips = []
        vpn_checked_ips = {}
        session = self.create_session()

        while True:
            torrents = self.client.torrents_info()
            for torrent in torrents:
                self.process_torrent_peers(torrent, session, ignored_ips, vpn_checked_ips)

            time.sleep(5)

    def create_session(self):
        session = requests.Session()
        session.headers.update({"X-Key": self.api_key})
        return session

    def process_torrent_peers(self, torrent, session, ignored_ips, vpn_checked_ips):
        peer_info = self.client.sync_torrent_peers(torrent_hash=torrent.hash)

        for peer in peer_info.get("peers", {}).values():
            ip = peer.get("ip", "")
            if ip in vpn_checked_ips:
                continue  # Skip if this IP has already been processed

            self.process_peer(peer, session, ignored_ips, vpn_checked_ips)

    def process_peer(self, peer, session, ignored_ips, vpn_checked_ips):
        client_name = peer.get("client", "")
        ip = peer.get("ip", "")
        port = peer.get("port", "")
        country_code = peer.get("country_code", "")

        if self.ban_by_blacklist and any(re.search(pattern, client_name) for pattern in self.blacklists):
            print(f"{z}{Fore.RESET}[{datetime.now()}] Banning {ip} because of his client '{client_name}'")
            self.ban_peer(ip, port, client_name)

        if self.ban_by_country:
            if country_code in self.country_codes:
                self.check_vpn(ip, port, country_code, session, ignored_ips, vpn_checked_ips)

    def ban_peer(self, ip, port, client_name):
        peer = f"{ip}:{port}"
        print(f"{Fore.LIGHTGREEN_EX}Banning {peer} because of his client '{client_name}{Fore.RESET}'")
        self.client.transfer_ban_peers(peer)

    def check_vpn(self, ip, port, country_code, session, ignored_ips, vpn_checked_ips):
        if self.vpn_detection:
            response = session.get(f"https://v2.api.iphub.info/ip/{ip}")
            if response.status_code == 429:
                logger_error("Exceeded API rate limit. Please try again tomorrow!")
                return

            if response.status_code == 200:
                block = response.json().get("block")
                peer = f"{ip}:{port}"
                if block == 0:
                    self.client.transfer_ban_peers(peer)
                    print(f"Peer {peer} is banned because of his country code '{country_code}'.")

                elif block == 1:
                    print(f"Peer {peer} is using VPN. Skipping...")
                    ignored_ips.append(ip)

            vpn_checked_ips[ip] = True  # Mark this IP as checked

        else:
            self.client.transfer_ban_peers(f"{ip}:{port}")
            print(f"Peer {ip} is banned because of his country code '{country_code}'.")


    def load_user_settings(self):
        try:
            if self.conf["APP"]["first_run"] == "true":
                self.configuration()

        finally:
            # Directly convert the string values to booleans
            self.ban_by_country = self.conf["Country"]["enabled"] == "true"
            self.vpn_detection = self.conf["Country"]["vpn_detection"] == "true"
            self.ban_by_blacklist = self.conf["Blacklist"]["enabled"] == "true"
            self.api_key = self.conf["Country"]["api_key"]

            # Get country codes as a list
            country_codes = self.conf.get("Country", "country").split(",")
            self.country_codes = [item for item in country_codes if item != ""]
            blacklists = self.conf.get("Blacklist", "blacklist").split(",")
            self.blacklists = [item for item in blacklists if item != ""]

            # Retrieve connection info in one step
            self.conn_info = {
                "host": self.conf["WebUi"]["host"],
                "port": self.conf["WebUi"]["port"],
                "username": self.conf["WebUi"]["username"],
                "password": self.conf["WebUi"]["password"]
            }


# Get desired version from command line
parser=argparse.ArgumentParser(description="")
parser.add_argument("version", nargs='?', choices=['', 'v1', 'v2'], default="")
parser.add_argument("-s", "--start", action="store_true")
args=parser.parse_args()

version = args.version[1] if args.version else None
    
if not version:
    version_input = input(f"""
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
    {Fore.LIGHTGREEN_EX}- VPN detection
    {Fore.LIGHTGREEN_EX}- Settings and persistent configuration
    {Fore.LIGHTRED_EX}- maybe less lightweight
    {Fore.LIGHTRED_EX}- not as fast as Legacy

    {return_color()}---------------[2]--->:{reset()}""")

    version = version_input if version_input else "2"

if version == "1":
    Legacy()

elif version == "2":
    V2(start=args.start)

