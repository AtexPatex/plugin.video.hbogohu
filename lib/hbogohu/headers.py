# -*- coding: utf-8 -*-
from lib.hbogohu import user_agent, operators

non_authenticated = {
    "Origin": "https://gateway.hbogo.eu",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "hu,en-US;q=0.9,en;q=0.8",
    "User-Agent": user_agent.WEB,
    "GO-Token": "",
    "Accept": "application/json",
    "GO-SessionId": "",
    "Referer": "https://gateway.hbogo.eu/signin/form",
    "Connection": "keep-alive",
    "GO-CustomerId": operators.NON_AUTHENTICATED_OPERATOR_ID,
    "Content-Type": "application/json",
}

authenticated = {
    "User-Agent": user_agent.WEB,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.hbogo.hu/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.hbogo.hu",
    "X-Requested-With": "XMLHttpRequest",
    "GO-Language": "HUN",
    "GO-requiredPlatform": "CHBR",
    "GO-Token": "",
    "GO-SessionId": "",
    "GO-swVersion": "4.8.0",
    "GO-CustomerId": "",
    "Connection": "keep-alive",
    "Accept-Encoding": "",
}
