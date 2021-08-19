#!/usr/bin/env python3

"""
Pulls torrent information from the qBittorrent API and pushes it to Splunk HEC

https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management
"""

import os
import logging
import sys
from socket import gethostname

import requests
import requests.exceptions

# remove this for testing
os.environ["LOGURU_LEVEL"] = "DEBUG"

# python3 -m pip install git+git://github.com/georgestarcher/Splunk-Class-httpevent.git
try:
    from splunk_http_event_collector import http_event_collector
except ImportError as error_message:
    sys.exit(f"Failed to import splunk_http_event_collector: {error_message}")

class API():
    """ handles interactions with the API """
    def __init__(self):
        """ for dealing with things """
        self.server = os.getenv('QB_SERVER_HOST')
        self.baseurl = f'http://{self.server}'
        self.username = os.getenv('QB_USERNAME')
        self.password = os.getenv('QB_PASSWORD')
        self.cookies = self.login()

    def do_post(self, url, data=None, cookies=None):
        """ general POST request thingie, kills the program if it fails. """
        try:
            response = requests.post(url, data=data, cookies=cookies)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as error:
            print(f"Connection error to {self.baseurl}, bailing: {error}", file=sys.stderr)
            sys.exit(1)
        except Exception as error: # pylint: disable=broad-except
            print(f"Error connecting to {url}, bailing: {error}", file=sys.stderr)
            sys.exit(1)
        return response

    def login(self):
        """ does the login and gets a cookie """
        response = self.do_post(
            url=f"{self.baseurl}/api/v2/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
        )
        print("Login: {}", response.text, file=sys.stdout)
        cookies = response.cookies
        return cookies

    def api_version(self):
        """ query the API version """
        response = self.do_post(
            f"{self.baseurl}/api/v2/app/webapiVersion", cookies=self.cookies
        )
        print("API Version: {}", response.text, file=sys.stdout)
        return response.text

    def get_torrents(self):
        """ pulls the torrent information """
        response = self.do_post(
            f"{self.baseurl}/api/v2/torrents/info", cookies=self.cookies
        )
        return response.json()


api = API()

hec = http_event_collector(
    token=os.getenv('HECTOKEN'),
    http_event_server=os.getenv('HECHOST'),
    http_event_port=os.getenv('HECPORT', "443"),
    http_event_server_ssl=True,
)
hec.index = os.getenv("HECINDEX", "torrent")
hec.log.setLevel(logging.DEBUG)

# pylint: disable=invalid-name
queue_counter = 0
for torrent in api.get_torrents():
    payload = {
        "sourcetype": os.getenv('HECSOURCETYPE', "torrent:info"),
        "host": gethostname(), # might as well just say what we think we are
        "source": "qbittorrent",
        "event": torrent,
    }
    print(torrent.get("name", file=sys.stdout))
    # send it
    hec.batchEvent(payload)
    queue_counter += 1
    if queue_counter > 20:
        hec.flushBatch()
        queue_counter = 0
print("Flushing queue...", file=sys.stdout)
hec.flushBatch()
