#!/usr/bin/env python3

"""
Pulls torrent information from the qBittorrent API and pushes it to Splunk HEC

https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management
"""

import os
import logging
import sys
from socket import gethostname

try:
    from splunk_http_event_collector import http_event_collector
except ImportError as error_message:
    sys.exit(f"Failed to import splunk_http_event_collector: {error_message}")

from . import API

if __name__ == '__main__':
    if not os.getenv("PARENT_HOST"):
        sys.exit("PARENT_HOST environment variable is not set, bailing.")

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
    hostname = gethostname()
    for torrent in api.get_torrents():

        # add this so we can troubleshoot later
        torrent["CONTAINER_ID"] = hostname

        payload = {
            "sourcetype": os.getenv('HECSOURCETYPE', "torrent:info"),
            "host" : os.getenv("PARENT_HOST"),
            "source": "qbittorrent",
            "event": torrent,
        }
        hec.batchEvent(payload)
        queue_counter += 1
        if queue_counter > 20:
            hec.flushBatch()
            queue_counter = 0
    print("Flushing queue...", file=sys.stdout)
    hec.flushBatch()
