from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFormLayout
)

from BackEnd import actions as act

class NotificationDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Notification")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        messageLabel = QLabel(message)
        self.layout.addWidget(messageLabel)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class RecoverDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("RecoverNotification")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.NoButton, QDialogButtonBox.Yes)
        self.buttonBox.accepted.connect(self.save_secret)
        self.buttonBox.rejected(self.reject)
        self.layout = QVBoxLayout()
        messageLabel = QLabel(message)
        self.layout.addLayout(messageLabel)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def save_secret(self):
        #call method in actions to save secret to file
        self.accept()
        return

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




class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
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