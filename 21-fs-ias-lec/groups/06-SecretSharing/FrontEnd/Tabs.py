"""THis is super module"""


# ~~~~~~~~~~~~ Imports  ~~~~~~~~~~~~
# FIrst 3 imports mega nice

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
    QScrollArea,
)

from BackEnd import actions as act
from FrontEnd.Dialogs import NotificationDialog


# ~~~~~~~~~~~~ Contact Tab  ~~~~~~~~~~~~

class ContactTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup Layout
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        # Saved Contacts box
        qFont = QFont()
        qFont.setBold(True)
        self.contactsLabel = QLabel()
        self.contactsLabel.setText("SAVED CONTACTS")
        self.contactsLabel.setFont(qFont)
        self.contactsLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.contactsLabel)
        #List of saved contacts
        self.contactEntryList = QListWidget()
        self.contactEntries = []
        self.loadContactEntries()
        self.vbox.addWidget(self.contactEntryList)
        # Possible Contacts box
        self.knownFeedsLabel = QLabel()
        self.knownFeedsLabel.setText("KNOWN FEED IDS")
        self.knownFeedsLabel.setFont(qFont)
        self.knownFeedsLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.knownFeedsLabel)

        # List of possible contacts
        self.contactAddList = QListWidget()
        self.listElements = []
        self.updatePossibleContacts()
        self.vbox.addWidget(self.contactAddList)

    def loadContactEntries(self):
        contact_dict = act.get_all_contacts_dict()
        for key in contact_dict:
            feed_id = contact_dict[key]
            contactEntry = ContactEntryWidget(feed_id, key, parent=self)
            myQListWidgetItem = QListWidgetItem(self.contactEntryList)
            myQListWidgetItem.setSizeHint(contactEntry.sizeHint())
            self.contactEntryList.addItem(myQListWidgetItem)
            self.contactEntryList.setItemWidget(myQListWidgetItem, contactEntry)
            self.contactEntries.append(contactEntry)

    def updatePossibleContacts(self):
        self.contactAddList.clear()
        contact_feed_ids = act.rq_handler.get_feed_ids()
        # remove ids which are already in contacts
        for username in act.get_all_contacts_dict():
            if act.get_contact_feed_id(username) in contact_feed_ids:
                contact_feed_ids.remove(act.get_contact_feed_id(username))
        for feed_id in contact_feed_ids:
            possible_contact = ContactAddWidget(feed_id, parent=self)
            myQListWidgetItem = QListWidgetItem(self.contactAddList)
            myQListWidgetItem.setSizeHint(possible_contact.sizeHint())
            self.contactAddList.addItem(myQListWidgetItem)
            self.contactAddList.setItemWidget(myQListWidgetItem, possible_contact)
            self.listElements.append(possible_contact)

        return

# Widget for each contact in ListWidget
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

# Widget for each possible contact in ListWidget
class ContactAddWidget(QWidget):
    def __init__(self, pubKey, parent=None):
        super(ContactAddWidget, self).__init__(parent)
        self.pub_key = pubKey
        # Setup Layout
        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)
        # Label for public key of possible contact
        self.requesterLabel = QLabel()
        self.requesterLabel.setText(self.pub_key.hex()[:35]+"...")
        self.requesterLabel.setWordWrap(True)
        self.hbox.addWidget(self.requesterLabel)
        # Input for name associated with public key
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("name")
        self.hbox.addWidget(self.nameInput)
        # Button to add to Contacts
        self.addButton = QPushButton()
        self.addButton.setText("add")
        self.addButton.clicked.connect(self.addToContacts)
        self.hbox.addWidget(self.addButton)
        self.added = False

    def addToContacts(self):
        act.contacts.load()
        act.create_new_contact(self.nameInput.text(), self.pub_key)
        act.contacts.save()
        self.added = True
        self.parent().parent().parent().updatePossibleContacts()
        self.parent().parent().parent().loadContactEntries()
        return


class ShareTab(QWidget):
    def __init__(self, parent=None):
        super(ShareTab, self).__init__(parent)
        # setup layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.pubInputs = []
        self.contact_usernames = act.get_all_contacts_dict().keys()

        # Input for secret name
        self.secretNameInput = QLineEdit()
        self.secretNameInput.setPlaceholderText("Name for Secret")
        self.vbox.addWidget(self.secretNameInput)

        # Input for Secret
        self.secretInput = QLineEdit()
        self.secretInput.setPlaceholderText("Secret you want to share")
        self.vbox.addWidget(self.secretInput)

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

    def updateContacts(self):
        self.contact_usernames = act.get_all_contacts_dict().keys()
        self.updateInputField()

    def updateWidgets(self, newValue):
        self.updatenumShardsRec(int(newValue))
        self.updateInputField()

    def updatenumShardsRec(self, newValue):
        self.numShardsRecInput.clear()
        for i in range (1, newValue+1):
            self.numShardsRecInput.addItem(str(i))

    def updateInputField(self):
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
        empty = False
        recipients = []
        for combobox in self.pubInputs:
            username = combobox.currentText()
            if username == "-":
                empty = True
            recipients.append(combobox.currentText())
        if not empty:
            secret_name = self.secretNameInput.text()
            secret = self.secretInput.text()
            num_shares = self.numShardsInput.currentText()
            threshold = self.numShardsRecInput.currentText()
            private_key = act.rq_handler.event_factory.get_private_key()
            if not secret_name or not secret or not num_shares or not threshold:
                requiredFieldsDialog = NotificationDialog("All Input fields are required!")
                requiredFieldsDialog.exec_()

            holder_feed_ids = list(map(lambda x: act.get_contact_feed_id(x).hex(), recipients))
            print(holder_feed_ids)

            packages = act.split_secret_into_share_packages(
                name=secret_name,
                secret=secret.encode(act.core.ENCODING),
                threshold=int(threshold),
                number_of_packages=int(num_shares),
                holders=holder_feed_ids
            )

            events = []
            counter = 0
            for recipient in recipients:
                events.append(act.process_outgoing_sub_event(t=act.core.E_TYPE.SHARE, private_key=private_key,
                                           feed_id=act.get_contact_feed_id(recipient), password=None,
                                           name=secret_name, package=packages[counter]))
                counter += 1
            print(events)
            act.handle_outgoing_sub_events(events)
            nDialog = NotificationDialog("Shards successfully sent!")
            nDialog.exec_()
            self.resetInputs()
        else:
            nDialog = NotificationDialog("Please choose unique friends")
            nDialog.exec_()
        return

    def resetInputs(self):
        self.numShardsInput.setCurrentIndex(0)
        self.numShardsRecInput.setCurrentIndex(0)
        self.secretNameInput.clear()
        self.secretInput.clear()
        return

# ~~~~~~~~~~~~ Recovery Tab  ~~~~~~~~~~~~

class RecoveryTab(QWidget):
    def __init__(self, parent=None):
        super(RecoveryTab, self).__init__(parent)
        # Setup Layout
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        # fond for boldness
        self.qFont = QFont()
        self.qFont.setBold(True)

        # Add automatic recovery part
        self.autoLabel = QLabel()
        self.autoLabel.setText("AUTO-RECOVERY")
        self.autoLabel.setFont(self.qFont)
        self.autoLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.autoLabel)
        self.autoRecovery = AutoRecovery(self)
        self.vbox.addWidget(self.autoRecovery)

        # Add manual recovery part
        self.manualLabel = QLabel()
        self.manualLabel.setText("MANUAL RECOVERY")
        self.manualLabel.setFont(self.qFont)
        self.manualLabel.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.manualLabel)
        self.manualRecovery = ManualRecovery(self)
        self.vbox.addWidget(self.manualRecovery)

# AutomaticRecovery Widget of the Recovery Tab
class AutoRecovery(QWidget):
    def __init__(self, parent=None):
        super(AutoRecovery, self).__init__(parent)
        # Setup Layout
        self.hbox = QHBoxLayout(self)
        self.setLayout(self.hbox)

        # ComboBox containing names of shared secrets
        self.keyNameSelection = QComboBox()
        self.updateComboBox()
        self.hbox.addWidget(self.keyNameSelection)
        # Add Button to initiate recovery
        self.recoverButton = QPushButton("Recover")
        self.recoverButton.clicked.connect(self.handleAutoRecovery)
        self.hbox.addWidget(self.recoverButton)

    def updateComboBox(self):
        self.keyNameSelection.clear()
        for name in act.secrets.keys():
            if name != "mapping":
                self.keyNameSelection.addItem(name)
        return

    def handleAutoRecovery(self):
        holders_feed_ids = list(map(lambda x: bytes.fromhex(x),
                                    act.secrets[self.keyNameSelection.currentText()]["Holders"]))
        private_key = act.rq_handler.event_factory.get_private_key()
        name = self.keyNameSelection.currentText()
        events = []
        for feed_id in holders_feed_ids:
            print(feed_id)
            events.append(act.process_outgoing_sub_event(t=act.core.E_TYPE.REQUEST, private_key=private_key,
                                                         feed_id=feed_id, password=None, name=name))
        act.handle_outgoing_sub_events(events)
        return

    def resetInputs(self):
        self.numShardsInput.setCurrentIndex(0)
        self.numShardsRecInput.setCurrentIndex(0)
        self.secretNameInput.clear()
        self.secretInput.clear()
        self.passInput.clear()
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

        # create ScrollArea for friends public key input
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)

        # Setup Content Widget and Layout for the Scroll Area
        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollContent.setLayout(self.scrollLayout)

        # Setup Widget containing number of shards and threshold
        self.lbl_box_widget = QWidget()
        self.lbl_box_widget.setLayout(QHBoxLayout())
        self.numShardsLabel = QLabel()
        self.numShardsLabel.setText("Number of shards")
        self.lbl_box_widget.layout().addWidget(self.numShardsLabel)
        self.numShardsInput = QComboBox()
        for i in range(1,20):
            self.numShardsInput.addItem(str(i))
        self.numShardsInput.currentTextChanged.connect(self.updateWidgets)
        self.lbl_box_widget.layout().addWidget(self.numShardsInput)
        self.thresholdLabel = QLabel()
        self.thresholdLabel.setText("Threshold")
        self.lbl_box_widget.layout().addWidget(self.thresholdLabel)
        self.threshold = QComboBox()
        for i in range(1, int(self.numShardsInput.currentText())+1):
            self.threshold.addItem(str(i))
        self.lbl_box_widget.layout().addWidget(self.threshold)
        self.lbl_box_widget.layout().setSpacing(20)
        self.sizeLabel = QLabel()
        self.sizeLabel.setText("Size")
        self.lbl_box_widget.layout().addWidget(self.sizeLabel)
        self.sizeBox = QComboBox()
        self.sizeBox.addItems(["don't know", "SMALL", "NORMAL", "LARGE"])
        self.lbl_box_widget.layout().addWidget(self.sizeBox)
        self.vbox.addWidget(self.lbl_box_widget)

        # get usernames and empty List holding reference to all the input field of pub keys
        self.contact_usernames = act.get_all_contacts_dict()
        self.added_list = []
        self.pubInputs = []
        # Add 1 Input field to start off
        self.addInputField()
        # Add widget to main Layout
        self.scroll.setWidget(self.scrollContent)
        self.vbox.addWidget(self.scroll)
        self.recButton = QPushButton("Recover")
        self.recButton.clicked.connect(self.handleManualRecovery)
        self.vbox.addWidget(self.recButton)

    def updateContacts(self):
        self.contact_usernames = act.get_all_contacts_dict()
        self.updateInputField()

    def updateWidgets(self, newValue):
        self.updatenumShardsRec(int(newValue))
        self.updateInputField()

    def updatenumShardsRec(self, newValue):
        self.threshold.clear()
        for i in range (1, newValue+1):
            self.threshold.addItem(str(i))

    def updateInputField(self):
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

    def handleManualRecovery(self):
        holders_feed_ids = []
        for cbox in self.pubInputs:
            holders_feed_ids.append(act.get_contact_feed_id(cbox.currentText()))
        size = self.sizeBox.currentText()
        if size == "don't know":
            size = None
        elif size == "SMALL":
            size = act.S_SIZE.SMALL
        elif size == "NORMAL":
            size = act.S_SIZE.NORMAL
        else:
            size = act.S_SIZE.LARGE
        act.add_information_from_scratch(name=self.nameInput.text(), threshold=int(self.threshold.currentText()),
                                         number_of_packages=int(self.numShardsInput.currentText()),
                                         holders=list(map(lambda x: x.hex(), holders_feed_ids)), size=size)
        # create requests
        events = []
        private_key = act.rq_handler.event_factory.get_private_key()
        name = self.nameInput.text()

        for feed_id in holders_feed_ids:
            events.append(act.process_outgoing_sub_event(t=act.core.E_TYPE.REQUEST, private_key=private_key, feed_id=feed_id,
                                                     name=name, password=None))

        act.handle_outgoing_sub_events(events)
        return
