# -*- coding:utf-8 -*-
   
class Chain(object):
    def __init__(self, url):
        self._url = url

    def __getattr__(self, item):
        return Chain('{}/{}'.format(self._url, item))

    def __str__(self):
        return self._url


def came_case_to_lower_case(arg_name):
    """
    aBC -> a_b_c
    :param arg_name:
    :return:
    """
    str = ""
    for i in range(0, len(arg_name)):
        if arg_name[i].isupper():
            str += '_'
            str += arg_name[i].lower()
        else:
            str += arg_name[i]
    return str


class Bunch(dict):
    def __getattr__(self, item):
        try:
            object.__getattribute__(self, item)
        except AttributeError:
            try:
                value = super(Bunch, self).__getitem__(item)
            except KeyError as e:
                raise AttributeError('attribute named {} was not found'.format(item)) from e
            else:
                if isinstance(value, dict):
                    return Bunch(value)
                elif isinstance(value, list):
                    # 将list中的dict转成Bunch
                    for i in range(len(value)):
                        value[i] = Bunch(value[i])
                return value

    def __setattr__(self, key, value):
        super(Bunch, self).__setitem__(key, value)
