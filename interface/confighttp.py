# -*- coding:utf-8 -*-

import requests
from configparser import ConfigParser
import time


#配置类
class ConfigHttp(object):
    def __init__(self, ini_file):
        self._ini_file = ini_file
        
        config = ConfigParser()
        config.read(self._ini_file)
        
        self._host = config.get("HTTP", "host")
        self._port = config.get("HTTP", "port")

        self._token = config.get("HTTP", "project_token")

        self._headers = {}

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    @property
    def token(self):
        return self._token

    @property
    def header(self):
        return self._headers

    @header.setter
    def header(self, headers):
        self._headers = headers

    def get(self, url, **kwargs):

        params = {"token": self.token}

        params.update(kwargs)

        url = "http://" + self.host + url + self.port

        while True:
            try:
                resp = requests.Session().get(url, headers=self._headers, params=params)
                resp.raise_for_status()
                break
            except requests.HTTPError as e:
                print(e)
                time.sleep(5)
            except Exception as e:
                print(e)
                time.sleep(5)

        return resp.json()
