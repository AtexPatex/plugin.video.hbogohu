# -*- coding: utf-8 -*-

from urlparse import parse_qsl

from lib.hbogohu.auth import login, generate_individualization, Session
from lib.hbogohu.play import play
from lib.hbogohu.queries import QueryManager
from lib.hbogohu.settings import Settings, LANGUAGE
from lib.hbogohu.wrapper import xbmc_wrapper

MODE_LISTING = 1
MODE_SEASON = 2
MODE_EPISODE = 3
MODE_SEARCH = 4
MODE_PLAY = 5
MODE_SILENT_REGISTER = 6
MODE_LOGIN = 7


class HboGoPlugin:

    def __init__(self, __add_on__, sys_args):
        self.__base_url__ = sys_args[0]
        self.__handle__ = int(sys_args[1])

        params = dict(parse_qsl(sys_args[2].replace("?", "")))
        self.url = params.get("url")
        self.name = params.get("name")
        self.thumbnail = params.get("thumbnail")
        self.mode = int(params.get("mode", "0"))
        self.cid = params.get("cid")

        self.__add_on__ = __add_on__
        self.__settings__ = Settings(self.__add_on__)
        language_index = self.__settings__.get(LANGUAGE)
        if language_index in [0, 1]:
            self.lang_code = "HUN"
            self.srt_subs_path = xbmc_wrapper.translate_path("special://temp/hbogo.Hungarian.Forced.srt")
        elif language_index == 2:
            self.lang_code = "ENG"
            self.srt_subs_path = xbmc_wrapper.translate_path("special://temp/hbogo.English.Forced.srt")

        self.media_path = xbmc_wrapper.translate_path(self.__add_on__.getAddonInfo("path") + "/resources/media/")
        self.session = Session()
        self.query_manager = QueryManager(self)

    def run(self):
        mode = self.mode
        url = self.url
        if not mode or not url:
            self.query_manager.categories()

        elif mode == MODE_LISTING:
            self.query_manager.listing()

        elif mode == MODE_SEASON:
            self.query_manager.season()

        elif mode == MODE_EPISODE:
            self.query_manager.episode()

        elif mode == MODE_SEARCH:
            self.query_manager.search()

        elif mode == MODE_PLAY:
            play(self)

        elif mode == MODE_SILENT_REGISTER:
            generate_individualization(self.__settings__)

        elif mode == MODE_LOGIN:
            login(self)

        xbmc_wrapper.end_of_directory(self.__handle__)
