# -*- coding:utf-8 -*-

from .confighttp import ConfigHttp


class GlobalConfig(object):
    def __init__(self):
        self.http = ConfigHttp('./config/http_config.ini')

    def get_http(self):
        return self.http


global_config = GlobalConfig()
