try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import datetime
import os.path
import pickle

import pyglet  # pip install pyglet

import TextWrapper
import feed
import pcap

import os
import sys

# import platform

# system = platform.system()  # determine platform

# Load Fonts
dirname = os.path.abspath(os.path.dirname(__file__))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeue.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueBd.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueIt.ttf'))

#TODO: install:
#pip install testfixtures
#pip install sqlalchemy
#pip install PyNaCl

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../07-logStore/src/logStore')
sys.path.append(folderG7)
print(folderG7)
from downConnection.DatabaseConnector import DatabaseConnector
from functions.Event import Event, Meta, Content
import hashlib  # Comes with python
import secrets  # Comes with python
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from testfixtures import LogCapture

class Login(Frame):

    def open_Chat(self):
        global app, root
        root.destroy()  # close old window
        root = Tk()  # create new Tk
        root.config(bg="lightgrey")
        app = Chat(master=root)  # create chat window
        # root2 = Toplevel()
        # app2 = Chat(root2)

    def chooseUsername(self, name):
        global username
        username = name

    def register(self, R_username=None):
        if R_username != "":
            self.loginAttempt(R_username)
        else:
            self.username_label.config(text="Enter Username:")
            self.usernameField.delete(0, 'end')

    def login(self, username=None):
        if username != "":
            pass
        else:
            self.username_label.config(text="Enter Username:")
            self.usernameField.delete(0, 'end')

    def createWidgets(self):
        self.loginFrame = Frame(self.master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.loginFrame.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)

        # LOGIN:
        # Username
        self.username_label = Label(self.loginFrame, text='Enter Username:')
        self.username_label.grid(column=0, row=3, sticky=N + S + E + W)
        self.usernameField = Entry(self.loginFrame, textvariable=self.username)
        self.usernameField.bind('<Return>', lambda event: self.login(self.username.get()))
        self.usernameField.grid(column=0, row=4, sticky=N + S + E + W)

        # Button
        self.login_button = Button(self.loginFrame, text='login',
                                   command=lambda: self.login(self.username.get()))
        self.login_button.grid(column=0, row=7, sticky=N + S + E + W)

        # REGISTER
        # Register Username  # --> In separatem Fenster? ToDo: Login wegmachen
        self.R_username_label = Label(self.loginFrame, text='\n\n\nNot registered yet?\n\nchoose Username:')
        self.R_username_label.grid(column=0, row=8, sticky=N + S + E + W)
        self.R_usernameField = Entry(self.loginFrame, textvariable=self.R_username)
        self.R_usernameField.bind('<Return>', lambda event: self.register(self.R_username.get()))
        self.R_usernameField.grid(column=0, row=9, sticky=N + S + E + W)

        # Button
        self.R_button = Button(self.loginFrame, text='register',
                               command=lambda: self.register(self.R_username.get()))
        self.R_button.grid(column=0, row=12, sticky=N + S + E + W)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Login")
        self.msg = StringVar()
        self.username = StringVar()
        self.R_username = StringVar()
        self.createWidgets()


class Chat(Frame):

    def save(self, content):
        feed._appendIt(self.username, 'append', content)

    def addAll(self, username, content):
        # try:
        # allMessges = SchnittstellenHelper.returnAll()#gruppe07.returnAll()
        # for i in range(len(allMessges)):
        #    if allMessges[i][2] != self.username: #sender if the content of the current entry at the index of the sender is not myself
        #        pass
        # except:
        self.add(username, content)

    def add(self, username, content):
        # self.updateContent(self.partner)  # instead of an update button, it checks for new incoming messages when/before when you send a new message: currently results in errors (Aborted (core dumped)): seems like an infinite loop
        self.time = datetime.datetime.now()
        # self.lastMessage[chatNumber] = self.time #Update last message sent from this person
        if username != self.username:  # user updated
            try:
                wrappedContent = TextWrapper.textWrap(content, 0)
                print("getting message from " + self.partner + ":")
                self.listBox1.insert('end', '[' + self.time.strftime("%H:%M:%S") + ']')
                self.listBox1.itemconfig('end', bg='white', foreground="lightgrey")
                self.listBox1.insert('end', wrappedContent[0])
                for i in range(2): self.listBox2.insert('end', "")  # add 2 empty lines to balance both sides
                self.listBox1.itemconfig('end', bg='white')
                self.listBox1.yview(END)
                self.listBox2.yview(END)
                self.listBox1.insert('end', '')  # some space to enhance appeal
                self.listBox2.insert('end', '')
            except:
                print("no new messages available from " + self.partner)
        else:  # user typed something
            lastEntry = ''
            index = 0
            ContentArray = pcap.dumpIt(username + '.pcap')
            while True:  # while not at the end of the list (we want to get the last entry)
                try:
                    lastEntry = ContentArray[index + 1]
                    lastEntry = lastEntry[2: len(ContentArray[index + 1]) - 2]  # removing the [""]
                    index += 1
                except:
                    print("Arrived at last message: \"" + lastEntry + "\"")
                    if content != '':
                        self.listBox2.insert('end', '[' + self.time.strftime("%H:%M:%S") + ']')
                        self.listBox2.itemconfig('end', bg='#dafac9',
                                                 foreground="lightgrey")  # dafac9 = light green (coloring for sender messaages)
                        self.listBox1.insert('end',
                                             '')  # adjust the other listbox for them to by synced on the same height
                        wrappedContent = TextWrapper.textWrap(content, 0)
                        print(".", wrappedContent)
                        for i in range(len(wrappedContent)):
                            self.listBox2.insert('end', wrappedContent[i])
                            self.listBox2.itemconfig('end', bg='#dafac9')
                            self.listBox1.insert('end',
                                                 '')  # adjust the other listbox for them to by synced on the same height
                            self.listBox1.yview(END)
                            self.listBox2.yview(END)

                        self.listBox1.yview(END)
                        self.listBox2.yview(END)
                        self.listBox1.insert('end', '')  # some space to enhance appeal
                        self.listBox2.insert('end', '')

                        self.text_field.delete(0, 'end')
                        self.save(content)
                    break

    def updateContent(self, fromUser):
        # ContentArray = pcap.dumpIt(fromUser + '.pcap')
        # print(ContentArray[self.alreadyUpdatedIndex+1])
        self.listBox1.delete(0, 'end')
        self.listBox2.delete(0, 'end')
        counter = 0
        while True:
            try:
                # print(pcap.dumpIt(fromUser + '.pcap')[1])
                self.add(fromUser, pcap.dumpIt(fromUser + '.pcap')[counter])
                counter += 1
            except:
                print("   No new messages found from: " + str(self.partner))
                break

    # these methods ensure that when the user scrolls with his mouse instead of the scrollbar, that both list boxes are synced and move at the same time up and down
    def scroll1(self,
                *args):  # when the user scrolls the listBox1, then this method ensures the position of listBox2 is synced
        if self.listBox2.yview() != self.listBox1.yview():  # when the listBox2 is out of sync...
            self.listBox2.yview_moveto(args[0])  # ...adjust the yview of listBox2
        # self.scrollbar.set(*args)  # sync the scrollbar with the mouse wheel position

    def scroll2(self,
                *args):  # when the user scrolls the listBox2, then this method ensures the position of listBox1 is synced
        if self.listBox1.yview() != self.listBox2.yview():  # when the listBox1 is out of sync...
            self.listBox1.yview_moveto(args[0])  # ...adjust the yview of listBox1
        # self.scrollbar.set(*args)  # sync the scrollbar with the mouse wheel position

    def yview(self, *args):  # self configured yview command. the only job is to trigger both sync methods from abouve
        self.listBox1.yview(*args)
        self.listBox2.yview(*args)

    def createWidgets(self):
        print("connected as: \"" + self.username + "\"")
        # window title: shows by what username you are connected to the application
        self.master.title("Subjective Chat: " + self.username.upper())

        # Chat: title bar: shows to who you are currently writing
        self.username_label = Label(self.topFrameChat, text="")
        self.username_label.configure(bg="#ededed", font=('HelveticaNeue', 16))

        # Chat: chatfield
        self.scrollbar = Scrollbar(self.middleFrameChat, orient="vertical")
        self.scrollbar.config(command=self.yview)

        self.listBox1 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll1)
        self.listBox1.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))

        self.listBox2 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll2)
        self.listBox2.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))

        # ---Tab Section---
        self.tabScrollbar = Scrollbar(self.tabFrame, orient="vertical")
        self.listBox3 = Listbox(self.tabFrame, height=24, width=25, yscrollcommand=self.tabScrollbar.set)
        self.tabScrollbar.config(command=self.listBox3.yview)
        self.listBox3.configure(bg='white', font=('HelveticaNeue', 15, 'bold'))

        self.listBox3.bind("<<ListboxSelect>>", lambda x: self.loadChat())

        # Chat: actions
        self.text_field = Entry(self.bottomFrameChat, textvariable=self.msg, font=('HelveticaNeue', 10))
        self.text_field.configure(bg='#f0f0f0')
        self.text_field.bind('<Return>', lambda event: self.addAll(self.username, self.msg.get()))
        self.send_button = Button(self.bottomFrameChat, text='Send',
                                  command=lambda: self.addAll(self.username, self.msg.get()), bg="#25D366",
                                  activebackground="#21B858", font=('HelveticaNeue', 10))
        self.update_button = Button(self.bottomFrameChat, text='Update',
                                    command=lambda: self.updateContent(self.partner), bg="white",
                                    font=('HelveticaNeue', 10))
        self.newChatButtonState = 0

        self.newMessageButton = Button(self.tabTopBar, text="new Chat",
                                       command=lambda: self.saveTypeAndSwitchState("NewChat"), bg="#25D366")
        self.newGroupButton = Button(self.tabTopBar, text="new Group",
                                     command=lambda: self.saveTypeAndSwitchState("NewGroup"), bg="#34B7F1")

        self.newMessageField = Entry(self.tabTopBar, textvariable=self.newMessageAddressant)
        self.newMessageField.bind('<Return>', lambda x: self.switchState())
        self.newMessageField.insert(0, "Enter Recepient(s) here")

    def createNewMessage(self, username):
        # TODO: check if entered partner is a valid partner which exists
        if username == "":
            pass
        else:
            if self.ButtonType == "NewChat":  # <-------
                self.personList.append([username, 12345])  # TODO: give Chat ID (12345 is just an example)
                self.peopleToBeAdded.append(username)  # so we know who to add
            else:  # self.ButtonType == "Group" TODO: not tested yet: should just add a list of participants as addressants(?)#<-------
                # print("Entered group participants:", self.newMessageAddressant.get())
                List = self.newMessageAddressant.get().split(", ")  # Group members should be separated by ", "
                # print("entered group:", List, "type:", str(type(List)))
                self.personList.append([List, 12345])  # TODO: give Chat ID (12345 is just an example)
                self.peopleToBeAdded.append(username)  # so we know who to add
            self.newMessageField.delete(0, 'end')

    def saveTypeAndSwitchState(self, Type):
        self.ButtonType = Type  # if it is group or chat
        self.switchState()

    def switchState(self):  # 0 = new chat , 1 = create chat
        if self.newChatButtonState == 0:  # create Chat or Group
            self.newMessageField.grid(row=0, column=0, sticky="ew")
            self.newMessageButton.config(text="create")
            self.newGroupButton.grid_remove()  # remove to make it prettier
            self.newChatButtonState = (
                                                  self.newChatButtonState + 1) % 2  # switch self.newChatButtonState between 0 and 1

        elif self.newChatButtonState == 1:  # Enter Chatname Or Group Name
            self.createNewMessage(self.newMessageAddressant.get())
            self.addPartners()
            self.newMessageField.delete(0, 'end')
            self.newMessageField.insert(0, "Enter Recepient(s) here")
            self.newMessageField.grid_remove()
            self.newMessageField.config(bg="white")
            self.newMessageButton.config(text="new Chat")
            self.newGroupButton.grid(row=0, column=3, sticky="e")
            self.newChatButtonState = (self.newChatButtonState + 1) % 2  # switch state between 0 and 1
            '''
            #check method which returns all feeds
            FeedArray = gruppe07.returnAllFeeds()
            found = False
            for i in FeedArray:
                if i == self.newMessageAddressant:
                    found = True
            if found:
                found = False
                self.newMessageField.config(bg="white")
                self.newMessageField.insert(0,"Enter Recepient(s) here")
                self.newMessageField.grid_remove()
                self.newMessageButton.config(text="new Chat")
                self.newChatButtonState = (self.newChatButtonState + 1) % 2 # switch state between 0 and 1
            else: # username not found
                self.newMessageField.insert(0,"Recepient(s) not found...")
                self.newMessageField.config(bg="#ffc2b3")
            '''

    def loadChat(
            self):  # when the user clicks on Person in listBox3 this function is called and loads the correct chat and sets up everything needed to start the communication
        selection = self.listBox3.curselection()[0]  # this gives an int value: first element = 0
        if selection % 2 == 1:
            selection -= 1
        if self.partner != self.personList[int(selection / 2)]:
            self.partner = self.listBox3.get(self.listBox3.curselection()[0])
            self.username_label.config(text=self.partner)
            self.updateContent(self.partner)

    def addPartners(self):
        self.newMessageCounter = 9  # TODO: this needs to be a dictionary (with the key as partnerName and value as counter) which is automatically updated when new messages arrive thath haven't been read (increase counter)
        if len(self.peopleToBeAdded) == 0:  # when application is started, this is always the case
            for i in range(len(self.personList)):
                self.listBox3.insert('end', self.personList[i][
                    0])  # with counter number TextWrapper.mergeNameCounter(self.personList[i], self.newMessageCounter,45)
                if (self.newMessageCounter != 0):
                    self.listBox3.itemconfig(i, bg='#dfd')
                else:
                    self.listBox3.itemconfig(i, bg="white")
                self.listBox3.insert('end', '')
        else:  # This can only be the case when the application is already started and the person just added a new chat / group
            for i in range(len(self.peopleToBeAdded)):
                self.listBox3.insert('end', self.peopleToBeAdded[
                    i])  # with counter number TextWrapper.mergeNameCounter(self.personList[i], self.newMessageCounter,45)
                if self.newMessageCounter != 0:
                    self.listBox3.itemconfig(i, bg='#dfd')
                else:
                    self.listBox3.itemconfig(i, bg="white")
                self.listBox3.insert('end', '')
            self.peopleToBeAdded = list()  # remove people since we already added them

        # Opening the first Chat by default
        if len(self.personList) != 0:
            self.partner = self.personList[0][0]
            self.username_label.config(text=self.partner)
        else:
            # self.partner = self.personList[0] # opening the first chat by default.
            self.username_label.config(text="")

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Subjective Chat")

        # Set Variables
        self.msg = StringVar()
        self.username = username
        self.partner = StringVar()
        self.newMessageAddressant = StringVar()
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.lastMessage = list()
        self.peopleToBeAdded = list()

        # set self.personList:
        try:  # Try to load the Variable: if it works, we know we can load it and assign it
            x = pickle.load(open("Data.pkl", "rb"))  # if it fails then we know we have not populated out pkl file yet
            self.personList = pickle.load(open("Data.pkl", "rb"))
            print("Variable sucessfully loaded: personList = ", self.personList)
        except:  # if we can't load the variable, we need to assign and dump it first
            List = list()
            pickle.dump(List, open("Data.pkl", "wb"))  # create an empty object
            self.personList = pickle.load(open("Data.pkl", "rb"))  # loading and setting it now
            print("File didn't exist, I created it for you: personList = ", self.personList)

        # Configure Application layout
        self.master.configure(height=24, width=50)
        self.tabFrame = Frame(self.master)
        self.tabFrame.pack(side='left', fill='both', expand=True)
        self.chatFrame = Frame(self.master)
        self.chatFrame.pack(side='right', fill='both', expand=True)

        # TabFrame new message area
        self.tabTopBar = Frame(self.tabFrame)

        # ---Chat Section---
        # Configure Frames
        self.topFrameChat = Frame(self.chatFrame)
        self.topFrameChat.pack(fill='both', expand=True)

        self.middleFrameChat = Frame(self.chatFrame)
        self.middleFrameChat.pack(fill='both', expand=True)

        self.bottomFrameChat = Frame(self.chatFrame)
        self.bottomFrameChat.pack(fill='both', expand=True)

        # Place Widgets
        self.createWidgets()

        self.addPartners()  # now we can add the partner(s) into ListBox3

        # Configure Subframes
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.tabFrame.rowconfigure(1, weight=1)
        self.chatFrame.columnconfigure(1, weight=1)
        self.topFrameChat.rowconfigure(1, weight=1)
        self.topFrameChat.columnconfigure(1, weight=1)
        self.middleFrameChat.rowconfigure(1, weight=1)
        self.middleFrameChat.columnconfigure(1, weight=1)
        self.bottomFrameChat.rowconfigure(1, weight=1)
        self.bottomFrameChat.columnconfigure(1, weight=1)

        # Placement
        self.username_label.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.listBox1.grid(row=1, column=0, sticky="nsew")
        self.listBox2.grid(row=1, column=1, sticky="nsew")
        self.listBox3.grid(row=1, column=0, sticky="nsew")
        self.text_field.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.send_button.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.update_button.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.tabTopBar.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.newMessageButton.grid(row=0, column=1, sticky="e")
        self.newGroupButton.grid(row=0, column=3, sticky="e")


root = Tk()
app = Login(master=root)

try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    # exit()
    pass

# Save settings with pickle
pickle.dump(app.personList, open("Data.pkl", "wb"))  # create an empty object
print("\"personList\" has been saved to \"Data.pkl\": personList = ", app.personList)
#TODO: save username for automatic login when keyfile is present
