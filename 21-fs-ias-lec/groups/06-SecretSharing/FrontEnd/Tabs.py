"""THis is super module"""


# ~~~~~~~~~~~~ Imports  ~~~~~~~~~~~~
# FIrst 3 imports mega nice


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
from PyQt5.QtGui import QFont
from BackEnd import actions as act


# ~~~~~~~~~~~~ Contact Tab  ~~~~~~~~~~~~

class ContactTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup Layout
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        # Saved Contacts box
        self.contactsLabel = QLabel()
        self.contactsLabel.setText("SAVED CONTACTS")
        qFont = QFont()
        qFont.setBold(True)
        self.contactsLabel.setFont(qFont)
        self.contactsLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.contactsLabel)
        self.contactEntryList = QListWidget()
        self.contactEntries = []
        self.loadContactEntries()
        self.vbox.addWidget(self.contactEntryList)

        # possible new contacts
        self.knownFeedsLabel = QLabel()
        self.knownFeedsLabel.setText("KNOWN FEED IDS")
        self.knownFeedsLabel.setFont(qFont)
        self.knownFeedsLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.knownFeedsLabel)

        # contact adding section
        # Qcombobox with feed id, get all feed (get_all_feed_ids - get_feed_ids)

        self.contactAddList = QListWidget()
        self.listElements = []
        self.updatePossibleContacts()
        self.vbox.addWidget(self.contactAddList)

    def loadContactEntries(self):
        self.contactEntryList.clear()
        contact_dict = act.get_all_contact_dict()
        for key in contact_dict:
            feed_id = contact_dict[key]
            contactEntry = ContactEntryWidget(feed_id, key, parent=self)
            myQListWidgetItem = QListWidgetItem(self.contactEntryList)
            myQListWidgetItem.setSizeHint(contactEntry.sizeHint())
            self.contactEntryList.addItem(myQListWidgetItem)
            self.contactEntryList.setItemWidget(myQListWidgetItem, contactEntry)
            self.contactEntries.append(contactEntry)

    def updatePossibleContacts(self):
        #get all feed ids
        contact_feed_ids = act.rq_handler.db_connection.get_all_feed_ids()
        #remove master feed id from list
        contact_feed_ids.remove(act.rq_handler.db_connection.get_host_master_id())
        # remove owned feed ids
        for feed_id in act.rq_handler.event_factory.get_own_feed_ids():
            contact_feed_ids.remove(feed_id)
        # remove ids which are already in contacts
        for username in act.contacts.keys():
            if act.contacts[username] in contact_feed_ids:
                contact_feed_ids.remove(act.contacts[username])

        for feed_id in contact_feed_ids:
            possible_contact = ContactAddWidget(feed_id, parent=self)
            myQListWidgetItem = QListWidgetItem(self.contactAddList)
            myQListWidgetItem.setSizeHint(possible_contact.sizeHint())
            self.contactAddList.addItem(myQListWidgetItem)
            self.contactAddList.setItemWidget(myQListWidgetItem, possible_contact)
            self.listElements.append(possible_contact)
        #in case you added an entry we may need to remove an entry
        for entry in self.listElements:
            if entry.added == True:
                self.contactAddList.removeItemWidget(entry)
        return


class ContactEntryWidget(QWidget):
    def __init__(self, feedID, name, parent=None):
        super(ContactEntryWidget, self).__init__(parent)
        # Setup Layout
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        # Label for feed id
        self.feedLabel = QLabel()
        self.feedLabel.setText(feedID)
        self.hbox.addWidget(self.feedLabel)
        # Label for name associated with feed id
        self.name = QLabel()
        self.name.setText(name)
        self.hbox.addWidget(self.name)


class ContactAddWidget(QWidget):
    def __init__(self, pubKey,parent=None):
        super(ContactAddWidget, self).__init__(parent)
        self.pub_key = pubKey
        # Setup Layout
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.requesterLabel = QLabel()
        self.requesterLabel.setText(self.pub_key)
        self.hbox.addWidget(self.requesterLabel)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("name")
        self.hbox.addWidget(self.nameInput)

        self.addButton = QPushButton()
        self.addButton.setText("add")
        self.addButton.clicked.connect(self.addToContacts)
        self.hbox.addWidget(self.addButton)
        self.added = False

    def addToContacts(self):
        act.contacts.load()
        act.create_new_contact(self.nameInput.text(), self.pub_key)
        act.contacts.save()
        self.deleteLater()
        print(self.parent())
        self.parent().parent().parent().loadContactEntries()
        return


class ShareTab(QWidget):
    def __init__(self, parent=None):
        super(ShareTab, self).__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.pubInputs = []
        self.contact_usernames = act.get_all_contact_dict().keys()

        # Input for secret name
        self.secretNameInput = QLineEdit()
        self.secretNameInput.setPlaceholderText("Name for Secret")
        self.vbox.addWidget(self.secretNameInput)

        # Input for Secret
        self.secretInput = QLineEdit()
        self.secretInput.setPlaceholderText("Secret you want to share")
        self.vbox.addWidget(self.secretInput)

        # Input for password
        self.passInput = QLineEdit()
        self.passInput.setPlaceholderText("Password")
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
            pubInput = QComboBox()
            pubInput.addItem("-")
            for name in self.contact_usernames:
                pubInput.addItem(name)
            self.pubInputs.append(pubInput)
            self.scrollLayout.addWidget(pubInput)
            self.scroll.resize(self.scroll.size())

    def shareSecret(self):
        recipients = []
        for combobox in self.pubInputs:
            recipients.append(combobox.currentText())
        if len(recipients) == len(set(recipients)):
            secret_name = self.secretNameInput.text()
            secret = self.secretInput.text()
            password = self.passInput.text()
            num_shares = self.numShardsInput.currentText()
            threshold = self.numShardsRecInput.currentText()
            # TODO method to send shards in actions.py
        else:
            # TODO ErrorDialog
            print("duplicates!!")
        return


# ~~~~~~~~~~~~ Recovery Tab  ~~~~~~~~~~~~

class RecoveryTab(QWidget):
    def __init__(self, parent=None):
        super(RecoveryTab, self).__init__(parent)
        # Setup Layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        qFont = QFont()
        qFont.setBold(True)

        # Add automatic recovery part
        self.autoLabel = QLabel()
        self.autoLabel.setText("AUTO-RECOVERY")
        self.autoLabel.setFont(qFont)
        self.autoLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.autoLabel)
        self.autoRecovery = AutoRecovery(self)
        self.vbox.addWidget(self.autoRecovery)

        # Add manual recovery part
        self.manualLabel = QLabel()
        self.manualLabel.setText("MANUAL RECOVERY")
        self.manualLabel.setFont(qFont)
        self.manualLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.manualLabel)
        self.manualRecovery = ManualRecovery(self)
        self.vbox.addWidget(self.manualRecovery)
        self.recButton = QPushButton("Recover")
        self.recButton.clicked.connect(self.handleManualRecovery)
        self.vbox.addWidget(self.recButton)


    def handleManualRecovery(self):
        # TODO Initiate manual recovery (writing in feeds etc)
        pass

    def autoRecovery(self):
        # TODO Initiate auto-recovery
        pass


# AutomaticRecovery Widget of the Recovery Tab
class AutoRecovery(QWidget):
    def __init__(self, parent=None):
        super(AutoRecovery, self).__init__(parent)
        # Setup Layout
        self.hbox = QHBoxLayout(self)
        self.setLayout(self.hbox)

        # ComboBox containing names of shared secrets
        self.keyNameSelection = QComboBox()
        self.updateComboBox()  # doesn't do anythin at the moment
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
        # Setup Layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Input field for Name of Secret to be recovered
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Name of Secret")
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
        self.lbl_box_widget = QWidget()
        self.lbl_box_widget.setLayout(QHBoxLayout())
        #self.listLabel = QLabel()
        #self.listLabel.setText("Contacts which hold a shard")
        #self.lbl_box_widget.layout().addWidget(self.listLabel)
        self.numShardsLabel = QLabel()
        self.numShardsLabel.setText("Number of shards")
        self.lbl_box_widget.layout().addWidget(self.numShardsLabel)
        self.numShardsInput = QComboBox()
        for i in range(1,20):
            self.numShardsInput.addItem(str(i))
        self.numShardsInput.currentTextChanged.connect(self.updateWidgets)
        self.lbl_box_widget.layout().addWidget(self.numShardsInput)
        self.lbl_box_widget.layout().setSpacing(40)
        self.thresholdLabel = QLabel()
        self.thresholdLabel.setText("Threshold")
        self.lbl_box_widget.layout().addWidget(self.thresholdLabel)
        self.threshold = QComboBox()
        for i in range(1, int(self.numShardsInput.currentText())+1):
            self.threshold.addItem(str(i))
        self.lbl_box_widget.layout().addWidget(self.threshold)
        #self.removeInputBtn = QPushButton("-")
        #self.removeInputBtn.setMaximumWidth(25)
        #self.removeInputBtn.clicked.connect(self.removeInputField)
        #self.lbl_box_widget.layout().addWidget(self.removeInputBtn)
        #self.addInputBtn = QPushButton("+")
        #self.addInputBtn.setMaximumWidth(25)
        #self.addInputBtn.clicked.connect(self.addInputField)
        #self.lbl_box_widget.layout().addWidget(self.addInputBtn)
        self.vbox.addWidget(self.lbl_box_widget)

        # get usernames and empty List holding reference to all the input field of pub keys
        self.contact_usernames = act.get_all_contact_dict().keys()
        self.added_list = []
        self.pubInputs = []
        # Add 1 Input field to start off
        self.addInputField()
        # Add widget to main Layout
        self.scroll.setWidget(self.scrollContent)
        self.vbox.addWidget(self.scroll)

    def updateWidgets(self, newValue):
        self.updatenumShardsRec(int(newValue))
        self.updateInputField(int(newValue))

    def updatenumShardsRec(self, newValue):
        self.threshold.clear()
        for i in range (1, newValue+1):
            self.threshold.addItem(str(i))

    def updateInputField(self, newValue):
        for j in range(len(self.pubInputs), 0, -1):
            self.scrollLayout.removeWidget(self.pubInputs.pop())
        for i in range(int(self.numShardsInput.currentText())):
            pubInput = QComboBox()
            pubInput.addItem("-")
            for name in self.contact_usernames:
                pubInput.addItem(name)
            self.pubInputs.append(pubInput)
            self.scrollLayout.addWidget(pubInput)
            self.scroll.resize(self.scroll.size())

    def addInputField(self):
        pubInput = QComboBox()
        pubInput.addItem("-")
        for name in self.contact_usernames:
            pubInput.addItem(name)
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