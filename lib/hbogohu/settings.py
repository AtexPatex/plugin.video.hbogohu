# -*- coding: utf-8 -*-
from lib.hbogohu.operators import OPERATOR_IDS

OPERATOR = "operator"
OPERATOR_ID = "operatorId"
USERNAME = "username"
PASSWORD = "password"
DEVICE_ID = "customerId"
INDIVIDUALIZATION = "individualization"
FAVORITES_GROUP_ID = "FavoritesGroupId"
SUBTITLE_AUTO_DOWNLOAD = "se"
LANGUAGE = "language"
LAST_SEARCH = "lastsearch"

KEYS_OF_STRING_PROPERTIES = [USERNAME, PASSWORD, DEVICE_ID, INDIVIDUALIZATION, FAVORITES_GROUP_ID, LAST_SEARCH]
KEYS_OF_INT_PROPERTIES = [OPERATOR, LANGUAGE]
KEYS_OF_BOOLEAN_PROPERTIES = [SUBTITLE_AUTO_DOWNLOAD]


class Settings:

    def __init__(self, __add_on__):
        self.__add_on__ = __add_on__
        self.__values = {}
        self.__load_settings()

    def __load_settings(self):
        for k in KEYS_OF_STRING_PROPERTIES:
            self.__values[k] = self.__add_on__.getSetting(k)
        for k in KEYS_OF_INT_PROPERTIES:
            self.__values[k] = int(self.__add_on__.getSetting(k))
        for k in KEYS_OF_BOOLEAN_PROPERTIES:
            self.__values[k] = bool(self.__add_on__.getSetting(k))

        self.__values[OPERATOR_ID] = OPERATOR_IDS[self.__values[OPERATOR]]

    def get(self, key):
        return self.__values.get(key)

    def store(self, key, value):
        current_setting = self.get(key)
        if current_setting != value:
            self.__add_on__.setSetting(key, value)
            self.__values[key] = value
