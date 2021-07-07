from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QScrollArea
)
from PyQt5.QtCore import Qt

from BackEnd import actions as act




class RequestTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Setup Layout
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.request_list = QListWidget()
        self.listElements = []
        self.updateRequests()
        self.vbox.addWidget(self.request_list)

        return

    def updateRequests(self):
        # TODO actually get all requests and create list with them
        for i in range(2):
            customRequestListItem = RequestListItem()
            myQListWidgetItem = QListWidgetItem(self.request_list)
            myQListWidgetItem.setSizeHint(customRequestListItem.sizeHint())
            self.request_list.addItem(myQListWidgetItem)
            self.request_list.setItemWidget(myQListWidgetItem, customRequestListItem)
            self.listElements.append(customRequestListItem)
        return

class RequestListItem(QWidget):
    def __init__(self, parent=None):
        super(RequestListItem, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Setup Layout
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.requesterLabel = QLabel()
        self.requesterLabel.setText('fc553b9c8c538019ac6de37e793286ec')
        self.hbox.addWidget(self.requesterLabel)

        self.validLabel = QLabel()
        self.validLabel.setText("verified")
        self.hbox.addWidget(self.validLabel)

        self.approveButton = QPushButton("send shard")
        self.approveButton.clicked.connect(self.sendShard)
        self.hbox.addWidget(self.approveButton)

        return

    def sendShard(self):
        # TODO actually write new event to feed to the right person
        print(f"sent shard to {self.requesterLabel.text()}!")
        return


class ShareTab(QWidget):
    def __init__(self, parent=None):
        super(ShareTab, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.pubInputs = []

        # Section for Secret to be shared input
        self.keyInfoLabel = QLabel("Private Key you want to share:")
        self.vbox.addWidget(self.keyInfoLabel)
        self.keyInput = QLineEdit()
        self.vbox.addWidget(self.keyInput)

        self.passInput = QLineEdit()
        self.passInput.setPlaceholderText("password")
        self.vbox.addWidget(self.passInput)

        # Setup ComboBox to set the number of Shards to be created
        self.numShardsLabel = QLabel("Number of Shards:")
        self.vbox.addWidget(self.numShardsLabel)
        self.numShardsInput = QComboBox()
        for i in range(1, 20):
            self.numShardsInput.addItem(str(i))
        self.numShardsInput.currentTextChanged.connect(self.updateWidgets)
        self.vbox.addWidget(self.numShardsInput)

        # Setup ComboBox to specify the number of shards required for recovery
        self.numShardsRecLabel = QLabel("Number of Shards required for recovery:")
        self.vbox.addWidget(self.numShardsRecLabel)
        self.numShardsRecInput = QComboBox()
        for i in range(1, 10):
            self.numShardsRecInput.addItem(str(i))
        self.vbox.addWidget(self.numShardsRecInput)

        # Label before pub key input section
        self.friendKeyInfoLabel = QLabel("Public Keys of friends you want to share the shards with:")
        self.vbox.addWidget(self.friendKeyInfoLabel)

        # Scroll Area for pub key input fields
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scroll.setWidget(self.scrollContent)
        self.vbox.addWidget(self.scroll)

        self.sharButton = QPushButton("share")
        self.sharButton.clicked.connect(self.shareSecret)
        self.vbox.addWidget(self.sharButton)
        self.updateWidgets(self.numShardsInput.currentText())
        return

    def updateWidgets(self, newValue):
        self.updatenumShardsRec(int(newValue))
        self.updateInputField(int(newValue))

    def updatenumShardsRec(self, newValue):
        self.numShardsRecInput.clear()
        for i in range (1, newValue+1):
            self.numShardsRecInput.addItem(str(i))

    def updateInputField(self, newValue):
        for j in range(len(self.pubInputs), 0, -1):
            self.scrollLayout.removeWidget(self.pubInputs.pop())
        for i in range(int(self.numShardsInput.currentText())):
            pubInput = QLineEdit()
            self.pubInputs.append(pubInput)
            self.scrollLayout.addWidget(pubInput)
            self.scroll.resize(self.scroll.size())

    def shareSecret(self):
        # TODO actually write events in feed
        act.append_test_message()
        act.rq_handler.next()
        print(f"shared secret: {self.keyInput.text()}")
        print("shard receivers: ")
        for i in range(len(self.pubInputs)):
            print(f"pubKey: {self.pubInputs[i].text()}")
        print(f"Shares required for recovery: {self.numShardsRecInput.currentText()}")

        return


# RecoveryTab, Interface to recover secrets
class RecoveryTab(QWidget):
    def __init__(self, parent=None):
        super(RecoveryTab, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Setup Layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Add automatic recovery part
        self.autoLabel = QLabel()
        self.autoLabel.setText("Automatic recovery")
        self.vbox.addWidget(self.autoLabel)
        self.autoRecovery = AutoRecovery(self)
        self.vbox.addWidget(self.autoRecovery)

        # Add manual recovery part
        self.manualLabel = QLabel()
        self.manualLabel.setText("Manual recovery")
        self.vbox.addWidget(self.manualLabel)
        self.manualRecovery = ManualRecovery(self)
        self.vbox.addWidget(self.manualRecovery)
        self.recButton = QPushButton("Recover")
        self.recButton.clicked.connect(self.handleManualRecovery)
        self.vbox.addWidget(self.recButton)

    def handleManualRecovery(self):
        act.rq_handler.next()
        # TODO Initiate manual recovery (writing in feeds etc)
        return


# AutomaticRecovery Widget of the Recovery Tab
class AutoRecovery(QWidget):
    def __init__(self, parent=None):
        super(AutoRecovery, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Setup Layout
        self.hbox = QHBoxLayout(self)
        self.setLayout(self.hbox)

        # ComboBox containing names of shared secrets
        self.keyNameSelection = QComboBox()
        self.updateComboBox() #doesn't do anythin at the moment
        # for now just add 2 items
        self.keyNameSelection.addItem("name of key 1")
        self.keyNameSelection.addItem("name of key 2")
        self.hbox.addWidget(self.keyNameSelection)
        # Add an Input field to enter password of secret to be recovered
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("password")
        self.hbox.addWidget(self.passwordInput)
        # Add Button to initiate recovery
        self.recoverButton = QPushButton("Recover")
        self.recoverButton.clicked.connect(self.startAutoRecovery)
        self.hbox.addWidget(self.recoverButton)

        return

    def updateComboBox(self):
        # TODO get names of shared secrets and update Combobox
        return

    def startAutoRecovery(self):
        # TODO initiate recovery
        return


# ManualRecovery Widget of the Recovery Tab
class ManualRecovery(QWidget):
    def __init__(self, parent=None):
        super(ManualRecovery, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Setup Layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Input field for Name of Secret to be recovered
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Name of Key Share")
        self.vbox.addWidget(self.nameInput)
        # Input field for the password of Secret to be recovered
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Password")
        self.vbox.addWidget(self.passwordInput)

        # create ScrollArea for friends public key input
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)

        # Setup Content Widget and Layout for the Scroll Area
        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollContent.setLayout(self.scrollLayout)

        # Setup Widget containing Label and + and - Button
        self.lbl_butn_widget = QWidget()
        self.lbl_butn_widget.setLayout(QHBoxLayout())
        self.listLabel = QLabel()
        self.listLabel.setText("Enter public Keys of Friends:")
        self.lbl_butn_widget.layout().addWidget(self.listLabel)
        self.removeInputBtn = QPushButton("-")
        self.removeInputBtn.setMaximumWidth(25)
        self.removeInputBtn.clicked.connect(self.removeInputField)
        self.lbl_butn_widget.layout().addWidget(self.removeInputBtn)
        self.addInputBtn = QPushButton("+")
        self.addInputBtn.setMaximumWidth(25)
        self.addInputBtn.clicked.connect(self.addInputField)
        self.lbl_butn_widget.layout().addWidget(self.addInputBtn)
        self.vbox.addWidget(self.lbl_butn_widget)

        # List holding reference to all the input field of pub keys
        self.pubInputs = []
        # Add 1 Input field to start off
        self.addInputField()
        # Add widget to main Layout
        self.scroll.setWidget(self.scrollContent)
        self.vbox.addWidget(self.scroll)
        return

    def addInputField(self):
        pubInput = QLineEdit()
        self.pubInputs.append(pubInput)
        self.scrollLayout.addWidget(pubInput)
        return

    def removeInputField(self):
        if len(self.pubInputs) > 1:
            self.scrollLayout.removeWidget(self.pubInputs.pop())
        return


class PendingTab(QWidget):
    def __init__(self, parent=None):
        super(PendingTab, self).__init__(parent)