# -*- coding: utf-8 -*-

import sys
from xbmcaddon import Addon

from lib.hbogohu.plugin import HboGoPlugin

if __name__ == "__main__":

    __hbo_go_plugin__ = HboGoPlugin(Addon(), sys.argv)
    __hbo_go_plugin__.run()

# vim: sw=2:ts=2:noexpandtab
