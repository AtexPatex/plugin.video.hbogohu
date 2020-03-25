# -*- coding: utf-8 -*-

import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmc
from xbmcaddon import Addon


def gui_dialog_ok(title, message):
    xbmcgui.Dialog().ok(title, message)


def execute_builtin(task):
    xbmc.executebuiltin(task)


def translate_path(path):
    return xbmc.translatePath(path)


def gui_list_item(name, icon_image, thumbnail_image, path=None):
    return xbmcgui.ListItem(name, iconImage=icon_image, thumbnailImage=thumbnail_image, path=path)


def keyboard_modal(default, title):
    keyboard = xbmc.Keyboard(default, title)
    keyboard.doModal()
    if not keyboard.isConfirmed():
        exit()
    return keyboard.getText()


def add_directory_item(handle, url, list_item, is_folder):
    return xbmcplugin.addDirectoryItem(
        handle=handle, url=url, listitem=list_item, isFolder=is_folder
    )


def end_of_directory(__handle__):
    return xbmcplugin.endOfDirectory(__handle__)


def set_resolved_url(__handle__, succeeded, list_item):
    return xbmcplugin.setResolvedUrl(__handle__, succeeded, list_item)
