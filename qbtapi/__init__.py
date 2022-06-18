""" Qbittorrent API dumper """

from socket import gethostname

import sys

from pydantic import BaseSettings, Field
import requests
import requests.exceptions


class QBTAPIConfig(BaseSettings):
    """configuration"""
    hec_hostname: str = Field(..., env="HECHOST", alias="HECHOST")
    hec_token: str = Field(..., env="HECTOKEN")
    hec_port: int = Field(8088, gt=0, lt=65535, env="HECPORT")
    hec_tls: bool = True

    hec_index: str = Field(default="torrent", env="HECINDEX")
    hec_source: str = "qbittorrent"
    hec_sourcetype: str =  Field(default="torrent:info", env='HECSOURCETYPE')

    hec_host_field = str = Field(default=gethostname(), env="HECHOSTFIELD")

    qb_hostname: str = Field(..., env="QB_SERVER_HOST")
    qb_username: str = Field(..., env="QB_USERNAME")
    qb_password: str = Field(..., env="QB_PASSWORD")

    #pylint: disable=too-few-public-methods
    class Config:
        """config settings for the QBTAPIConfig Class"""
        env_file = '.env'
        env_file_encoding = 'utf-8'

class API():
    """ handles interactions with the API """
    def __init__(self, config: QBTAPIConfig):
        """ for dealing with things """
        self.server = config.qb_hostname
        self.baseurl = f'http://{self.server}'
        self.username = config.qb_username
        self.password = config.qb_password
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
        print(f"Login: {response.text}", file=sys.stdout)
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
