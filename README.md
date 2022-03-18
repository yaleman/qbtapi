This queries the qbittorrent API and sends the info about the currently running torrents to Splunk via the HTTP Event Collector

Docker requires the following environment variables:

 - QB_SERVER_HOST    - hostname:port
 - QB_USERNAME       - username
 - QB_PASSWORD       - password
 - HECTOKEN          - Splunk HEC token
 - HECHOST           - Splunk HEC host
 - HECPORT           - Splunk HEC port (must be HTTPS), defaults to "443"
 - HECSOURCETYPE     - Splunk Sourcetype
 - HECINDEX          - Splunk Index, defaults to "torrent"
