""" Qbittorrent API dumper """


import os
import sys

import requests
import requests.exceptions

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
