# -*- coding: utf-8 -*-
import os
import codecs
import json


class MyLocale(object):
    """ Settings handler """

    locale_file = None  # type: str
    add_help = None  # type: str
    add_done = None  # type: str
    add_exists = None  # type: str
    edit_help = None  # type: str
    edit_done = None  # type: str
    edit_denied = None  # type: str
    stat_help = None  # type: str
    stat_done = None  # type: str
    del_help = None  # type: str
    del_done = None  # type: str
    notfound = None  # type: str

    def __init__(self, locale_file):
        self.reload(locale_file)

    def reload(self, locale_file):
        try:
            f = codecs.open(locale_file, encoding='utf-8-sig', mode='r')
        except (IOError, TypeError):
            locale_file = os.path.join(os.path.dirname(__file__), '..', 'locale', 'en.json')
            f = codecs.open(locale_file, encoding='utf-8-sig', mode='r')

        self.__dict__ = json.load(f, encoding='utf-8')
        self.locale_file = locale_file

        return
