# -*- coding: utf-8 -*-
from uuid import uuid4
import json

from lib.hbogohu import operators, headers
from lib.hbogohu.favorites import get_favorite_group
from lib.hbogohu.settings import DEVICE_ID, INDIVIDUALIZATION, FAVORITES_GROUP_ID, USERNAME, PASSWORD, OPERATOR, \
    OPERATOR_ID
from lib.hbogohu.wrapper import xbmc_wrapper, requests_wrapper


class Session:

    def __init__(self):
        self.session_id = operators.NON_AUTHENTICATED_OPERATOR_ID
        self.go_token = ""
        self.go_customer_id = ""
        pass

    def login(self, session_id):
        self.session_id = session_id

    def is_authenticated(self):
        return self.session_id != operators.NON_AUTHENTICATED_OPERATOR_ID

    def get_authenticated_headers(self):
        return self.__fill_headers(headers.authenticated)

    def __fill_headers(self, header):
        header["GO-Token"] = str(self.go_token)
        header["GO-SessionId"] = str(self.session_id)
        header["GO-CustomerId"] = str(self.go_customer_id)
        return header


def login(__hbo_go_plugin__):
    # belepes

    settings = __hbo_go_plugin__.__settings__
    add_on = __hbo_go_plugin__.__add_on__
    if not all((settings.get(INDIVIDUALIZATION), settings.get(DEVICE_ID))):
        generate_individualization(settings)

    if not settings.get(FAVORITES_GROUP_ID):
        get_favorite_group(__hbo_go_plugin__)

    if not all((settings.get(USERNAME), settings.get(PASSWORD))):
        xbmc_wrapper.gui_dialog_ok("Hiba", "Kérlek add meg a beállításoknál a belépési adatokat!")
        add_on.openSettings("Accunt")
        xbmc_wrapper.execute_builtin("Container.Refresh")
        login(__hbo_go_plugin__)


    # TODO: a gatewayes hivasok helyett lehet vissza lehet alni a bulgar verziora, de jelenleg igy tuti mukodik
    # a linkek a weboldalrol lettek kiszedve
    if settings.get(OPERATOR) == 1:
        url = "https://api.ugw.hbogo.eu/v3.0/Authentication/HUN/JSON/HUN/COMP"
    else:
        url = "https://hugwapi.hbogo.eu/v2.1/Authentication/json/HUN/COMP"

    data_obj = {
        "Action": "L",
        "AppLanguage": None,
        "ActivationCode": None,
        "AllowedContents": [],
        "AudioLanguage": None,
        "AutoPlayNext": False,
        "BirthYear": 1,
        "CurrentDevice": {
            "AppLanguage": "",
            "AutoPlayNext": False,
            "Brand": "Chromium",
            "CreatedDate": "",
            "DeletedDate": "",
            "Id": operators.NON_AUTHENTICATED_OPERATOR_ID,
            "Individualization": settings.get(INDIVIDUALIZATION),
            "IsDeleted": False,
            "LastUsed": "",
            "Modell": "62",
            "Name": "",
            "OSName": "Ubuntu",
            "OSVersion": "undefined",
            "Platform": "COMP",
            "SWVersion": "2.4.2.4025.240",
            "SubtitleSize": "",
        },
        "CustomerCode": "",
        "DebugMode": False,
        "DefaultSubtitleLanguage": None,
        "EmailAddress": settings.get(USERNAME),
        "FirstName": "",
        "Gender": 0,
        "Id": operators.NON_AUTHENTICATED_OPERATOR_ID,
        "IsAnonymus": True,
        "IsPromo": False,
        "Language": "HUN",
        "LastName": "",
        "Nick": "",
        "NotificationChanges": 0,
        "OperatorId": settings.get(OPERATOR_ID),
        "OperatorName": "",
        "OperatorToken": "",
        "ParentalControl": {
            "Active": False,
            "Password": "",
            "Rating": 0,
            "ReferenceId": operators.NON_AUTHENTICATED_OPERATOR_ID,
        },
        "Password": settings.get(PASSWORD),
        "PromoCode": "",
        "ReferenceId": operators.NON_AUTHENTICATED_OPERATOR_ID,
        "SecondaryEmailAddress": "",
        "SecondarySpecificData": None,
        "ServiceCode": "",
        "SubscribeForNewsletter": False,
        "SubscState": None,
        "SubtitleSize": "",
        "TVPinCode": "",
        "ZipCode": "",
    }

    data = json.dumps(data_obj)
    response = requests_wrapper.post(url, headers.non_authenticated, data)

    json_response = response.json()

    if json_response.get("ErrorMessage"):
        xbmc_wrapper.gui_dialog_ok("Login Hiba!", json_response["ErrorMessage"])

    settings.store(DEVICE_ID, json_response["Customer"]["CurrentDevice"]["Id"])
    settings.store(INDIVIDUALIZATION, json_response["Customer"]["CurrentDevice"]["Individualization"])

    __hbo_go_plugin__.session.login(json_response["SessionId"])
    if not __hbo_go_plugin__.session.is_authenticated():
        xbmc_wrapper.gui_dialog_ok("Login Hiba!", "Ellenőrizd a belépési adatokat!")
        add_on.openSettings("Accunt")
        xbmc_wrapper.execute_builtin("Action(Back)")
    else:
        __hbo_go_plugin__.session.go_token = json_response["Token"]
        __hbo_go_plugin__.session.go_customer_id = json_response["Customer"]["Id"]


def generate_individualization(__settings__):
    # individualization es customerId eltarolasa

    if not __settings__.get(INDIVIDUALIZATION):
        __settings__.store(INDIVIDUALIZATION, str(uuid4()))

    if not __settings__.get(DEVICE_ID):
        __settings__.store(DEVICE_ID, str(uuid4()))
