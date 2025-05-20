#!/usr/bin/env python3

"""
Pulls torrent information from the qBittorrent API and pushes it to Splunk HEC

https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management
"""

import logging
import os

import click
from splunk_http_event_collector import http_event_collector  # type: ignore[import-untyped]

from qbtapi import API, QBTAPIConfig

CONFIG_FILENAMES = [
    "qbtapi.json",
    "~/.config/qbtapi.json",
    "/etc/qbtapi.json",
    os.getenv("QBTAPI_CONFIG_FILE", None),
]


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--dry-run", is_flag=True, help="Do not send data to Splunk")
def main(debug: bool, dry_run: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = QBTAPIConfig.model_validate({})
    api = API(config=config)

    hec = http_event_collector(
        token=config.hec_token,
        http_event_server=config.hec_hostname,
        http_event_port=str(config.hec_port),
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
        if not dry_run:
            hec.batchEvent(payload)
        queue_counter += 1
        if queue_counter > 20:
            if not dry_run:
                hec.flushBatch()
            queue_counter = 0
    logger.info("Flushing queue...")
    hec.flushBatch()


if __name__ == "__main__":
    main()
