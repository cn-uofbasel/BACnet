import sys
import os


def setup_logging():
    # Todo move to main()
    import logging
    log_formatter = logging.Formatter('%(msecs)dms %(funcName)s %(lineno)d %(message)s')
    log_filename = os.path.join("secret_sharing.log")
    log_filemode = "w"
    log_level = logging.DEBUG

    fh = logging.FileHandler(filename=log_filename, mode=log_filemode)
    fh.setFormatter(log_formatter)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.setLevel(log_level)


from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QScrollArea,
    QPushButton,
)
from PyQt5.QtCore import Qt, QFile, QIODevice, QTextStream
from FrontEnd.Tabs import ContactTab, ShareTab, RecoveryTab, act
from FrontEnd.Dialogs import LoginDialog, RegisterDialog
from FrontEnd.CustomTab import TabBar, TabWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Widget holding all the window contents
        self.widget = QWidget()
        # Layout for self.widget
        self.vbox = QVBoxLayout()
        self.widget.setLayout(self.vbox)
        # Setup different Tabs
        self.tabs = TabWidget(self)
        self.tabs.setTabBar(TabBar())
        self.tabs.setElideMode(Qt.ElideRight)
        self.contactTab = ContactTab(self)
        self.tabs.addTab(self.contactTab, "Contacts")
        self.shareTab = ShareTab(self)
        self.tabs.addTab(self.shareTab, "Share")
        self.recoveryTab = RecoveryTab(self)
        self.tabs.addTab(self.recoveryTab, "Recovery")
        self.configureUpdates()
        # Add the tabs to the Layout of self.widget
        self.vbox.addWidget(self.tabs)
        # Create Update Button, should pull all the information from ?? and update the contents
        self.updateButton = QPushButton("Update")
        # TODO create update function and connect to button
        self.updateButton.clicked.connect(self.updateContents)
        self.vbox.addWidget(self.updateButton)

        # add a scroll area to deal with resizing of the window
        self.scroll = QScrollArea()
        # we can turn off the vertical scrollbar because there is a minimum size
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        # set self.widget in the scroll area
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        # definition of window size and Title
        self.resize(500, 600)
        self.setMinimumHeight(600)
        self.setWindowTitle("Secret Sharing BACnet")
        print(act.core.pwd_encrypt_name(act.master_password,"TheName"))
        print(act.core.pwd_encrypt_name(act.master_password,"TheName"))
        self.show()
        return

    def updateContents(self):
        act.handle_new_events(act.rq_handler.event_factory.get_private_key())
        print("updated")

    def configureUpdates(self):
        self.tabs.currentChanged.connect(self.shareTab.updateContacts)
        self.tabs.currentChanged.connect(self.recoveryTab.autoRecovery.updateComboBox)
        self.tabs.currentChanged.connect(self.recoveryTab.manualRecovery.updateContacts)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style from: https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss
    if act.user_exists():
        login = LoginDialog()
        if not login.exec_():
            sys.exit(-1)
    else:
        register = RegisterDialog()
        if not register.exec_():
            sys.exit(-1)

    setup_logging()  # connect to backend loggers

    qss = "FrontEnd/styles/style3.qss"
    stream = QFile(qss)
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())
    stream.close()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
