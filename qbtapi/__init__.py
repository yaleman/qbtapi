"""Qbittorrent API dumper"""

import logging
import sys
from socket import gethostname
from typing import Any

import requests
import requests.exceptions
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests.cookies import RequestsCookieJar


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

    qb_hostname: str = Field("localhost", validation_alias="QB_SERVER_HOST")
    qb_username: str = Field(..., validation_alias="QB_USERNAME")
    qb_password: SecretStr = Field(..., validation_alias="QB_PASSWORD")
    qb_port: int = Field(8080, gt=0, lt=65535, validation_alias="QB_PORT")
    qb_use_tls: bool = Field(default=False, validation_alias="QB_USE_TLS")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class API:
    """handles interactions with the API"""

    def __init__(self, config: QBTAPIConfig):
        """for dealing with things"""
        self.config = config

        self.session = requests.Session()
        self.cookies = self.login()
        self.logger = logging.getLogger(__name__)

    @property
    def baseurl(self) -> str:
        """returns the base URL"""
        scheme = "https" if self.config.qb_use_tls else "http"
        return f"{scheme}://{self.config.qb_hostname}:{self.config.qb_port}"

    def do_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        cookies: RequestsCookieJar | None = None,
    ) -> requests.Response:
        """general POST request thingie, kills the program if it fails."""
        try:
            response = self.session.post(url, data=data, cookies=cookies, timeout=30)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as error:
            self.logger.error("Connection error to %s, bailing: %s", url, error)
            sys.exit(1)
        except Exception as error:  # noqa: BLE001
            self.logger.error("Error connecting to %s, bailing: %s", url, error)
            sys.exit(1)
        return response

    def login(self) -> RequestsCookieJar:
        """does the login and gets a cookie"""
        self.logger.info("Logging in to %s", self.baseurl)
        response = self.do_post(
            url=f"{self.baseurl}/api/v2/auth/login",
            data={
                "username": self.config.qb_username,
                "password": self.config.qb_password.get_secret_value(),
            },
        )
        self.logger.info("Login: %s", response.text)
        if "fails" in response.text.lower():
            self.logger.error("Login failed, check your credentials")
            sys.exit(1)
        cookies = response.cookies
        return cookies

    def api_version(self) -> str:
        """query the API version"""
        response = self.do_post(
            f"{self.baseurl}/api/v2/app/webapiVersion", cookies=self.cookies
        )
        self.logger.debug("API Version: %s", response.text)
        return response.text

    def get_torrents(self) -> dict[str, Any]:
        """pulls the torrent information"""
        response = self.do_post(
            f"{self.baseurl}/api/v2/torrents/info", cookies=self.cookies
        )
        result: dict[str, Any] = response.json()
        return result
