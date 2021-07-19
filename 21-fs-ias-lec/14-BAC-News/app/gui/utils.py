# -- standard python --
import os
import math
# -- PyQt --
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# loads fonts stored in /data/fonts for use in application
def load_fonts():
    # load custom fonts
    db = qtg.QFontDatabase()
    walbaum = os.getcwd() + "/data/fonts/Walbaum.ttf"
    merri_light = os.getcwd() + "/data/fonts/Merriweather-Light.ttf"
    merri_regular = os.getcwd() + "/data/fonts/Merriweather-Regular.ttf"
    merri_bold = os.getcwd() + "/data/fonts/Merriweather-Bold.ttf"
    merri_black = os.getcwd() + "/data/fonts/Merriweather-BlackItalic.ttf"
    merri_italic = os.getcwd() + "/data/fonts/Merriweather-Italic.ttf"
    assistant = os.getcwd() + "/data/fonts/Assistant.ttf"

    # add to application
    db.addApplicationFont(walbaum)
    db.addApplicationFont(merri_light)
    db.addApplicationFont(merri_regular)
    db.addApplicationFont(merri_bold)
    db.addApplicationFont(merri_black)
    db.addApplicationFont(merri_italic)
    db.addApplicationFont(assistant)

# used for determining starting window size
def get_screen_size(app):
    screen = app.primaryScreen()
    size = screen.size()
    w = size.width()
    h = size.height()
    return (w, h)

# scales the given window to 70% of screen size
def starting_screen_size(window, app):
    w, h = get_screen_size(app)
    # application takes up 70% of screen size on start
    RATIO = 0.7
    w = math.floor(RATIO * w)
    h = math.floor(RATIO * h)
    window.resize(w, h)

# clears every widget / layout from layout
# used for resetting window
def remove_widgets(layout):
    # iterate over every widget/layout in layout
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)

        # not ideal but seems to work
        # remove parents of widget
        if str(type(item)) == "<class 'PyQt5.QtWidgets.QWidgetItem'>":
            item.widget().setParent(None)
        else:
            if str(type(item)) != "<class 'PyQt5.QtWidgets.QSpacerItem'>":
                remove_widgets(item)
                item.layout().setParent(None)

# used for loading app icons of application
def load_app_icons(app):
    app_icon = qtg.QIcon()
    path = os.getcwd() + "/data/images/"
    app_icon.addFile(path + "16x16.png", qtc.QSize(16, 16))
    app_icon.addFile(path + "24x24.png", qtc.QSize(24, 24))
    app_icon.addFile(path + "32x32.png", qtc.QSize(32, 32))
    app_icon.addFile(path + "48x48.png", qtc.QSize(48, 48))
    app_icon.addFile(path + "256x256.png", qtc.QSize(256, 256))
    app.setWindowIcon(app_icon)

# removes reading indication from article title
def remove_dot(title):
    if not title.startswith("\u2022"):
        return title
    else:
        # remove dot and space in front of title
        return title[2:]
