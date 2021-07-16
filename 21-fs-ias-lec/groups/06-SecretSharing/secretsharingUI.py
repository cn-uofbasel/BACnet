import sys

from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QScrollArea,
    QPushButton,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QLabel
)
from PyQt5.QtCore import Qt, QFile, QIODevice, QTextStream
from FrontEnd.Tabs import ContactTab, ShareTab, RecoveryTab, act, NotificationDialog
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
        self.show()
        return

    def updateContents(self):
        act.handle_new_events(act.rq_handler.event_factory.get_private_key())
        print("updated")

    def configureUpdates(self):
        self.tabs.currentChanged.connect(self.shareTab.updateContacts)
        self.tabs.currentChanged.connect(self.recoveryTab.autoRecovery.updateComboBox)
        self.tabs.currentChanged.connect(self.recoveryTab.manualRecovery.updateContacts)

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super(RegisterDialog, self).__init__(parent)
        registerLayout = QFormLayout()
        self.usernameInput = QLineEdit()
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.secondPasswordInput = QLineEdit()
        self.secondPasswordInput.setEchoMode(QLineEdit.Password)
        registerLayout.addRow("Username", self.usernameInput)
        registerLayout.addRow("Password", self.passwordInput)
        registerLayout.addRow("Passwort repeated", self.secondPasswordInput)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.register)
        self.buttons.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(registerLayout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def register(self):
        try:
            act.create_user(self.usernameInput.text(), self.passwordInput.text(), self.secondPasswordInput.text())
            self.accept()
        except act.PasswordError as pe:
            self.passwordInput.clear()
            self.secondPasswordInput.clear()
            errorDialog = NotificationDialog(pe.message)
            errorDialog.exec_()




class LoginPage(QDialog):
    def __init__(self, parent=None):
        super(LoginPage, self).__init__(parent)
        loginLayout = QFormLayout()
        self.usernameLabel = QLabel()
        self.usernameLabel.setText(act.rq_handler.username)
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        loginLayout.addRow("Username: ", self.usernameLabel)
        loginLayout.addRow("Password: ", self.passwordInput)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.login)
        self.buttons.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(loginLayout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def login(self):
        try:
            act.login(self.passwordInput.text())
            self.accept()
        except act.PasswordError as pe:
            self.passwordInput.clear()
            errorDialog = NotificationDialog(pe.message)
            errorDialog.exec_()






if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Style from: https://github.com/sommerc/pyqt-stylesheets/blob/master/pyqtcss/src/dark_orange/style.qss
    if act.user_exists():
        login = LoginPage()
        if not login.exec_():
            sys.exit(-1)
    else:
        register = RegisterDialog()
        if not register.exec_():
            sys.exit(-1)

    qss = "FrontEnd/styles/style3.qss"
    stream = QFile(qss)
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())
    stream.close()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
