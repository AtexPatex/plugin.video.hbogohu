# -*- coding: utf-8 -*-
import urllib

from lib.hbogohu import content_types
from lib.hbogohu.auth import login
from lib.hbogohu.directory import DirectoryManager
from lib.hbogohu.favorites import get_favorite_group
from lib.hbogohu.settings import FAVORITES_GROUP_ID, LAST_SEARCH
from lib.hbogohu.util import safe_encode
from lib.hbogohu.wrapper import requests_wrapper, xbmc_wrapper


class QueryManager:

    def __init__(self, __hbo_go_plugin__):
        self.__hbo_go_plugin__ = __hbo_go_plugin__
        self.directory_manager = DirectoryManager(__hbo_go_plugin__)

    def categories(self):
        # kategoria

        self.directory_manager.add_directory("Keresés...", "search", "", 4, "")

        session = self.__hbo_go_plugin__.session
        settings = self.__hbo_go_plugin__.__settings__
        favorites_group_id = settings.get(FAVORITES_GROUP_ID)
        if not favorites_group_id:
            get_favorite_group(self.__hbo_go_plugin__)

        media_path = self.__hbo_go_plugin__.media_path
        if favorites_group_id:
            self.directory_manager.add_directory(
                "Lejátszási listád",
                "https://huapi.hbogo.eu/v7/CustomerGroup/json/HUN/COMP/%s/-/-/-/1000/-/-/false"
                % (favorites_group_id),
                "",
                1,
                media_path + "FavoritesFolder.png",
            )

        response = requests_wrapper.get(
            "https://huapi.hbogo.eu/v5/Groups/json/HUN/COMP", session.get_authenticated_headers()
        )
        json_response = response.json()

        if json_response.get("ErrorMessage"):
            xbmc_wrapper.gui_dialog_ok("Hiba", json_response["ErrorMessage"])

        for item in json_response.get("Items"):
            if not item.get("ObjectUrl"):
                # if the item has no URL we shouldn't display it
                continue
            self.directory_manager.add_directory(
                safe_encode(item.get("Name", "Ismeretlen kategória")),
                item.get("ObjectUrl").replace(
                    "/0/{sort}/{pageIndex}/{pageSize}/0/0", "/0/0/1/1024/0/0"
                ),
                "",
                1,
                media_path + "DefaultFolder.png",
            )

    def listing(self):
        # lista

        session = self.__hbo_go_plugin__.session
        if not session.is_authenticated():
            login(self.__hbo_go_plugin__)

        response = requests_wrapper.get(self.__hbo_go_plugin__.url, session.get_authenticated_headers())
        response_json = response.json()

        if response_json.get("ErrorMessage"):
            xbmc_wrapper.gui_dialog_ok("Hiba", response_json["ErrorMessage"])
        # If there is a subcategory / genres
        if len(response_json["Container"]) > 1:
            for container in response_json["Container"]:
                self.list_add_subcategory(container)
        else:
            items = response_json["Container"][0].get("Contents", {}).get("Items")

            for item in items:
                content_type = item["ContentType"]

                if (
                    content_type == content_types.CONTENT_TYPE_MOVIE
                ):  # 1 = MOVIE/EXTRAS, 2 = SERIES(serial), 3 = SERIES(episode)
                    self.list_add_movie_link(item)

                elif content_type == content_types.CONTENT_TYPE_SERIES_EPISODE:
                    self.list_add_series_episode(item)

                else:
                    self.list_add_series(item)

    # evadok
    def season(self):
        session = self.__hbo_go_plugin__.session
        response = requests_wrapper.get(self.__hbo_go_plugin__.url, session.get_authenticated_headers())
        json_response = response.json()

        if json_response.get("ErrorMessage"):
            xbmc_wrapper.gui_dialog_ok("Hiba", json_response["ErrorMessage"])

        items = json_response.get("Parent", {}).get("ChildContents", {}).get("Items")
        for item in items:
            self.season_add_season(item)

    # epizodok
    def episode(self):
        session = self.__hbo_go_plugin__.session
        response = requests_wrapper.get(self.__hbo_go_plugin__.url, session.get_authenticated_headers())
        response_json = response.json()

        if response_json.get("ErrorMessage"):
            xbmc_wrapper.gui_dialog_ok("Hiba", response_json["ErrorMessage"])

        items = response_json.get("ChildContents", {}).get("Items")
        for item in items:
            self.episode_add_episode(item)

    def search_add_movie(self, item):
        if not item.get("ObjectUrl"):
            return
        object_url = item["ObjectUrl"]
        plot = safe_encode(item["Abstract"])
        age_rating = item["AgeRating"]
        imdb = item["ImdbRate"]
        background_url = item["BackgroundUrl"]
        cast = [item["Cast"].split(", ")][0]
        director = item["Director"]
        writer = item["Writer"]
        duration = item["Duration"]
        genre = item["Genre"]
        name = safe_encode(item["Name"])
        original_name = item["OriginalName"]
        production_year = item["ProductionYear"]

        self.directory_manager.add_link(
            object_url,
            plot,
            age_rating,
            imdb,
            background_url,
            cast,
            director,
            writer,
            duration,
            genre,
            name,
            original_name,
            production_year,
            5,
        )

    def search_add_series_episode(self, item):
        if not item.get("ObjectUrl"):
            return
        object_url = item["ObjectUrl"]
        plot = safe_encode(item["Abstract"])
        age_rating = item["AgeRating"]
        imdb = item["ImdbRate"]
        background_url = item["BackgroundUrl"]
        cast = [item["Cast"].split(", ")][0]
        director = item["Director"]
        writer = item["Writer"]
        duration = item["Duration"]
        genre = item["Genre"]
        name = "%s %s" % (
            item.get("SeriesName").encode("utf-8"),
            item.get("Name").encode("utf-8")
        )
        original_name = item["OriginalName"]
        production_year = item["ProductionYear"]

        self.directory_manager.add_link(
            object_url,
            plot,
            age_rating,
            imdb,
            background_url,
            cast,
            director,
            writer,
            duration,
            genre,
            name,
            original_name,
            production_year,
            5,
        )

    def search_add_series(self, item):
        if not item.get("ObjectUrl"):
            return
        name = safe_encode(item["Name"])
        object_url = item["ObjectUrl"]
        plot = safe_encode(item["Abstract"])
        background_url = item["BackgroundUrl"]
        self.directory_manager.add_directory(name, object_url, plot, 2, background_url)

    def search(self):
        settings = self.__hbo_go_plugin__.__settings__
        media_path = self.__hbo_go_plugin__.media_path
        session = self.__hbo_go_plugin__.session

        search_string = urllib.unquote_plus(settings.get(LAST_SEARCH))
        search_text = xbmc_wrapper.keyboard_modal(search_string, "Filmek, sorozatok keresése...")
        search_text = urllib.quote_plus(search_text)
        if not search_text:
            self.directory_manager.add_directory("Nincs találat", "", "", "", media_path + "DefaultFolderBack.png")
        else:
            settings.store(LAST_SEARCH, search_text)

            response = requests_wrapper.get(
                "https://huapi.hbogo.eu/v8/Search/json/HUN/COMP/%s/0/0/0/0/0/3"
                % (search_text.encode("utf-8")),
                session.get_authenticated_headers()
            )
            response_json = response.json()

            if response_json.get("ErrorMessage"):
                xbmc_wrapper.gui_dialog_ok("Hiba", response_json["ErrorMessage"])

            br = 0
            items = response_json["Container"][0]["Contents"]["Items"]
            for item in items:
                if (
                    item["ContentType"] == content_types.CONTENT_TYPE_MOVIE
                    or item["ContentType"] == content_types.CONTENT_TYPE_MOVIE_ALT
                ):  # 1,7 = MOVIE/EXTRAS, 2 = SERIES(serial), 3 = SERIES(episode)
                    # Ако е филм    # add_link(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
                    self.search_add_movie(item)
                elif item["ContentType"] == content_types.CONTENT_TYPE_SERIES_EPISODE:
                    # Ако е Epizód на сериал    # add_link(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
                    self.search_add_series_episode(item)
                else:
                    self.search_add_series(item)
                    # Ако е сериал
                br = br + 1
            if br == 0:
                self.directory_manager.add_directory(
                    "Nincs találat", "", "", "", media_path + "DefaultFolderBack.png"
                )

    def list_add_movie_link(self, item):
        # if it's a movie: # add_link(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
        plot = safe_encode(item["Abstract"])

        if item.get("AvailabilityTo"):
            plot += " A film megtekinthető: %s" % (
                safe_encode(item["AvailabilityTo"])
            )

        object_url = item["ObjectUrl"]
        age_rating = item["AgeRating"]
        imdb = item["ImdbRate"]
        background_url = item["BackgroundUrl"]
        cast = [item["Cast"].split(", ")][0]
        director = item["Director"]
        writer = item["Writer"]
        duration = item["Duration"]
        genre = item["Genre"]
        name = safe_encode(item["Name"])
        original_name = item["OriginalName"]
        production_year = item["ProductionYear"]

        self.directory_manager.add_link(
            object_url,
            plot,
            age_rating,
            imdb,
            background_url,
            cast,
            director,
            writer,
            duration,
            genre,
            name,
            original_name,
            production_year,
            5,
        )
        # xbmc.log('GO: FILMI: DUMP: ' + item['ObjectUrl'], xbmc.LOGNOTICE)

    def list_add_series_episode(self, item):
        # If it's a series episode: # add_link(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
        plot = safe_encode(item["Abstract"])
        if item.get("AvailabilityTo"):
            plot += " Az epizód megtekinthető: %s" % (
                safe_encode(item["AvailabilityTo"])
            )

        object_url = item["ObjectUrl"]
        age_rating = item["AgeRating"]
        imdb = item["ImdbRate"]
        background_url = item["BackgroundUrl"]
        cast = [item["Cast"].split(", ")][0]
        director = item["Director"]
        writer = item["Writer"]
        duration = item["Duration"]
        genre = item["Genre"]
        name = "%s - %s. ÉVAD %s. RÉSZ" % (
            item.get("SeriesName", "Ismeretlen cím").encode("utf-8"),
            item.get("SeasonIndex"),
            item.get("Index"),
        )
        original_name = item["OriginalName"]
        production_year = item["ProductionYear"]

        self.directory_manager.add_link(
            object_url,
            plot,
            age_rating,
            imdb,
            background_url,
            cast,
            director,
            writer,
            duration,
            genre,
            name,
            original_name,
            production_year,
            5,
        )

    def list_add_series(self, item):
        # If it's a series
        name = safe_encode(item["Name"])
        object_url = item["ObjectUrl"]
        abstract = safe_encode(item["Abstract"])
        mode = 2
        background_url = item["BackgroundUrl"]
        self.directory_manager.add_directory(name, object_url, abstract, mode, background_url)

    def list_add_subcategory(self, item):
        media_path = self.__hbo_go_plugin__.media_path
        self.directory_manager.add_directory(
            safe_encode(item["Name"]),
            item["ObjectUrl"],
            "",
            1,
            media_path + "DefaultFolder.png",
        )

    def season_add_season(self, item):
        if not item.get("ObjectUrl"):
            return
        self.directory_manager.add_directory(
            safe_encode(item["Name"]),
            item["ObjectUrl"],
            safe_encode(item["Abstract"]),
            3,
            item["BackgroundUrl"],
        )

    def episode_add_episode(self, item):
        if not item.get("ObjectUrl"):
            return
        # add_link(ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode)
        plot = safe_encode(item["Abstract"])
        if item.get("AvailabilityTo"):
            plot += " Az epizód megtekinthető: %s" % (
                safe_encode(item["AvailabilityTo"])
            )

        object_url = item["ObjectUrl"]
        age_rating = item["AgeRating"]
        imdb = item["ImdbRate"]
        background_url = item["BackgroundUrl"]
        cast = [item["Cast"].split(", ")][0]
        director = item["Director"]
        writer = item["Writer"]
        duration = item["Duration"]
        genre = item["Genre"]
        name = "%s - %s. ÉVAD %s. RÉSZ" % (
            item.get("SeriesName", "Ismeretlen cím").encode("utf-8"),
            item.get("SeasonIndex"),
            item.get("Index"),
        )
        original_name = item["OriginalName"]
        production_year = item["ProductionYear"]

        self.directory_manager.add_link(
            object_url,
            plot,
            age_rating,
            imdb,
            background_url,
            cast,
            director,
            writer,
            duration,
            genre,
            name,
            original_name,
            production_year,
            5,
        )
