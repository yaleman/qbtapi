#!/usr/bin/env python3

"""
Pulls torrent information from the qBittorrent API and pushes it to Splunk HEC

https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management
"""

import logging
import os
import sys

from splunk_http_event_collector import http_event_collector  # type:ignore

from qbtapi import API, QBTAPIConfig

CONFIG_FILENAMES = [
    "qbtapi.json",
    "~/.config/qbtapi.json",
    "/etc/qbtapi.json",
    os.getenv("QBTAPI_CONFIG_FILE", None),
]

if __name__ == "__main__":

    config = QBTAPIConfig()
    api = API(config=config)

    hec = http_event_collector(
        token=config.hec_token,
        http_event_server=config.hec_hostname,
        http_event_port=config.hec_port,
        http_event_server_ssl=config.hec_tls,
    )
    hec.index = config.hec_index
    hec.log.setLevel(logging.DEBUG)

    # pylint: disable=invalid-name
    queue_counter = 0
    for torrent in api.get_torrents():

        # add this so we can troubleshoot later
        payload = {
            "sourcetype": config.hec_sourcetype,
            "host": config.hec_host_field,
            "source": config.hec_source,
            "event": torrent,
        }
        hec.batchEvent(payload)
        queue_counter += 1
        if queue_counter > 20:
            hec.flushBatch()
            queue_counter = 0
    print("Flushing queue...", file=sys.stdout)
    hec.flushBatch()
