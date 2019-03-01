# -*- coding: utf-8 -*-
import codecs
import json


class MySettings(object):
    """ Settings handler """
    cooldown = 10  # type: int
    prefix = '!'  # type: str
    locale = 'en'  # type: str
    settings_file = None  # type: str

    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.cooldown = MySettings.cooldown
        self.prefix = MySettings.prefix
        self.locale = MySettings.locale

        try:
            with codecs.open(settings_file, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8')
        except IOError:
            pass

    def reload(self, json_data):
        self.__dict__ = json.loads(json_data, encoding='utf-8')
        try:
            self.cooldown = int(self.cooldown)
        except ValueError:
            self.cooldown = 10

        return
    
    def save(self):
        try:
            with codecs.open(self.settings_file, encoding='utf-8-sig', mode='w+') as f:
                json.dump(self.__dict__, f, encoding='utf-8')
            with codecs.open(self.settings_file.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write('var settings = {0};'.format(json.dumps(self.__dict__, encoding='utf-8')))
        except IOError:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return
