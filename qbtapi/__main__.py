#!/usr/bin/env python3
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management

import os
import requests
import logging
import sys
from socket import gethostname

# remove this for testing
os.environ["LOGURU_LEVEL"] = "WARNING"
try:
    from loguru import logger
except ImportError as error_message:
    sys.exit(f"Failed to import loguru: {error_message}")

# python3 -m pip install git+git://github.com/georgestarcher/Splunk-Class-httpevent.git
try:
    from splunk_http_event_collector import http_event_collector
except ImportError as error_message:
    sys.exit(f"Failed to import splunk_http_event_collector: {error_message}")

class API(object):
    def __init__(self):
        """ for dealing with things """
        self.server = os.getenv('QB_SERVER_HOST')
        self.baseurl = f'http://{self.server}'
        self.username = os.getenv('QB_USERNAME')
        self.password = os.getenv('QB_PASSWORD')
        self.cookies = self.login()

    def login(self):
        """ does the login and gets a cookie """
        response = requests.post(
            f"{self.baseurl}/api/v2/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
        )
        response.raise_for_status()
        logger.debug("Login: {}", response.text)
        cookies = response.cookies
        return cookies

    def apiVersion(self):
        response = requests.post(
            f"{self.baseurl}/api/v2/app/webapiVersion", cookies=self.cookies
        )
        response.raise_for_status()
        logger.debug("API Version: {}", response.text)
        return response.text

    def getTorrents(self):
        response = requests.post(
            f"{self.baseurl}/api/v2/torrents/info", cookies=self.cookies
        )
        response.raise_for_status()

        return response.json()


api = API()

hec = http_event_collector(
    token=os.getenv('HECTOKEN'),
    http_event_server=os.getenv('HECHOST'),
    http_event_port=os.getenv('HECPORT', 443),
    http_event_server_ssl=True,
)
hec.index = os.getenv("HECINDEX", "torrent")
hec.log.setLevel(logging.DEBUG)

counter = 0
for torrent in api.getTorrents():
    payload = {
        "sourcetype": os.getenv('HECSOURCETYPE', "torrent:info"),
        "host": gethostname(), # might as well just say what we think we are
        "source": "qbittorrent",
        "event": torrent,
    }
    logger.debug(torrent.get("name"))
    # send it
    hec.batchEvent(payload)
    counter += 1
    if counter > 20:
        hec.flushBatch()
        counter = 0
logger.debug("Flushing queue...")
hec.flushBatch()
