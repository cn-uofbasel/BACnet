# -- standard python --
import os
import queue
# -- PyQt --
import qtawesome as qta
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
# -- own classes --
import gui.utils as utils
import gui.style as style
import transfer.local_network as net
from logic.article import Category
from logic.interface import LogicInterface as Logic
from gui.interface import Interface
from transfer.LAN_server import LANServer
from transfer.LAN_client import LANClient
from transfer.bt_server import bt_server as BTServer
from transfer.bt_client import bt_client as BTClient
from bacnet.core import BACCore
from logic.article import Article

# own label class that can be clicked like a QPushButton
class imageLabel(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    def mouseReleaseEvent(self, ev):
        if ev.button() == qtc.Qt.LeftButton:
            self.clicked.emit()

# QThread that downloads articles via logic.download_new_articles
class downloadingThread(qtc.QThread):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic

    def run(self):
        self.logic.download_new_articles()

# QThread that downloads articles via LAN connection
class LANThread(qtc.QThread):
    def __init__(self, LAN_client, ip, queue):
        super().__init__()
        self.LAN_client = LAN_client
        self.ip = ip
        self.queue = queue

    def run(self):
        ret = self.LAN_client.start_client(self.ip)
        if ret == 1:
            self.queue.put(False)
        else:
            self.queue.put(True)

# QThread that downloads articles via Bluetooth connection
class BTThread(qtc.QThread):
    def __init__(self, BT_client, mac):
        super().__init__()
        self.BT_client = BT_client
        self.mac = mac

    def run(self):
        self.BT_client.start_client(self.mac)

# QThread that exports bac feeds to given path
class BACExportThread(qtc.QThread):
    def __init__(self, core, path):
        super().__init__()
        self.core = core
        self.path = path

    def run(self):
        self.core.export_db_to_pcap(self.path)

# QThread that imports .pcap files from given path
class BACImportThread(qtc.QThread):
    def __init__(self, core, path):
        super().__init__()
        self.core = core
        self.path = path

    def run(self):
        self.core.import_from_pcap_to_db(self.path)

# new window for displaying articles
class externalWindow(qtw.QWidget):
    def __init__(self, title, html, w, h, light):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(w, h)

        if light:
            self.setStyleSheet(style.getLightStyleSheet())
        else:
            self.setStyleSheet(style.getDarkStyleSheet())

        # create reader
        reader = qtw.QTextBrowser()
        style.setArticleStyle(reader)
        reader.setOpenExternalLinks(True)
        reader.insertHtml(html)
        reader.moveCursor(qtg.QTextCursor.Start)

        layout = qtw.QVBoxLayout()
        layout.addWidget(reader)

        self.setLayout(layout)

    def switch(self, light):
        if light:
            self.setStyleSheet(style.getLightStyleSheet())
        else:
            self.setStyleSheet(style.getDarkStyleSheet())

# pop up window for selecting bac-net feed on which to append article to
class bacPopUp(qtw.QDialog):
    def __init__(self, core, json):
        super().__init__()
        self.setMinimumWidth(300)
        self.core = core
        self.json = json

        #create widgets
        title = qtw.QLabel("Select feed:")

        selector = qtw.QComboBox()
        selector.addItems(core.get_feednames_from_host())
        self.selector = selector

        btn = qtw.QPushButton("append")
        btn.clicked.connect(self.append)

        # create layout and add widgets
        form = qtw.QFormLayout(self)
        form.addRow(title)
        form.addRow(selector)
        form.addRow(btn)

    # appends the current article to selected feed
    def append(self):
        feed = self.selector.currentText()
        self.core.create_event(feed, self.json)
        self.close()

# main GUI class
class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # diverse inits
        self.server_socket = None
        self.active_article_filter = None
        self.today_btn = None
        self.week_btn = None
        self.all_btn = None
        self.downLayout = None
        self.srfBtn = None
        self.bookmark = None
        self.bookmark_gif = None
        self.bookmark_active = False
        self.archive_reader = None
        self.mdi_btn = None
        self.combo = None
        self.current_title = None
        self.downloading_thread = None
        self.lan_thread = None
        self.lan_is_downloading = False
        self.BT_is_downloading = False
        self.MAC_input = None
        self.IP_input = None
        self.BT_thread = None
        self.download_status = queue.Queue()
        self.external_btn = None
        self.open_windows = []
        self.login = None
        self.bac_core = BACCore()
        self.feed_input = None
        self.bac_btn = None
        self.active_feed = None
        self.articles_in_feeds = None
        self.bac_selector = None
        self.bac_article_lst = None
        self.bac_selector = None
        self.bac_articles = []
        self.bac_reader = None
        self.bac_import_thread = None
        self.bac_export_thread = None

        # initiate window
        super().__init__(windowTitle="BAC News")

        # keyboard shortcuts
        self.shortcut_book = qtw.QShortcut(qtg.QKeySequence("Ctrl+B"), self)
        self.shortcut_book.activated.connect(self.update_bookmark)
        self.shortcut_open = qtw.QShortcut(qtg.QKeySequence("Ctrl+O"), self)
        self.shortcut_open.activated.connect(self.open_external)
        self.shortcut_new = qtw.QShortcut(qtg.QKeySequence("Ctrl+D"), self)
        self.shortcut_new.activated.connect(self.set_downloading_section)
        self.shortcut_archive = qtw.QShortcut(qtg.QKeySequence("Ctrl+A"), self)
        self.shortcut_archive.activated.connect(self.set_archiving_section)
        self.shortcut_switch = qtw.QShortcut(qtg.QKeySequence("Ctrl+S"), self)
        self.shortcut_switch.activated.connect(self.switch)
        self.shortcut_read = qtw.QShortcut(qtg.QKeySequence("Ctrl+R"), self)
        self.shortcut_read.activated.connect(self.set_reading_section)
        self.shortcut_today = qtw.QShortcut(qtg.QKeySequence("1"), self)
        self.shortcut_today.activated.connect(self.switch_today)
        self.shortcut_week = qtw.QShortcut(qtg.QKeySequence("2"), self)
        self.shortcut_week.activated.connect(self.switch_week)
        self.shortcut_all = qtw.QShortcut(qtg.QKeySequence("3"), self)
        self.shortcut_all.activated.connect(self.switch_all)

        # for interacting with back-end
        self.interface = Interface(self)
        self.logic = Logic()
        self.LAN_client = LANClient()
        self.LAN_server = LANServer()
        self.BT_server = BTServer()
        self.BT_client = BTClient()

        # load app icons
        utils.load_app_icons(app)

        # load fonts used in ui
        utils.load_fonts()

        # start in light theme
        self.light = True
        self.setStyleSheet(style.getLightStyleSheet())

        # used for styling in css
        self.setObjectName("main")

        # grid layout for placing items, 100 rows, 100 cols
        # main part of program
        self.main = qtw.QGridLayout()

        # get menu bar
        menu = self.get_menu_bar()

        # start with article view
        self.set_reading_section()

        # master layout with menu and active section
        superLayout = qtw.QGridLayout()
        superLayout.setObjectName("super")
        # add menu and main
        superLayout.addWidget(menu, 0, 0, 10, 100)
        superLayout.addLayout(self.main, 10, 0, 90, 100)

        # configure window and application details and show
        self.setLayout(superLayout)
        utils.starting_screen_size(self, app)
        self.setMinimumSize(700, 500)
        self.show()

    # if application is closed
    def closeEvent(self, event):
        # stop diverse servers
        self.LAN_server.stop_server()
        self.BT_server.stop_server()

    # menu bar of app
    def get_menu_bar(self):
        # menu bar on top of screen
        menu = qtw.QHBoxLayout()

        # logo, top left
        logo = qtw.QLabel(text="News")
        logo.setObjectName("logo")
        menu.addWidget(logo)

        # menu items
        # from left to right
        # button 1 -- reading section
        self.b1 = qtw.QPushButton(text="read")
        self.b1.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b1.clicked.connect(self.set_reading_section)

        # used for setting style of currently selected section
        self.selected = self.b1

        # button 2 -- downloading section
        self.b2 = qtw.QPushButton(text="get new articles")
        self.b2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b2.clicked.connect(self.set_downloading_section)

        # button3 -- archive section
        self.b3 = qtw.QPushButton(text="archive")
        self.b3.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b3.clicked.connect(self.set_archiving_section)

        # button 4 -- dark/light mode toggle
        self.b4 = qtw.QPushButton(text="dark")
        self.b4.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b4.clicked.connect(self.switch)
        # switch for changing UI style sheet
        self.switch = self.b4

        # button 5 -- BAC-net, last addition
        self.b5 = qtw.QPushButton(text="BAC-net")
        self.b5.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b5.clicked.connect(self.set_BAC_section)

        # ordering
        menu.addWidget(self.b1) # reader
        menu.addWidget(self.b5) # BAC-net
        menu.addWidget(self.b3) # archive
        menu.addWidget(self.b2) # get new articles
        menu.addWidget(self.b4) # dark/light mode switch

        # container for menu bar
        container = qtw.QWidget()
        # for styling
        container.setObjectName("container")
        # add menu to container
        container.setLayout(menu)

        return container

    # main reading section of app
    def set_reading_section(self):
        # clear previous layout
        self.tab_changed()
        self.set_selected_menu_button(self.b1)

        # main article box, HTML reader
        text = qtw.QTextBrowser()
        self.article = text
        # css styling for article
        style.setArticleStyle(self.article)
        text.setOpenExternalLinks(True)

        #article selector, LHS of app
        selector = qtw.QListWidget()
        self.selector = selector
        selector.setWordWrap(True)
        # read articles from /data/articles folder
        entries = self.get_article_lst()
        selector.addItems(entries)
        # add event for user input
        selector.itemSelectionChanged.connect(self.selected_article_changed)
        # start with first article selected
        selector.setCurrentRow(0)
        # move cursor to start of text
        text.moveCursor(qtg.QTextCursor.Start)

        # bookmark for moving articles to archive section
        if self.light:
            color = "black"
        else:
            color = "#f7f7f7"

        mdi_book = qta.icon("mdi.bookmark-outline", color=color)
        mdi_book_btn = qtw.QPushButton()
        mdi_book_btn.setObjectName("bookmark-btn")
        mdi_book_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        mdi_book_btn.clicked.connect(self.update_bookmark)
        mdi_book_btn.setIconSize(qtc.QSize(40, 40))
        mdi_book_btn.setIcon(mdi_book)
        mdi_book_btn.setToolTip("archive article")
        self.mdi_btn = mdi_book_btn
        self.draw_bookmark()

        # for opening articles in own windows
        mdi_external = qta.icon("mdi.open-in-new", color=color)
        external_btn = qtw.QPushButton()
        external_btn.setObjectName("bookmark-btn")
        external_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        external_btn.clicked.connect(self.open_external)
        external_btn.setIconSize(qtc.QSize(35, 35))
        external_btn.setIcon(mdi_external)
        external_btn.setToolTip("open in new window")
        self.external_btn = external_btn

        # for sharing on bac net
        mdi_bac = qta.icon("mdi.folder-key-network", color=color)
        bac_btn = qtw.QPushButton()
        bac_btn.setObjectName("bookmark-btn")
        bac_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        bac_btn.clicked.connect(self.handle_bac_net)
        bac_btn.setIconSize(qtc.QSize(35, 35))
        bac_btn.setIcon(mdi_bac)
        bac_btn.setToolTip("add to BAC-net")
        self.bac_btn = bac_btn

        # article filters
        self.today_btn = qtw.QPushButton(text="today")
        self.today_btn.setObjectName("filter-btn-selected")
        self.today_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.today_btn.clicked.connect(self.switch_today)
        # start with "today" article filter
        self.active_article_filter = self.today_btn

        self.week_btn = qtw.QPushButton(text="week")
        self.week_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.week_btn.clicked.connect(self.switch_week)
        self.week_btn.setObjectName("filter-btn")

        self.all_btn = qtw.QPushButton(text="all")
        self.all_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.all_btn.clicked.connect(self.switch_all)
        self.all_btn.setObjectName("filter-btn")

        filter_layout = qtw.QHBoxLayout()
        filter_layout.setObjectName("filter-layout")
        filter_layout.addWidget(self.today_btn)
        filter_layout.addWidget(self.week_btn)
        filter_layout.addWidget(self.all_btn)
        # -- end of filters --

        # category chooser
        combo = qtw.QComboBox()
        combo.setObjectName("combo")
        combo.setToolTip("select category")
        combo.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        combo.addItem("All Categories")
        combo.addItem("Switzerland")
        combo.addItem("International")
        combo.addItem("Economics")
        combo.addItem("Culture")
        combo.addItem("Sports")
        combo.addItem("Meteo")
        combo.addItem("Panorama")
        # if selection changed
        combo.activated[str].connect(self.filter_selection_changed)
        self.combo = combo

        # left of article reader
        lhs_layout = qtw.QVBoxLayout()
        lhs_layout.addLayout(filter_layout)
        lhs_layout.addWidget(combo)
        lhs_layout.addWidget(selector)

        # right of article reader
        rhs_layout = qtw.QVBoxLayout()
        rhs_layout.addWidget(mdi_book_btn)
        rhs_layout.addWidget(bac_btn)
        rhs_layout.addWidget(external_btn)
        rhs_layout.addStretch()

        # article selector 20% of content
        self.main.addLayout(lhs_layout, 0, 0, 100, 20)
        # article 75% of content
        self.main.addWidget(text, 0, 20, 100, 75)
        # bookmarks etc. 5% of content
        self.main.addLayout(rhs_layout, 0, 95, 100, 5)

    # downloading and sharing section of app
    def set_downloading_section(self):
        if self.logic.is_updating or self.lan_is_downloading or self.BT_is_downloading:
            # show loading screen if currently downloading
            self.set_loading_screen_section()
            return

        # clear main layout
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # layouts
        downLayout = qtw.QVBoxLayout()
        downLayout.setContentsMargins(200, 30, 200, 0)
        toggleLayout = qtw.QHBoxLayout()

        # -- begin toggles for switching between sharing and downloading --
        toggle = qtw.QPushButton(text="import")
        toggle.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        toggle.setCheckable(True)
        # start in downloading mode
        toggle.setChecked(True)
        toggle.clicked.connect(self.toggle_download)
        toggle.setObjectName("toggleTrue")
        self.toggle = toggle

        toggle2 = qtw.QPushButton(text="export")
        toggle2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        toggle2.setCheckable(True)
        toggle2.setChecked(False)
        toggle2.clicked.connect(self.toggle2_download)
        toggle2.setObjectName("toggleFalse")
        self.toggle2 = toggle2

        toggleLayout.addWidget(toggle)
        toggleLayout.addWidget(toggle2)
        # -- end of toggles --

        srfB = qtw.QPushButton(text="SRF")
        srfB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        srfB.clicked.connect(self.handle_download)
        srfB.setObjectName("srfButton")

        blueB = qtw.QPushButton(text="bluetooth")
        blueB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        blueB.clicked.connect(self.switch_blue)
        blueB.setObjectName("blueButton")

        bacB = qtw.QPushButton(text="BAC-Net")
        bacB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        bacB.clicked.connect(self.switch_bac)
        bacB.setObjectName("bacButton")

        localB = qtw.QPushButton(text="local network")
        localB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        localB.clicked.connect(self.switch_wlan)
        localB.setObjectName("bacButton")

        # add buttons to download layout
        downLayout.addLayout(toggleLayout)
        downLayout.addWidget(srfB)
        downLayout.addWidget(bacB)

        on_macOS = self.BT_server.on_macOS()

        if not on_macOS:
            downLayout.addWidget(blueB)
        # for testing:
        #downLayout.addWidget(blueB)

        downLayout.addWidget(localB)
        downLayout.addStretch()
        self.downLayout = downLayout
        self.srfBtn = srfB

        # add to layout
        self.main.addLayout(downLayout, 0, 0)

    # downloading animation
    def set_loading_screen_section(self):
        # reset layout
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        #new layouts
        layout = qtw.QVBoxLayout()
        centering_layout = qtw.QHBoxLayout()

        # get correct gif
        if self.light:
            gif_path = os.getcwd() + "/data/images/loading_light.gif"
        else:
            gif_path = os.getcwd() + "/data/images/loading_dark.gif"
        loading = qtg.QMovie(gif_path)

        loading_label = qtw.QLabel()
        loading_label.setObjectName("gif")
        loading_label.setMovie(loading)
        loading.start()

        layout.addStretch()
        layout.addWidget(loading_label)
        layout.addStretch()

        centering_layout.addStretch()
        centering_layout.addWidget(loading_label)
        centering_layout.addStretch()

        self.main.addLayout(centering_layout, 0, 0)

    # LAN server UI
    def set_lan_server_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # don't kill open server
        self.LAN_server.keep_alive()

        # open a new server if no already running
        if not self.LAN_server.is_running():
            self.LAN_server.start_server_threaded()

        # wait for server to run
        while not self.LAN_server.is_running():
            pass

        # widgets
        text = "Your IP address is: "
        address = self.LAN_server.get_IP()
        label = qtw.QLabel(text + address)
        label.setObjectName("server-text")

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addStretch()
        lanLayout.addWidget(label)
        lanLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(lanLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    # LAN client UI
    def set_lan_client_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # widgets
        title = qtw.QLabel(text="Server selection:")
        title.setObjectName("lan-title")

        # get list of devices
        devices = net.get_devices()
        ip = []
        for d in devices:
            ip_addr = d["ip"]
            name = d["name"]
            entry = ip_addr + "\t" + name
            ip.append(entry)

        # display devices in list widget
        lst = qtw.QListWidget()
        lst.addItems(ip)
        lst.setCurrentRow(0)
        self.serverLst = lst

        manual_btn = qtw.QPushButton(text="manually input IP")
        manual_btn.setObjectName("manualButton")
        manual_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        manual_btn.clicked.connect(self.set_lan_client_manual_input_section)

        connect_btn = qtw.QPushButton(text="connect")
        connect_btn.setObjectName("bacButton")
        connect_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        connect_btn.clicked.connect(self.connect)

        btns = qtw.QVBoxLayout()
        btns.addWidget(manual_btn)
        btns.addWidget(connect_btn)

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addWidget(title)
        lanLayout.addWidget(lst)
        lanLayout.addLayout(btns)

        self.main.addLayout(lanLayout, 0, 0)

    # LAN client UI for manually entering an IP address
    def set_lan_client_manual_input_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        label = qtw.QLabel("Enter partner's IP address:")
        label.setObjectName("client-text")

        input = qtw.QLineEdit()
        input.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        regex = qtc.QRegExp("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        input.setValidator(qtg.QRegExpValidator(regex))
        input.setAlignment(qtc.Qt.AlignCenter)
        self.IP_input = input

        btn = qtw.QPushButton("connect")
        btn.setObjectName("bacButton")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(self.connect_manually)

        btn2 = qtw.QPushButton("back")
        btn2.setObjectName("manualButton2")
        btn2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn2.clicked.connect(self.set_lan_client_section)

        layout = qtw.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(btn2)
        layout.addWidget(btn)
        layout.addStretch()

        horizontal = qtw.QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(layout)
        horizontal.addStretch()

        self.main.addLayout(horizontal, 0, 0)

    # bluetooth server UI
    def set_blue_server_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # bluetooth sockets do not work on macOS
        on_macOS = self.BT_server.on_macOS()

        # keep server alive if open
        self.BT_server.keep_alive()

        if not on_macOS:
            if not self.BT_server.is_running():
                # not on mac -> open socket
                self.BT_server.start_server_threaded()

            # wait for server to run
            while not self.BT_server.is_running():
                pass

        # not displayed on macOS
        text = "Your MAC-address is: "
        address = self.BT_server.get_mac_address()

        # check if bluetooth possible
        if address is None:
            self.set_info_screen("Bluetooth not available.", "back", self.set_downloading_section)
            return

        label = qtw.QLabel(text + address)
        label.setObjectName("server-text")

        # only displayed on macOS
        text2 = "MacOS bluetooth transfer is not supported."
        label2 = qtw.QLabel(text2)
        label2.setObjectName("server-text")

        BTLayout = qtw.QVBoxLayout()
        BTLayout.addStretch()
        if not on_macOS:
            BTLayout.addWidget(label)
        else:
            BTLayout.addWidget(label2)
        BTLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(BTLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    # bluetooth client UI
    def set_blue_client_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        label = qtw.QLabel("Enter partner's MAC-address:")
        label.setObjectName("client-text")

        input = qtw.QLineEdit()
        input.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        # only allow input of valid MAC addresses
        regex = qtc.QRegExp("^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$")
        input.setValidator(qtg.QRegExpValidator(regex))
        input.setAlignment(qtc.Qt.AlignCenter)
        self.MAC_input = input

        btn = qtw.QPushButton("connect")
        btn.setObjectName("bt-client-btn")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(self.connect_BT)

        layout = qtw.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(btn)
        layout.addStretch()

        horizontal = qtw.QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(layout)
        horizontal.addStretch()

        self.main.addLayout(horizontal, 0, 0)

    # archive section of app
    def set_archiving_section(self):
        # clear main layout
        self.tab_changed()
        self.set_selected_menu_button(self.b3)

        # article reader
        text = qtw.QTextBrowser()
        style.setArticleStyle(text)
        text.setOpenExternalLinks(True)
        self.archive_reader = text

        # article selector
        selector = qtw.QListWidget()
        self.selector = selector
        selector.setWordWrap(True)
        # only bookmarked articles
        entries = self.get_bookmarked_article_lst()
        selector.addItems(entries)
        selector.itemSelectionChanged.connect(self.archive_article_changed)
        selector.setCurrentRow(0)
        text.moveCursor(qtg.QTextCursor.Start)

        # bookmark btn
        if self.light:
            color = "black"
        else:
            color = "#f7f7f7"

        mdi_book = qta.icon("mdi.bookmark-outline", color=color)
        mdi_book_btn = qtw.QPushButton()
        mdi_book_btn.setObjectName("bookmark-btn")
        mdi_book_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        mdi_book_btn.clicked.connect(self.update_bookmark)
        mdi_book_btn.setIconSize(qtc.QSize(40, 40))
        mdi_book_btn.setIcon(mdi_book)
        mdi_book_btn.setToolTip("archive article")
        self.mdi_btn = mdi_book_btn
        self.draw_bookmark()

        # for opening articles in own windows
        mdi_external = qta.icon("mdi.open-in-new", color=color)
        external_btn = qtw.QPushButton()
        external_btn.setObjectName("bookmark-btn")
        external_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        external_btn.clicked.connect(self.open_external)
        external_btn.setIconSize(qtc.QSize(35, 35))
        external_btn.setIcon(mdi_external)
        external_btn.setToolTip("open in new window")
        self.external_btn = external_btn

        # for sharing on bac net
        mdi_bac = qta.icon("mdi.folder-key-network", color=color)
        bac_btn = qtw.QPushButton()
        bac_btn.setObjectName("bookmark-btn")
        bac_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        bac_btn.clicked.connect(self.handle_bac_net)
        bac_btn.setIconSize(qtc.QSize(35, 35))
        bac_btn.setIcon(mdi_bac)
        bac_btn.setToolTip("add to BAC-net")
        self.bac_btn = bac_btn

        rhs_layout = qtw.QVBoxLayout()
        rhs_layout.addWidget(mdi_book_btn)
        rhs_layout.addWidget(bac_btn)
        rhs_layout.addWidget(external_btn)
        rhs_layout.addStretch()

        self.main.addWidget(selector, 0, 0, 100, 20)
        self.main.addWidget(text, 0, 20, 100, 75)
        self.main.addLayout(rhs_layout, 0, 95, 100, 5)

    # BAC-net feed reader and creator
    def set_BAC_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b5)

        # check if a user account is already present
        if self.bac_core.exists_db() == 0:
            self.set_login_section()
            return

        # if exists, go through setup
        self.bac_core.setup_db()
        articles, titles, feeds = self.get_bac_feeds()

        # create UI elements
        article_lst = qtw.QListWidget()
        article_lst.setWordWrap(True)
        article_lst.itemSelectionChanged.connect(self.bac_article_selection_changed)
        self.bac_article_lst = article_lst

        bac_selector = qtw.QComboBox()
        bac_selector.setObjectName("combo")
        bac_selector.setToolTip("select feed")
        bac_selector.addItems(feeds)
        bac_selector.setCurrentIndex(0)
        bac_selector.currentTextChanged.connect(self.update_bac_article_lst)
        bac_selector.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.bac_selector = bac_selector

        btn = qtw.QPushButton("Create new feed")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.setObjectName("bacButton")
        btn.clicked.connect(self.set_create_feed_section)

        lhs_layout = qtw.QVBoxLayout()
        lhs_layout.addWidget(bac_selector)
        lhs_layout.addWidget(article_lst)
        lhs_layout.addWidget(btn)

        text = qtw.QTextBrowser()
        style.setArticleStyle(text)
        text.setOpenExternalLinks(True)
        self.bac_reader = text

        # update content
        self.update_bac_article_lst()

        self.main.addLayout(lhs_layout, 0, 0, 10, 2)
        self.main.addWidget(text, 0, 2, 10, 8)

    # used for creating BAC-net username
    def set_login_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b5)

        text = qtw.QLabel("Enter a username:")
        text.setObjectName("client-text")

        login = qtw.QLineEdit()
        login.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        login.setAlignment(qtc.Qt.AlignCenter)
        self.login = login

        btn = qtw.QPushButton("continue")
        btn.setObjectName("loginBtn")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(self.bac_login)

        layout = qtw.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(text)
        layout.addWidget(login)
        layout.addWidget(btn)
        layout.addStretch()

        horizontal = qtw.QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(layout)
        horizontal.addStretch()

        self.main.addLayout(horizontal, 0, 0)

    # customizable info screen
    # msg = big text message
    # btn_name = text on btn beneath info
    # btn_fct = button onclick function
    def set_info_screen(self, msg, btn_name, btn_fct):
        self.tab_changed()

        label = qtw.QLabel(msg)
        label.setObjectName("server-text")

        btn = qtw.QPushButton(text=btn_name)
        btn.setObjectName("bacButton")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(btn_fct)

        vertical = qtw.QVBoxLayout()
        vertical.addStretch()
        vertical.addWidget(label)
        vertical.addWidget(btn)
        vertical.addStretch()

        horizontal = qtw.QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(vertical)
        horizontal.addStretch()

        self.main.addLayout(horizontal, 0, 0)

    # used for creating new BAC-net feed
    def set_create_feed_section(self):
        self.tab_changed()

        title = qtw.QLabel("Enter a feed name:")
        title.setObjectName("client-text")

        input = qtw.QLineEdit()
        input.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        input.setAlignment(qtc.Qt.AlignCenter)
        self.feed_input = input

        btn = qtw.QPushButton("create")
        btn.setObjectName("bacButton")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(self.create_feed)

        layout = qtw.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(input)
        layout.addWidget(btn)
        layout.addStretch()

        h_layout = qtw.QHBoxLayout()
        h_layout.addStretch()
        h_layout.addLayout(layout)
        h_layout.addStretch()

        self.main.addLayout(h_layout, 0, 0)

    # used for updating the article list in the BAC-net section after a feed has been chosen
    def update_bac_article_lst(self):
        if self.bac_selector is None or self.bac_selector.currentText() is None:
            self.set_info_screen("No feed was selected.", "back", self.set_BAC_section)
            return

        # get current feed name
        # format: "feedname" by username
        # extract feedname and username:
        text = self.bac_selector.currentText()
        split = text.split("\"")

        if len(split) < 3:
            return

        feed = split[1]
        name = split[2].split("by ")[1]

        # get json list for corresponding feed
        json_lst = self.bac_core.get_json_files_from_feed((feed, name))

        # create articles from json files
        articles = []
        for json in json_lst:
            article = Article("SRF")
            article.fill_article_from_json_string(json)
            articles.append(article)

        self.bac_articles = articles

        # extract titles and display in UI
        titles = [x.title_1 for x in articles]
        self.bac_article_lst.clear()
        self.bac_article_lst.addItems(titles)
        self.bac_article_lst.setCurrentRow(0)
        self.bac_reader.moveCursor(qtg.QTextCursor.Start)

    # returns a 3-tuple of all articles, article titles and feed names
    def get_bac_feeds(self):
        tuples = self.bac_core.get_all_feed_name_host_tuples()
        feeds = []
        json = []
        for tuple in tuples:
            # format string for returning later
            # format: "feedname" by username
            feeds.append("\"" + tuple[0] + "\"" + " by " + tuple[1])
            list = self.bac_core.get_json_files_from_feed(tuple)
            for item in list:
                json.append(item)

        # create articles from json files
        articles = []
        for item in json:
            article = Article("SRF")
            article.fill_article_from_json_string(item)
            articles.append(article)

        # extract titles
        titles = []
        for item in articles:
            titles.append(item.title_1)

        # reverse so most recently appended article on top of list
        titles.reverse()

        return (articles, titles, feeds)

    # creates a new feed with help of input name from self.set_create_feed_section()
    def create_feed(self):
        # get text
        name = self.feed_input.text()

        if len(name) > 0:
            # check if name already exists
            names = self.bac_core.get_feednames_from_host()
            if name in names:
                self.set_info_screen("Feedname already exists.", "back", self.set_create_feed_section)
                return

            self.bac_core.create_feed(name)
            self.set_BAC_section()
        else:
            # if input is empty
            self.set_info_screen("Invalid feed name.", "back", self.set_create_feed_section)

    # creates a new user
    def bac_login(self):
        # get input username from self.set_login_section()
        name = self.login.text()

        if len(name) > 0:
            self.bac_core.setup_db(name)
            self.set_BAC_section()
        else:
            # empty name not accepted
            self.set_info_screen("Invalid name.", "back", self.set_login_section)

    # used in bac-net section
    # update article in reader according to selected article
    def bac_article_selection_changed(self):
        # get currently selected article
        current = self.bac_article_lst.currentItem().text()

        # find article instance with corresponding title
        target_article = None
        for article in self.bac_articles:
            if article.title_1 == current:
                target_article = article

        if target_article is None:
            #print("article not found")
            return

        # set article to reader
        html = target_article.get_html()
        self.bac_reader.clear()
        self.bac_reader.insertHtml(html)

    # if selected article in article selector changes
    # used in reading section
    def selected_article_changed(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()

        # remove "new article" indication
        if selectedArticle.startswith("\u2022"):
            unmarked = selectedArticle[2:]
            self.selector.currentItem().setText(unmarked)

        # set article to reader
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.article.clear()
        self.article.insertHtml(html)

        # check article bookmark status
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

        #mark as read
        self.logic.mark_as_opened(selectedArticle)
        self.current_title = selectedArticle

    # if selected article in article selector changes
    # used in archive section
    def archive_article_changed(self):
        # get new article title
        selectedArticle = self.selector.currentItem().text()
        self.current_title = selectedArticle

        # get html of article and set it to reader
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.archive_reader.clear()
        self.archive_reader.insertHtml(html)

        # check bookmark status
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

    # used for switching between dark/light mode
    def switch(self):
        # switch from dark to light or vice versa
        if self.light:
            self.switch.setText("light")
            css = style.getDarkStyleSheet()
        else:
            self.switch.setText("dark")
            css = style.getLightStyleSheet()

        self.setStyleSheet(css)
        self.light = not self.light

        # update colors of menu bar
        self.set_selected_menu_button(self.selected)

        # update external link icon
        if self.light:
            icon = qta.icon("mdi.open-in-new", color="black")
        else:
            icon = qta.icon("mdi.open-in-new", color="#f7f7f7")

        if self.light:
            icon2 = qta.icon("mdi.folder-key-network", color="black")
        else:
            icon2 = qta.icon("mdi.folder-key-network", color="#f7f7f7")

        self.external_btn.setIcon(icon)
        self.bac_btn.setIcon(icon2)

        # update external windows
        for window in self.open_windows:
            if window.isVisible():
                window.switch(self.light)
            else:
                # remove windows from list if no longer open
                self.open_windows.remove(window)

        # if currently in downloading screen, get new gif
        if self.selected == self.b2 and self.logic.is_updating:
            self.set_loading_screen_section()

        if self.selected == self.b2 and self.lan_is_downloading:
            self.set_loading_screen_section()

        if self.selected == self.b2 and self.BT_is_downloading:
            self.set_loading_screen_section()

        # update bookmark color
        self.draw_bookmark()
        # update filter color
        self.update_switches()

    # set the currently selected button and set correct color
    def set_selected_menu_button(self, button):
        self.selected = button
        buttons = [self.b1, self.b2, self.b3, self.b4, self.b5]
        for b in buttons:
            if (self.light):
                b.setStyleSheet("color: black;")
            else:
                b.setStyleSheet("color: white")

        button.setStyleSheet("color: grey;")

    # switch between downloading/sharing mode in downloading section
    def toggle_download(self):
        # switch toggles
        if self.toggle.isChecked():
            self.toggle.setObjectName("toggleTrue")
            self.toggle2.setChecked(False)
            self.toggle2.setObjectName("toggleFalse")

            # set correct style
            if self.light:
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: black;")
            else:
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: #f7f7f7;")
        else:
            # if already activated toggle was selected, reactivate
            self.toggle.setChecked(True)

        # refresh section
        self.set_downloading_section()

    # switch between downloading/sharing mode in downloading section
    def toggle2_download(self):
        # switch toggles
        if self.toggle2.isChecked():
            self.toggle2.setObjectName("toggleTrue")
            self.toggle.setChecked(False)
            self.toggle.setObjectName("toggleFalse")

            # set correct style
            if self.light:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: black;")
            else:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: #f7f7f7;")
        else:
            # reactivate if already active toggle selected
            self.toggle2.setChecked(True)

        # remove srf button in sharing mode
        if not self.srfBtn == None:
            self.downLayout.removeWidget(self.srfBtn)
            self.srfBtn = None

    # activated if srf button is clicked
    # download new articles
    def handle_download(self):
        # set loading screen
        self.set_loading_screen_section()
        # create and start downloadingThread
        self.downloading_thread = downloadingThread(self.logic)
        self.downloading_thread.start()
        # switch to reading section when finished downloading
        self.downloading_thread.finished.connect(self.srf_download_finished)

    # activated after scraping is finished
    # not possible to directly insert above
    def srf_download_finished(self):
        self.set_info_screen("Download successful.", "read", self.set_reading_section)

    # if a user wants to add an article to a bac net feed
    # present pop up window and let user choose feed
    def handle_bac_net(self):
        if self.selector.currentItem() is None:
            if self.selected == self.b1:
                self.set_info_screen("Please select an article first.", "back", self.set_reading_section)
            else:
                self.set_info_screen("Please select an article first.", "back", self.set_archiving_section)
            return

        # check if bac net is set up, if not let user log in
        if self.bac_core.exists_db() == 0:
            self.set_login_section()
            return

        # set up database, necessary for appending to feed
        self.bac_core.setup_db()

        # if user has not created any feeds
        if len(self.bac_core.get_feednames_from_host()) == 0:
            self.set_info_screen("Please create a feed first.", "create feed", self.set_create_feed_section)
            return

        # get current article
        title = self.selector.currentItem().text()
        article = self.logic.get_article_from_title(title)

        # present pop up
        dialog = bacPopUp(self.bac_core, article.get_json())
        dialog.exec_()

    # imports .pcap files into bac net section of app
    def bac_import(self):
        # check if bac net is set up
        if self.bac_core.exists_db() == 0:
            self.set_BAC_section()
            return

        self.bac_core.setup_db()

        # let user choose directory
        path = str(qtw.QFileDialog.getExistingDirectory(self, "Import"))

        # give path to bac core
        # self.bac_core.import_from_pcap_to_db(path)
        self.set_loading_screen_section()
        self.lan_is_downloading = True

        self.bac_import_thread = BACImportThread(self.bac_core, path)
        self.bac_import_thread.finished.connect(self.finished_bac_import)
        self.bac_import_thread.start()

    # resets loading screen after bac import finished
    def finished_bac_import(self):
        self.lan_is_downloading = False
        self.set_info_screen("Successfully imported feeds.", "BAC-section", self.set_BAC_section)

    # exports .pcap files
    def bac_export(self):
        # check if bac net was set up
        if self.bac_core.exists_db() == 0:
            self.set_BAC_section()
            return

        self.bac_core.setup_db()

        # choose directory
        path = str(qtw.QFileDialog.getExistingDirectory(self, "Export"))

        # give to bac core
        # self.bac_core.export_db_to_pcap(path)
        self.set_loading_screen_section()
        self.lan_is_downloading = True

        self.bac_export_thread = BACExportThread(self.bac_core, path)
        self.bac_export_thread.finished.connect(self.finished_bac_export)
        self.bac_export_thread.start()

    # resets loading screen after bac export finished
    def finished_bac_export(self):
        self.lan_is_downloading = False
        self.set_info_screen("Successfully exported feeds.", "back", self.set_downloading_section)

    # check current mode downloading/sharing and select corresponding action
    def switch_wlan(self):
        if self.toggle.isChecked():
            self.set_lan_client_section()
        else:
            self.set_lan_server_section()

    # check current mode downloading/sharing and select corresponding action
    def switch_blue(self):
        if self.toggle.isChecked():
            self.set_blue_client_section()
        else:
            self.set_blue_server_section()

    # in downloading section, open correct bac net response (import or export)
    def switch_bac(self):
        if self.toggle.isChecked():
            self.bac_import()
        else:
            self.bac_export()

    # used in LAN client UI
    # connect to selected IP address
    def connect(self):
        ip = self.serverLst.currentItem().text()
        ip = ip.split("\t")[0]
        #print("trying to connect to " + ip)
        self.set_loading_screen_section()
        self.lan_thread = LANThread(self.LAN_client, ip, self.download_status)
        self.lan_thread.start()
        self.lan_is_downloading = True
        self.lan_thread.finished.connect(self.finished_lan_download)

    # used if user wants to manually input an IP address for LAN connection
    def connect_manually(self):
        # get input
        ip = self.IP_input.text()
        # check validity
        if len(ip) >= 7 and len(ip) <= 15:
            #print("trying to connect to " + ip)
            self.set_loading_screen_section()
            self.lan_thread = LANThread(self.LAN_client, ip, self.download_status)
            self.lan_thread.start()
            self.lan_is_downloading = True
            self.lan_thread.finished.connect(self.finished_lan_download)
        else:
            self.set_info_screen("Invalid IP address.", "back", self.set_lan_client_manual_input_section)

    # used for reading user input
    # retrieves entered MAC address and hands it to Bluetooth client
    def connect_BT(self):
        mac = self.MAC_input.text()
        if len(mac) == 17:
            # valid address
            self.set_loading_screen_section()
            self.BT_thread = BTThread(self.BT_client, mac)
            self.BT_thread.start()
            self.BT_is_downloading = True
            self.BT_thread.finished.connect(self.finished_BT_download)
        else:
            # invalid address
            self.set_info_screen("Invalid MAC address.", "back", self.set_blue_client_section)

    # used after lan download finishes, turns off loading screen
    def finished_lan_download(self):
        self.lan_is_downloading = False
        bool = self.download_status.get()
        self.download_status.empty()
        if bool == True:
            self.set_info_screen("Download failed.", "back", self.set_downloading_section)
        else:
            self.set_info_screen("Download successful.", "read", self.set_reading_section)

    # used after Bluetooth download finishes, turns off loading screen
    def finished_BT_download(self):
        self.BT_is_downloading = False
        self.set_reading_section()

    # switch active article filter to "today"
    def switch_today(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.today_btn
        self.today_btn.setStyleSheet("color: grey; height: 20%;")
        self.today_btn.setObjectName("filter-btn-active")

        # update article selection according to filter
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # switch active article filter to "week"
    def switch_week(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.week_btn
        self.week_btn.setStyleSheet("color: grey; height: 20%;")
        self.week_btn.setObjectName("filter-btn-active")

        # update article list
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # switch active article filter to "all"
    def switch_all(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.all_btn
        self.all_btn.setStyleSheet("color: grey; height: 20%;")
        self.all_btn.setObjectName("filter-btn-active")

        # update entries in article selector
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # update stylesheet of main window according to mode
    def update_style(self):
        if self.light:
            self.setStyleSheet(style.getLightStyleSheet())
        else:
            self.setStyleSheet(style.getDarkStyleSheet())

    # get article list according to active filter
    def get_article_lst(self):
        if self.active_article_filter == self.today_btn:
            return self.logic.get_article_titles_today()
        if self.active_article_filter == self.week_btn:
            return self.logic.get_article_titles_week()
        else:
            return self.logic.get_article_titles()

    # get list of all bookmarked articles
    def get_bookmarked_article_lst(self):
        lst = self.logic.get_bookmarked_article_titles()
        return lst

    # get list of all articles and set it to selector
    # not paying attention to filter
    def update_article_list(self):
        entries = self.get_article_lst()
        self.selector.clear()
        self.selector.addItems(entries)

    # updates the bookmark icon after clicking on it
    # also communicates with back-end to update article bookmark in json files
    def update_bookmark(self):
        # get title without reading indication
        title = utils.remove_dot(self.current_title)
        if title == None:
            # nothing to bookmark
            return

        # check if article is bookmarked
        active = self.logic.is_article_bookmarked(title)
        # send bookmark info to back-end and update icon
        if active:
            self.logic.remove_bookmark_article(title)
            self.draw_mdi_outline()
        else:
            self.logic.bookmark_article(title)
            self.fill_mdi()

        # if in archive section: update selector
        if self.selected == self.b3:
            entries = self.get_bookmarked_article_lst()
            self.selector.clear()
            self.selector.addItems(entries)

    # draws the appropriate bookmark icon, considering bookmark status
    def draw_bookmark(self):
        if self.selector.currentItem() == None:
            # nothing to bookmark
            return

        # get current title and check if active
        title = self.selector.currentItem().text()
        active = self.logic.is_article_bookmarked(title)

        if active:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

    # draws empty bookmark -> not bookmarked, considers dark/light mode
    def draw_mdi_outline(self):
        if self.mdi_btn == None:
            # nothing to bookmark
            return

        if self.light:
            icon = qta.icon("mdi.bookmark-outline", color="black")
        else:
            icon = qta.icon("mdi.bookmark-outline", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    # draws full bookmark -> bookmarked, considers dark/light mode
    def fill_mdi(self):
        if self.mdi_btn == None:
            # nothing to bookmark
            return

        if self.light:
            icon = qta.icon("mdi.bookmark", color="black")
        else:
            icon = qta.icon("mdi.bookmark", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    # on category filter change
    # get correct articles and display them in selector
    def filter_selection_changed(self, category):
        if category == None:
            # if not given, get active filter from combo box
            category = str(self.combo.currentText())

        # get artcile list, considering time filter (today, week, all)
        titles = self.get_article_lst()

        # apply category filter to list
        if category == "All Categories":
            self.update_article_list()
            return
        elif category == "Switzerland":
            new_lst = self.logic.filter_by_category(titles, Category.SWITZERLAND)
        elif category == "International":
            new_lst = self.logic.filter_by_category(titles, Category.INTERNATIONAL)
        elif category == "Economics":
            new_lst = self.logic.filter_by_category(titles, Category.ECONOMICS)
        elif category == "Culture":
            new_lst = self.logic.filter_by_category(titles, Category.CULTURE)
        elif category == "Sports":
            new_lst = self.logic.filter_by_category(titles, Category.SPORTS)
        elif category == "Meteo":
            new_lst = self.logic.filter_by_category(titles, Category.METEO)
        elif category == "Panorama":
            new_lst = self.logic.filter_by_category(titles, Category.PANORAMA)

        self.selector.clear()
        self.selector.addItems(new_lst)

    # update style of time filter switches considering dark/light mode and active switch
    def update_switches(self):
        if self.light:
            if self.active_article_filter == self.today_btn:
                self.today_btn.setStyleSheet("color: grey; height: 20%;")
                self.week_btn.setStyleSheet("color: black; height: 20%;")
                self.all_btn.setStyleSheet("color: black; height: 20%;")
            if self.active_article_filter == self.week_btn:
                self.today_btn.setStyleSheet("color: black; height: 20%;")
                self.week_btn.setStyleSheet("color: grey; height: 20%;")
                self.all_btn.setStyleSheet("color: black; height: 20%;")
            if self.active_article_filter == self.all_btn:
                self.today_btn.setStyleSheet("color: black; height: 20%;")
                self.week_btn.setStyleSheet("color: black; height: 20%;")
                self.all_btn.setStyleSheet("color: grey; height: 20%;")
        else:
            if self.active_article_filter == self.today_btn:
                self.today_btn.setStyleSheet("color: grey; height: 20%;")
                self.week_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.all_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
            if self.active_article_filter == self.week_btn:
                self.today_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.week_btn.setStyleSheet("color: grey; height: 20%;")
                self.all_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
            if self.active_article_filter == self.all_btn:
                self.today_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.week_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.all_btn.setStyleSheet("color: grey; height: 20%;")

    # reset window on section change
    def tab_changed(self):
        # clear window
        utils.remove_widgets(self.main)
        # stop active servers
        self.LAN_server.stop_server()
        self.BT_server.stop_server()

    # opens the currently selected article in a new window
    def open_external(self):
        # in reading section
        if self.selected == self.b1:
            if self.selector.currentItem() is None:
                return
            title = self.selector.currentItem().text()
            title = utils.remove_dot(title)
        # archive section
        elif self.selected == self.b3:
            if self.selector.currentItem() is None:
                return
            else:
                title = self.selector.currentItem().text()
                title = utils.remove_dot(title)
        else:
            return

        # retrieve html from title
        html = self.logic.get_article_html_by_title1(title)
        external_window = externalWindow(title, html, self.window().width(), self.window().height(), self.light)
        external_window.show()

        self.open_windows.append(external_window)
