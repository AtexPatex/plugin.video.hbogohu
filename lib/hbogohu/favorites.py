# -*- coding: utf-8 -*-
from lib.hbogohu.settings import FAVORITES_GROUP_ID
from lib.hbogohu.wrapper import requests_wrapper


def get_favorite_group(__hbo_go_plugin__):
    # lejatszasi lista id lekerdezes

    response = requests_wrapper.get("https://huapi.hbogo.eu/v7/Settings/json/HUN/COMP",
                                    __hbo_go_plugin__.session.get_authenticated_headers())
    json_rsp = response.json()

    __hbo_go_plugin__.__settings__.store(FAVORITES_GROUP_ID, json_rsp["FavoritesGroupId"])
