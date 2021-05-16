import sys

from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QScrollArea,
    QPushButton,
)
from PyQt5.QtCore import Qt, QFile, QIODevice, QTextStream
from Pages import RequestTab, ShareTab, RecoveryTab, PendingTab
from CustomTab import TabBar, TabWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
        return

    def initUI(self):
        # Widget holding all the window contents
        self.widget = QWidget()
        # Layout for self.widget
        self.vbox = QVBoxLayout()
        self.widget.setLayout(self.vbox)

        # Setup different Tabs
        tabs = TabWidget(self)
        tabs.setTabBar(TabBar())
        tabs.setElideMode(Qt.ElideRight)
        tabs.addTab(RequestTab(self), "Requests")
        tabs.addTab(ShareTab(self), "Share")
        tabs.addTab(RecoveryTab(self), "Recovery")
        tabs.addTab(PendingTab(self), "Pending")

        # Add the tabs to the Layout of self.widget
        self.vbox.addWidget(tabs)

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
        self.resize(600, 600)
        self.setMinimumHeight(600)
        self.setWindowTitle("Secret Sharing BACnet")

        return

    def updateContents(self):
        #TODO actually update content
        print("updated")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style form: https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss


    qss = "styles/style3.qss"
    stream = QFile(qss)
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())
    window = MainWindow()


    window.show()
    sys.exit(app.exec_())
