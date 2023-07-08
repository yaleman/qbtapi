""" Qbittorrent API dumper """

from socket import gethostname

import sys
from typing import Any, Dict, Optional

from pydantic import Field
import requests
from requests.cookies import RequestsCookieJar
import requests.exceptions
from pydantic_settings import BaseSettings, SettingsConfigDict


class QBTAPIConfig(BaseSettings):
    """configuration"""

    hec_hostname: str = Field(..., validation_alias="HECHOST", alias="HECHOST")
    hec_token: str = Field(..., validation_alias="HECTOKEN")
    hec_port: int = Field(8088, gt=0, lt=65535, validation_alias="HECPORT")
    hec_tls: bool = True

    hec_index: str = Field(default="torrent", validation_alias="HECINDEX")
    hec_source: str = "qbittorrent"
    hec_sourcetype: str = Field(
        default="torrent:info", validation_alias="HECSOURCETYPE"
    )

    hec_host_field: str = Field(default=gethostname(), validation_alias="HECHOSTFIELD")

    qb_hostname: str = Field(..., validation_alias="QB_SERVER_HOST")
    qb_username: str = Field(..., validation_alias="QB_USERNAME")
    qb_password: str = Field(..., validation_alias="QB_PASSWORD")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class API:
    """handles interactions with the API"""

    def __init__(self, config: QBTAPIConfig):
        """for dealing with things"""
        self.server = config.qb_hostname
        self.baseurl = f"http://{self.server}"
        self.username = config.qb_username
        self.password = config.qb_password
        self.cookies = self.login()

    def do_post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        cookies: Optional[RequestsCookieJar] = None,
    ) -> requests.Response:
        """general POST request thingie, kills the program if it fails."""
        try:
            response = requests.post(url, data=data, cookies=cookies, timeout=30)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as error:
            print(
                f"Connection error to {self.baseurl}, bailing: {error}", file=sys.stderr
            )
            sys.exit(1)
        except Exception as error:  # pylint: disable=broad-except
            print(f"Error connecting to {url}, bailing: {error}", file=sys.stderr)
            sys.exit(1)
        return response

    def login(self) -> RequestsCookieJar:
        """does the login and gets a cookie"""
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

    def api_version(self) -> str:
        """query the API version"""
        response = self.do_post(
            f"{self.baseurl}/api/v2/app/webapiVersion", cookies=self.cookies
        )
        print("API Version: {}", response.text, file=sys.stdout)
        return response.text

    def get_torrents(self) -> Dict[str, Any]:
        """pulls the torrent information"""
        response = self.do_post(
            f"{self.baseurl}/api/v2/torrents/info", cookies=self.cookies
        )
        result: Dict[str, Any] = response.json()
        return result
