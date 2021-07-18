import os

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


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super(RegisterDialog, self).__init__(parent)
        self.setWindowTitle("Registration")
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
        self.setWindowTitle("Login")
        loginLayout = QFormLayout()
        self.usernameLabel = QLabel()
        self.usernameLabel.setText(act.core.rq_handler.username)
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



class RecoveredDialog(QDialog):
    def __init__(self, secret: bytes, message: str, secret_name: str, scratch_info=None, parent=None):
        super(RecoveredDialog, self).__init__(parent)
        self.secret = secret
        self.secret_name = secret_name
        self.setWindowTitle("Recovery")
        self.buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.buttons.accepted.connect(self.save_to_file)
        self.buttons.rejected.connect(self.no_save)
        self.layout = QVBoxLayout()
        messageLabel = QLabel(message)
        if scratch_info is not None:
            messageLabel.setText(f"scratch recovery of secret with name {secret_name}")
            scratchLabel = QLabel(scratch_info)
        secretLabel = QLabel(secret.decode(act.ENCODING))
        self.layout.addWidget(messageLabel)
        if scratch_info is not None:
            self.layout.addWidget(scratchLabel)
            self.layout.addSpacing(20)
        self.layout.addWidget(secretLabel)
        saveLabel = QLabel("Save Secret to \"recovered\" directory?")
        self.layout.addWidget(saveLabel)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def save_to_file(self):
        with open(os.path.join(act.settings.RECOVERY_DIR, self.secret_name),'wb+') as fd:
            fd.write(self.secret)
        self.remove_from_sharebuffer()
        self.accept()


    def no_save(self):
        self.remove_from_sharebuffer()
        self.reject()

    def remove_from_sharebuffer(self):
        try:
            act.delete_packages_from_share_buffer(self.secret_name)
        except act.SecretSharingError:
            pass
