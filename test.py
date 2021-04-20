#!/usr/bin/env python3
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management

import os
import requests
import logging
# remove this for testing
os.environ['LOGURU_LEVEL'] = "WARNING"
from loguru import logger
from config import username, password, qbthost, hec_token, hec_host, source_host
# python3 -m pip install git+git://github.com/georgestarcher/Splunk-Class-httpevent.git

from splunk_http_event_collector import http_event_collector

BASEURL=qbthost

class API(object):

    def __init__(self):
        """ for dealing with things """
        self.cookies = self.login()

    def login(self, username=username, password=password):
        response = requests.post(f"{BASEURL}/api/v2/auth/login", data={ "username" : username, "password" : password})
        response.raise_for_status()
        logger.debug("Login: {}", response.text)
        cookies = response.cookies
        return cookies

    def apiVersion(self):
        response = requests.post(f"{BASEURL}/api/v2/app/webapiVersion", cookies=self.cookies)
        response.raise_for_status()
        logger.debug("API Version: {}", response.text)
        return response.text

    def getTorrents(self):
        response = requests.post(f"{BASEURL}/api/v2/torrents/info", cookies=self.cookies)
        response.raise_for_status()

        return response.json()

api = API(username, password)

hec = http_event_collector(token=hec_token,
                           http_event_server=hec_host,
                           http_event_port=443,
                           http_event_server_ssl=True,
                           )
hec.index = "torrent"
hec.log.setLevel(logging.DEBUG)

counter = 0
for torrent in api.getTorrents():
    payload = {
        "sourcetype" : "torrent:info",
        "host" : source_host,
        "source" : "qbittorrent",
        "event" : torrent,
    }
    logger.debug(torrent.get('name'))
    # send it
    hec.batchEvent(payload)
    counter += 1
    if counter > 20:
        hec.flushBatch()
        counter = 0
logger.debug("Flushing queue...")
hec.flushBatch()