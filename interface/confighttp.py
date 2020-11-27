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

        self._cookies = None

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

    def get(self, url, flag=True, cookie_need_flag=True, **kwargs):
        if flag:
            params = {}
            params.update(kwargs)
        else:
            params = None

        if cookie_need_flag:
            cookie = self._cookies
        else:
            cookie = None

        url = "http://" + self.host + url

        while True:
            try:
                resp = requests.Session().get(url, headers=self._headers, params=params, cookies=cookie)
                resp.raise_for_status()
                break
            except requests.HTTPError as e:
                print(e)
                time.sleep(5)
            except Exception as e:
                print(e)
                time.sleep(5)

        return resp.json()

    def login(self, url, user, password):

        payload = {
            "email": user,
            "password": password
        }

        url = "http://" + self.host + url

        resp = requests.Session().post(url, data=payload)

        # 这里先默认会登录成功
        # self._headers['Cookie'] = resp.headers['Set-Cookie'].split(';')[0]
        # print(self._headers)
        self._cookies= resp.cookies
