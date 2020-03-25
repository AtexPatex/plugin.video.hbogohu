# -*- coding: utf-8 -*-

from base64 import b64encode
from copy import copy
import inputstreamhelper
import json
import re
import urllib

from lib.hbogohu import headers, user_agent
from lib.hbogohu.auth import login
from lib.hbogohu.settings import SUBTITLE_AUTO_DOWNLOAD, OPERATOR_ID
from lib.hbogohu.wrapper import requests_wrapper, xbmc_wrapper


# lejatszas
def play(__hbo_go_plugin__):

    session = __hbo_go_plugin__.session
    settings = __hbo_go_plugin__.__settings__
    str_sub_path = __hbo_go_plugin__.srt_subs_path
    cid = __hbo_go_plugin__.cid
    thumbnail = __hbo_go_plugin__.thumbnail
    if not session.is_authenticated():
        login(__hbo_go_plugin__)

    if settings.get(SUBTITLE_AUTO_DOWNLOAD):
        try:
            # http://huapi.hbogo.eu/player50.svc/Content/json/HUN/COMP/
            # http://huapi.hbogo.eu/player50.svc/Content/json/HUN/APPLE/
            # http://huapi.hbogo.eu/player50.svc/Content/json/HUN/SONY/
            play_headers = copy(session.get_authenticated_headers())
            play_headers["User-Agent"] = user_agent.MOBILE
            response = requests_wrapper.get(
                "http://huapi.hbogo.eu/v5/Content/json/HUN/MOBI/" + cid,
                play_headers
            )
            json_response = response.json()

            try:
                lang_code = __hbo_go_plugin__.lang_code
                if json_response["Subtitles"][0]["Code"] == lang_code:
                    slink = json_response["Subtitles"][0]["Url"]
                elif json_response["Subtitles"][1]["Code"] == lang_code:
                    slink = json_response["Subtitles"][1]["Url"]
                data = requests_wrapper.get(slink, session.get_authenticated_headers()).text

                subs = re.compile(
                    r'<p[^>]+begin="([^"]+)\D(\d+)"[^>]+end="([^"]+)\D(\d+)"[^>]*>([\w\W]+?)</p>'
                ).findall(data)
                row = 0
                buffer = ""
                for sub in subs:
                    row = row + 1
                    buffer += str(row) + "\n"
                    buffer += (
                        "%s,%03d" % (sub[0], int(sub[1]))
                        + " --> "
                        + "%s,%03d" % (sub[2], int(sub[3]))
                        + "\n"
                    )
                    buffer += (
                        urllib.unquote_plus(sub[4])
                        .replace("<br/>", "\n")
                        .replace("<br />", "\n")
                        .replace("\r\n", "")
                        .replace("&lt;", "<")
                        .replace("&gt;", ">")
                        .replace("\n    ", "")
                        .strip()
                    )
                    buffer += "\n\n"
                    sub = "true"
                    with open(str_sub_path, "w") as sub_file:
                        sub_file.write(buffer)

                if sub != "true":
                    raise Exception()

            except:
                sub = "false"
        except:
            sub = "false"

    purchase_payload = (
        '<Purchase xmlns="go:v5:interop"><AllowHighResolution>true</AllowHighResolution><ContentId>'
        + cid
        + "</ContentId><CustomerId>"
        + session.go_customer_id
        + "</CustomerId><Individualization>"
        + session.individualization
        + "</Individualization><OperatorId>"
        + settings.get(OPERATOR_ID)
        + "</OperatorId><ClientInfo></ClientInfo><IsFree>false</IsFree><UseInteractivity>false</UseInteractivity>"
        + "</Purchase>"
    )

    purchase_headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "GO-CustomerId": str(session.go_customer_id),
        "GO-requiredPlatform": "CHBR",
        "GO-SessionId": str(session.session_id),
        "GO-swVersion": "4.7.4",
        "GO-Token": str(session.go_token),
        "Host": "huapi.hbogo.eu",
        "Referer": "https://hbogo.hu/",
        "Origin": "https://www.hbogo.hu",
        "User-Agent": user_agent.WEB,
    }

    response = requests_wrapper.post(
        "https://huapi.hbogo.eu/v5/Purchase/Json/HUN/COMP",
        purchase_headers,
        purchase_payload
    )
    json_response = response.json()

    if json_response.get("ErrorMessage"):
        xbmc_wrapper.gui_dialog_ok("Hiba", json_response["ErrorMessage"])

    media_url = json_response["Purchase"]["MediaUrl"] + "/Manifest"
    player_session_id = json_response["Purchase"]["PlayerSessionId"]
    x_dt_auth_token = json_response["Purchase"]["AuthToken"]

    dt_custom_data = b64encode(
        json.dumps(
            {
                "userId": session.go_customer_id,
                "sessionId": player_session_id,
                "merchant": "hboeurope",
            }
        )
    )

    li = xbmc_wrapper.gui_list_item(icon_image=thumbnail, thumbnail_image=thumbnail, path=media_url)
    if settings.get(SUBTITLE_AUTO_DOWNLOAD) and sub == "true":
        li.setSubtitles([str_sub_path])
    license_server = "https://lic.drmtoday.com/license-proxy-widevine/cenc/"
    license_headers = urllib.urlencode(
        {
            "dt-custom-data": dt_custom_data,
            "x-dt-auth-token": x_dt_auth_token,
            "Origin": "https://www.hbogo.hu",
            "Content-Type": "",
        }
    )
    license_key = license_server + "|" + license_headers + "|R{SSM}|JBlicense"

    protocol = "ism"
    drm = "com.widevine.alpha"
    is_helper = inputstreamhelper.Helper(protocol, drm=drm)
    is_helper.check_inputstream()
    li.setProperty("inputstreamaddon", "inputstream.adaptive")
    li.setProperty("inputstream.adaptive.manifest_type", protocol)
    li.setProperty("inputstream.adaptive.license_type", drm)
    li.setProperty("inputstream.adaptive.license_data", "ZmtqM2xqYVNkZmFsa3Izag==")
    li.setProperty("inputstream.adaptive.license_key", license_key)

    xbmc_wrapper.set_resolved_url(__hbo_go_plugin__.__handle__, True, li)
