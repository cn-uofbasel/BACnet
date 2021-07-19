from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

def setArticleStyle(article):
    # style sheet for displayed article
    article.document().setDefaultStyleSheet(
        "body {font-family: Merriweather;} "
        "p {font-size: 18px; line-height: 1.5; font-weight: 300;} "
        "h1 {font-weight: bold; font-style: italic;} "
        "h3 {color: lightgrey;}"
        "h2 {color: grey;}"
        "ul {text-indent: 0px; margin-left: 0px; padding-left: 0px;}"
        "li {list-style-type: disc; font-size: 16px; line-height: 1.5; font-style: italic; margin-left: 0px; padding-left: 0px;}"
    )
    return

def getLightStyleSheet():
    # light mode style sheet
    stylesheet = """
    QWidget {
        background-color: #f7f7f7;
        color: black;
        padding: 0px;
        margin: 0px;
        font-family: Merriweather;
    }
    QTextBrowser {
        background-color: #f7f7f7;
        border-style: none;
        border-left: 5px;
        padding-right: 100px;
        padding-left: 50px;
        padding-top: 10px;
        margin-right: 0px;
    }
    QTextBrowser QScrollBar {
        height: 0px;
        width: 0px;
    }
    QListWidget QScrollBar {
        height: 0px;
        width: 0px;
    }
    QPushButton {
        font-weight: light;
        font-size: 15px;
    }
    QListWidget {
        font-family: Assistant;
        font-weight: 400;
        font-size: 18px;
        line-height: 2;
        border-style: none;
        spacing: 10;
    }
    QListWidget::Item {
        padding-top: 5px;
        padding-bottom: 5px;  
        border-bottom: 1px solid lightgrey;  
        border-radius: 3px;
    }
    QListWidget::Item:selected {
        color: #f7f7f7;
        background-color: black;
        margin: 0px;
        padding: 0px;
        border-radius: 3px;
    }
    #logo {
        font-size: 40px;
        font-weight: bold;
        font-family: Walbaum Fraktur;
    }
    QPushButton {
        height: 50%;
        border-style: none;
        font-family: Assistant;
        font-weight: 500;
        font-size: 16px;
    }
    #main {
    }
    #container {
        border-bottom: 1px solid lightgrey;
    }
    #selected {
        color: red;
    }
    #srfButton {
        background-color: #AF011E;
        color: #f7f7f7;
        border-radius: 3px;
    }
    #srfButton:pressed {
        background-color: #f7f7f7;
        color: #AF011E;
        border-style: solid;
        border-width: 1px;
        border-color: #AF011E;
    }
    #blueButton {
        background-color: #0C3C91;
        color: #f7f7f7;
        border-radius: 3px;
    }
    #blueButton:pressed {
        background-color: #f7f7f7;
        color: #0C3C91;
        border-style: solid;
        border-width: 1px;
        border-color: #0C3C91;
    }
    #downloadTitle {
        font-size: 20px;
    }
    #toggleTrue {
        color: grey;
    }
    #toggleFalse {
        color: black;
    }
    #bacButton {
        color: #f7f7f7;
        background-color: black;
        border-radius: 3px;
        border-style: none;
    }
    #bacButton:pressed {
        color: black;
        background-color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: black;
    }
    #manualButton {
        color: black;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
        border: 1px solid black
    }
    #manualButton:pressed {
        color: #f7f7f7;
        background-color: black;
        border-style none;
    }
    #manualButton2 {
        margin-top: 50px;
        color: black;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
        border: 1px solid black
    }
    #manualButton2:pressed {
        color: #f7f7f7;
        background-color: black;
        border-style none;
    }

    #gif {
        margin-bottom: 100px;
    }
    #connectButton {
        background-color: black;
        color: #f7f7f7;
        border-radius: 5px;
        padding: 5px;
    }
    #connectButton:pressed {
        background-color: #f7f7f7;
        border-style: solid;
        border-radius: 1px;
        border-color: black;
        color: black;
    }
    #lan-title {
        font-family: Assistant;
        font-size: 20px;
        margin-bottom: 10px;
        margin-top: 5px;
    }
    #server-text {
        font-family: Assistant;
        font-size: 50px;
        margin-bottom: 40px;
        text-align: center;
    }
    #filter-layout {
        margin: 0px;
        padding: 0px;
    }
    #filter-btn {
        padding: 0px;
        margin: 0px;
        height: 20%;
    }
    #filter-btn-selected {
        padding: 0px;
        margin: 0px;
        height: 20%;
        color: grey;
    }
    #bookmark {
        padding: 0px;
        margin: 0px;
        font-size: 100px;
        height: 40px;
    }
    #bookmark-btn {
    }
    #combo {
        margin-bottom: 5px;
    }
    QComboBox {
        color: black;
        background-color: #f7f7f7;
        border: 1px solid black;
        border-radius: 3px;
        padding: 5px;
        font-family: Assistant;
        font-size: 16px;
    }
    QComboBox::Item {
        background-color: black;
        color: #f7f7f7;
    }
    QComboBox::Item:selected {
        background-color: #f7f7f7;
        color: black;
    }
    QComboBox::drop-down {
        border-radius: 3px;
    }
    #client-text {
        font-family: Assistant;
        font-size: 35px;
        text-align: center;
        margin-bottom: 10px;
    }
    QLineEdit {
        font-family: Assistant;
        font-size: 25px;
        border: 1px solid #f7f7f7;
        background-color: black;
        padding: 5px;
        border-radius: 3px;
    }
    QLineEdit:focus {
        background: #f7f7f7;
        color: black;
        border: 1px solid black;
        outline: none;
        show-decoration-selected: 0;
    }   
    #bt-client-btn {
        color: #f7f7f7;
        background-color: black;
        border-radius: 3px;
        border-style: none;
        margin-top: 10px;
        margin-bottom: 100px;
    }
    #bt-client-btn:pressed {
        color: black;
        background-color: #f7f7f7;
        border: 1px solid black;
        border-radius: 3px;
        margin-top: 10px;
    }
    #loginBtn {
        color: #f7f7f7;
        background-color: black;
        border-radius: 3px;
        border-style: none;
        margin-bottom: 50px;
    }
    #loginBtn:pressed {
        color: black;
        background-color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: black;
    }
    #bac-text {
        font-family: Assistant;
        font-size: 35px;
        text-align: center;
        margin-bottom: 10px;
    }"""
    return stylesheet

def getDarkStyleSheet():
    # dark mode style sheet
    stylesheet = """
    QWidget {
        background-color: #282828;
        color: #f7f7f7;
        padding: 0px;
        margin: 0px;
        font-family: Merriweather;
    }
    QTextBrowser {
        background-color: #282828;
        color: #f7f7f7;
        border-style: none;
        border-left: 5px;
        padding-right: 100px;
        padding-left: 50px;
        padding-top: 10px;
    }
    QTextBrowser QScrollBar {
        height: 0px;
        width: 0px;
    }
    QListWidget QScrollBar {
        height: 0px;
        width: 0px;
    }
    QPushButton {
        font-weight: light;
        font-size: 15px;
    }
    QListWidget {
        font-family: Assistant;
        font-weight: 400;
        font-size: 18px;
        line-height: 2;
        border-style: none;
        spacing: 10;
    }
    QListWidget::Item {
        padding-top: 5px;
        padding-bottom: 5px;
        border-bottom: 1px solid lightgrey;  
    }
    QListWidget::Item:selected {
        color: #282828;
        background-color: #f7f7f7;
        margin: 0px;
        padding: 0px;
        border-radius: 3px;
    }
    #logo {
        font-size: 40px;
        font-weight: bold;
        font-family: Walbaum Fraktur;
    }
    QPushButton {
        height: 50%;
        border-style: none;
        font-family: Assistant;
        font-weight: 500;
        font-size 16px;
    }
    #main {
    }
    #container {
        border-bottom: 1px solid lightgrey;
    }
    #selected {
        color: red;
    }
    #srfButton {
        background-color: #f7f7f7;
        color: #AF011E;
        border-radius: 3px;
        border-style: none;
    }
    #srfButton:pressed {
        background-color: #AF011E;
        color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #blueButton {
        background-color: #f7f7f7;
        color: #0C3C91;
        border-radius: 3px;
    }
    #blueButton:pressed {
        background-color: #0C3C91;
        color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #downloadTitle {
        font-size: 20px;
    }
    #toggleTrue {
        color: grey;
    }
    #toggleFalse {
        color: #f7f7f7;
    }
    #bacButton {
        color: #282828;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
    }
    #bacButton:pressed {
        color: #f7f7f7;
        background-color: #282828;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #manualButton {
        color: #f7f7f7;
        background-color: #282828;
        border-radius: 3px;
        border-style: none;
        border: 1px solid #f7f7f7;
    }
    #manualButton:pressed {
        color: #282828;
        background-color: #f7f7f7;
    }
    #manualButton2 {
        margin-top: 50px;
        color: #f7f7f7;
        background-color: #282828;
        border-radius: 3px;
        border-style: none;
        border: 1px solid #f7f7f7;
    }
    #manualButton2:pressed {
        color: #282828;
        background-color: #f7f7f7;
        border-style: none;
    }

    #gif {
        margin-bottom: 100px;
    }
    #lan-title {
        font-family: Assistant;
        font-size: 20px;
        margin-bottom: 10px;
        margin-top: 5px;
    }
    #server-text {
        font-family: Assistant;
        font-size: 50px;
        margin-bottom: 40px;
        text-align: center;
    }
    #filter-layout {
        margin: 0px;
        padding: 0px;
    }
    #filter-btn {
        padding: 0px;
        margin: 0px;
        height: 20%;
        color: #f7f7f7;
    }
    #filter-btn-selected {
        padding: 0px;
        margin: 0px;
        height: 20%;
        color: grey;
    }
    #bookmark {
        padding: 0px;
        margin: 0px;
        font-size: 100px;
        height: 40px;
    }
    #bookmark-btn {
    }
    #combo {
        margin-bottom: 5px;
    }
    QComboBox {
        color: #f7f7f7;
        background-color: #282828;
        border: 1px solid #f7f7f7;
        border-radius: 3px;
        padding: 5px;
        font-family: Assistant;
        font-size: 16px;
    }
    QComboBox::Item {
        background-color: #f7f7f7;
        color: #282828;
    }
    QComboBox::Item:selected {
        background-color: #282828;
        color: #f7f7f7;
    }
    QComboBox::drop-down {
        border-radius: 3px;
    }
    #client-text {
        font-family: Assistant;
        font-size: 35px;
        text-align: center;
        margin-bottom: 10px;
    }
    QLineEdit {
        font-family: Assistant;
        font-size: 25px;
        border: 1px solid #282828;
        background-color: #f7f7f7;
        padding: 5px;
        border-radius: 3px;
    }
    QLineEdit:focus {
        background: #282828;
        color: #f7f7f7;
        border: 1px solid #f7f7f7;
        outline: none;
        show-decoration-selected: 0;
    }   
    #bt-client-btn {
        color: #282828;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
        margin-top: 10px;
        margin-bottom: 100px;
    }
    #bt-client-btn:pressed {
        color: #f7f7f7;
        background-color: #282828;
        border: 1px solid #f7f7f7;
        border-radius: 3px;
        margin-top: 10px;
    }
    #loginBtn {
        color: #282828;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
        margin-bottom: 50px;
    }
    #loginBtn:pressed {
        color: #f7f7f7;
        background-color: #282828;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #bac-text {
        font-family: Assistant;
        font-size: 35px;
        text-align: center;
        margin-bottom: 10px;
    }"""
    return stylesheet
