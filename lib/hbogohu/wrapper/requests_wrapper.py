# -*- coding: utf-8 -*-

import requests


def get(url, headers):
    return requests.get(url, headers=headers)


def post(url, headers, data):
    return requests.post(url, headers=headers, data=data)
