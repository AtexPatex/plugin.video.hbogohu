# -*- coding: utf-8 -*-


def safe_encode(str):
    if not (str is None):
        return str.encode("utf-8", "ignore")
    else:
        return str