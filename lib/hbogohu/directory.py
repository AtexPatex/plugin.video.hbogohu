# -*- coding: utf-8 -*-
import urllib

from lib.hbogohu.wrapper import xbmc_wrapper


class DirectoryManager:

    def __init__(self, __hbo_go_plugin__):
        self.base_url = __hbo_go_plugin__.__base_url__
        self.handle = __hbo_go_plugin__.__handle__
        self.url = __hbo_go_plugin__.url

    def add_link(self, ou, plot, ar, imdb, bu, cast, director, writer, duration, genre, name, on, py, mode):
        cid = ou.rsplit("/", 2)[1]

        u = (
            self.base_url
            + "?"
            + urllib.urlencode(
                {"url": self.url, "mode": str(mode), "name:": name, "cid": cid, "thumbnail": bu}
            )
        )

        liz = xbmc_wrapper.gui_list_item(name, icon_image=bu, thumbnail_image=bu)
        liz.setArt({"thumb": bu, "poster": bu, "banner": bu, "fanart": bu})
        liz.setInfo(
            type="Video",
            infoLabels={
                "plot": plot,
                "mpaa": str(ar) + "+",
                "rating": imdb,
                "cast": cast,
                "director": director,
                "writer": writer,
                "duration": duration,
                "genre": genre,
                "title": name,
                "originaltitle": on,
                "year": py,
            },
        )
        liz.addStreamInfo("video", {"width": 1280, "height": 720})
        liz.addStreamInfo("video", {"aspect": 1.78, "codec": "h264"})
        liz.addStreamInfo("audio", {"codec": "aac", "channels": 2})
        liz.setProperty("IsPlayable", "true")
        ok = xbmc_wrapper.add_directory_item(self.handle, u, liz, False)
        return ok

    def add_directory(self, name, url, plot, mode, icon_image):
        u = (
            self.base_url
            + "?"
            + urllib.urlencode({"url": url, "mode": str(mode), "name": name})
        )

        liz = xbmc_wrapper.gui_list_item(
            name, icon_image="DefaultFolder.png", thumbnail_image=icon_image
        )
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})

        ok = xbmc_wrapper.add_directory_item(
            handle=self.handle, url=u, list_item=liz, is_folder=True
        )

        return ok
