import json
from sys import getsizeof

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

# -------------
# WHAT YOU NEED TO DO:
#    we haven't implemented an automatic installation of the following
#    libraries yet so you'll need to install them manually.
#    Here are the commands for Linux:

# prerequisite: # apt install python3-pip
# You also need to navigate to 'BACnet/groups/07-logStore/src' and then:
# 		'pip install .'

import pickle  # pip install pickle-mixin
import pyglet  # pip install pyglet
from PIL import ImageTk, Image  # sudo apt-get install python3-pil python3-pil.imagetk
import base64  # pip install pybase64
# -------------


# Libraries which are included:

import os
import os.path
import secrets
import random
import hashlib
import webbrowser
import string
import math
import platform
import time
import datetime
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.Padding import unpad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode

import pyDH

# determine platform
system = platform.system()  # currently only supports Linux (works on other platforms but the look and feel is not the same)

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

# Import from gruppe04
folderG4 = os.path.join(dirname, '../../04-logMerge/eventCreationTool')
sys.path.append(folderG4)
import EventCreationTool

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../07-14-logCtrl/src')
sys.path.append(folderG7)
from logStore.transconn.database_connector import DatabaseConnector
# from testfixtures import LogCapture
from logStore.funcs.event import Event, Meta, Content
from logStore.appconn.chat_connection import ChatFunction

# Import our (gruppe03) libraries
from subChat import Colorize
from subChat import TextWrapper

# Load Fonts
# Helvetica Neue:
pyglet.font.add_file(os.path.join(dirname, 'subChat/font/helveticaneue/HelveticaNeue.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'subChat/font/helveticaneue/HelveticaNeueBd.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'subChat/font/helveticaneue/HelveticaNeueIt.ttf'))

# Set global variables
app = None  # currently active app
pickle_file_names = ['personList.pkl', 'username.pkl']  # use to reset user or create new one
switch = ["", "", ""]


# -----------------------------------------------------------------------------


class Login(Frame):

    def __init__(self, master=None):
        self.username = StringVar()
        Frame.__init__(self, master)
        master.title("BAC net")
        master.config(bg="#f2f9ec")
        self.createWidgets()

    def createWidgets(self):
        global logo_path, name_path
        self.login_frame = Frame(self.master)
        self.login_frame.config(bg="#f2f9ec")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Logo img Label
        raw_img = Image.open(logo_path)
        render_img = ImageTk.PhotoImage(raw_img)
        self.img = Label(self.login_frame, image=render_img)
        self.img.image = render_img
        self.img.config(bg="#f2f9ec")

        # Name img Label
        raw_name_img = Image.open(name_path)
        render_name_img = ImageTk.PhotoImage(raw_name_img)
        self.name_img = Label(self.login_frame, image=render_name_img)
        self.name_img.image = render_name_img
        self.name_img.config(bg="#f2f9ec")

        # "REGISTER"

        self.username_label = Label(self.login_frame,
                                    text='\n\nLet\'s create a unique Key for you!\n\n\nchoose a Username:',
                                    bg='#f2f9ec')
        self.username_field = Entry(self.login_frame, textvariable=self.username)
        self.username_field.insert(0, "Enter your name here")
        self.username_field.bind("<Button-1>", lambda event: self.clear_on_entry())
        self.username_field.bind('<Return>', lambda event: self.create_key(self.username.get()))

        # Spacer
        self.spacer0 = Label(self.login_frame, bg='#f2f9ec')
        self.spacer1 = Label(self.login_frame, bg='#f2f9ec')
        self.spacer2 = Label(self.login_frame, bg='#f2f9ec')

        # Button
        self.button = Button(self.login_frame, text='create key', command=lambda: self.create_key(self.username.get()),
                             bg="#77b238", activebackground="#527a27")

        # Grid
        self.login_frame.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)
        self.spacer0.grid(column=0, row=0, sticky=N + S + E + W)
        self.img.grid(column=0, row=1, sticky=N + S + E + W)
        self.name_img.grid(column=0, row=2, sticky=N + S + E + W)
        self.username_label.grid(column=0, row=3, sticky=N + S + E + W)
        self.username_field.grid(column=0, row=4, sticky=N + S + E + W)
        self.spacer1.grid(column=0, row=5, sticky=N + S + E + W)
        self.button.grid(column=0, row=6, sticky=N + S + E + W)
        self.spacer2.grid(column=0, row=7, sticky=N + S + E + W)

    # -------------- HELP FUNCTIONS --------------
    def create_key(self, username=None):
        if username != "" and len(username) <= 16:
            ecf = EventCreationTool.EventFactory()
            public_key = ecf.get_feed_id()
            chat_function = ChatFunction()
            first_event = ecf.first_event('chat', chat_function.get_host_master_id())

            chat_function.insert_event(first_event)

            self.dictionary = {
                'username': username,
                'public_key': public_key
            }
            pickle.dump(self.dictionary, open(pickle_file_names[1], "wb"))  # save username and key
            print("Your username has been saved:", username)

            self.open_Chat()
        else:
            self.username_field.delete(0, 'end')
            self.username_field.insert(0, 'Username must be < 17 letters')

    def clear_on_entry(self):
        if self.username_field.get() == 'Enter your name here' \
                or self.username_field.get() == 'Username must be < 17 letters':
            self.username_field.delete(0, 'end')

    def open_Chat(self):
        global app, root
        root.destroy()  # close old window
        root = Tk()  # create new Tk
        root.config(bg="lightgrey")
        app = Chat(master=root)  # create chat window
    # -------------- -------------- --------------


class DisplayFile(Frame):
    def __init__(self, master=None):
        global app
        Frame.__init__(self, master)
        self.master.title("File")

        self.master.configure(height=24, width=50)
        self.frame = Frame(self.master)
        self.frame.pack(fill='both', expand=True)
        self.file = switch[0]
        self.file_name = switch[1][0:switch[1].rfind('.')]
        self.file_type = switch[2]
        self.file_ending = switch[1][switch[1].rfind('.') + 1:]

        self.createWidgets()

    def createWidgets(self):
        global switch, dirname

        # Where the files will be saved
        image_folder = os.path.join(dirname, 'Images/')
        pdf_folder = os.path.join(dirname, 'Pdfs/')
        try:  # try to create a directory
            os.mkdir(image_folder)
            os.mkdir(pdf_folder)
        except FileExistsError:  # if this gives an error, then we know the file already exists.
            pass

        # Convert back from hex String to bytes
        byte_string = self.file.encode("utf-8")

        # Decode
        decoded_string = base64.b64decode(byte_string)

        # Display an image
        if self.file_type == 'img':
            filename = str(
                self.file_name + '.' + self.file_ending)  # + "[" + str(datetime.datetime.now())+'].' + self.file_ending)
            file_path = os.path.join(image_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded_string)

            raw_img = Image.open(file_path)
            render_img = ImageTk.PhotoImage(raw_img)

            img = Label(self.frame, image=render_img)
            img.image = render_img
            img.pack(side="bottom", fill="both", expand="yes")

        # Display a pdf
        elif self.file_type == 'pdf':
            filename = str(self.file_name + "[" + str(datetime.datetime.now()) + '].' + self.file_ending)
            file_path = os.path.join(pdf_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded_string)
            webbrowser.open(file_path)


class Chat(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("BAC net")

        # Set Variables
        self.msg = StringVar()
        self.dictionary = pickle.load(open(pickle_file_names[1], "rb"))
        self.username = self.dictionary['username']
        self.feed_id = self.dictionary['public_key']
        self.partner = list()  # empty partner as default... tuple: name, chatID
        self.partner.append("")
        self.partner.append("")
        self.entry_field = StringVar()
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.lastMessage = list()
        self.chat_function = ChatFunction()
        self.stored_messages = 0
        self.chat_messages_index = 1
        self.pubkey = 0
        self.partners_pubkey = 0
        self.messages = []
        self.send_pubkey = True
        self.is_initiator = False
        self.pubkey_dict = {}
        self.groupchats = []
        self.generate_new_pubkey = True

        # Set EventFactory
        x = self.chat_function.get_current_event(self.chat_function.get_all_feed_ids()[1])
        most_recent_event = self.chat_function.get_current_event(self.feed_id)
        self.ecf = EventCreationTool.EventFactory(most_recent_event)  # damit wieder gleiche Id benutzt wird

        # set self.personList:
        try:  # Try to load the Variable: if it works, we know we can load it and assign it
            x = pickle.load(
                open(pickle_file_names[0], "rb"))  # if it fails then we know we have not populated our pkl file yet
            self.person_list = pickle.load(open(pickle_file_names[0], "rb"))
        except:  # if we can't load the variable, we need to assign and dump it first
            List = list()
            pickle.dump(List, open(pickle_file_names[0], "wb"))  # create an empty object
            self.person_list = pickle.load(open(pickle_file_names[0], "rb"))  # loading and setting it now

        # Configure Application layout
        self.master.configure(height=24, width=50)
        self.tabFrame = Frame(self.master)
        self.tabFrame.pack(side='left', fill='both', expand=True)
        self.chatFrame = Frame(self.master)
        self.chatFrame.pack(side='right', fill='both', expand=True)

        # TabFrame new message area
        self.tabTopBar = Frame(self.tabFrame)
        self.tabTopBar.config(bg="#ededed")

        # Configure Frames
        self.topFrameChat = Frame(self.chatFrame)
        self.topFrameChat.pack(fill='both', expand=True)

        self.middleFrameChat = Frame(self.chatFrame)
        self.middleFrameChat.pack(fill='both', expand=True)

        self.bottomFrameChat = Frame(self.chatFrame)
        self.bottomFrameChat.pack(fill='both', expand=True)

        # Place Widgets
        self.createWidgets()

        # now we can add the partner(s) into ListBox3
        self.addPartners()

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
        self.tabTopBar.rowconfigure(1, weight=1)
        self.tabTopBar.columnconfigure(1, weight=1)

        # Placement
        self.username_label.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.listBox1.grid(row=1, column=0, sticky="nsew")
        self.listBox2.grid(row=1, column=1, sticky="nsew")
        self.text_field.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.send_button.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.update_button.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.tabTopBar.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.create_Button.grid(row=0, column=1, sticky="ew")
        self.join_Button.grid(row=0, column=2, sticky="ew")
        self.listBox3.grid(row=1, column=0, sticky="nsew")

    def createWidgets(self):
        print("connected as: \"" + self.username + "\"")
        # window title: shows by what username you are connected to the application
        self.master.title("BAC net  -  " + self.username.upper())

        # Chat: title bar: shows to who you are currently writing
        self.username_label = Label(self.topFrameChat, text="")
        self.username_label.configure(bg="#ededed", font=('HelveticaNeue', 14))

        # Chat: chatfield
        self.scrollbar = Scrollbar(self.middleFrameChat, orient="vertical")
        self.scrollbar.config(command=self.yview)

        self.listBox1 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll1)
        self.listBox1.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))
        self.listBox1.bind("<<ListboxSelect>>", lambda x: self.open_file1())

        self.listBox2 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll2)
        self.listBox2.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))
        self.listBox2.bind("<<ListboxSelect>>", lambda x: self.open_file2())

        # ---Tab Section---
        self.tabScrollbar = Scrollbar(self.tabFrame, orient="vertical")
        self.listBox3 = Listbox(self.tabFrame, height=23, width=25, yscrollcommand=self.tabScrollbar.set,
                                selectbackground="#ededed")
        self.tabScrollbar.config(command=self.listBox3.yview)
        self.listBox3.configure(bg='white', font=('HelveticaNeue', 15, 'bold'))
        self.listBox3.bind("<<ListboxSelect>>", lambda x: self.loadChat())

        # Chat: actions
        self.text_field = Entry(self.bottomFrameChat, textvariable=self.msg, font=('HelveticaNeue', 10))
        self.text_field.configure(bg='#f0f0f0')
        self.text_field.bind('<Return>', lambda event: self.check_and_save(self.msg.get(), self.partner[1]))
        self.text_field.bind("<Button-1>", lambda event: self.clear_on_entry("text_field"))
        self.send_button = Button(self.bottomFrameChat, text='Send',
                                  command=lambda: self.check_and_save(self.msg.get(), self.partner[1]), bg="#25D366",
                                  activebackground="#21B858", font=('HelveticaNeue', 10))
        self.update_button = Button(self.bottomFrameChat, text='Update', command=lambda: self.loadChat(self.partner),
                                    bg="white", font=('HelveticaNeue', 10))
        self.create_Button = Button(self.tabTopBar, text="   create   ",
                                    command=lambda: self.saveTypeAndSwitchState("create"), bg="#25D366",
                                    activebackground="#21B858", font=('HelveticaNeue', 11))  # green
        self.join_Button = Button(self.tabTopBar, text="           join             ",
                                  command=lambda: self.saveTypeAndSwitchState("join"), bg="#34B7F1",
                                  activebackground="#0f9bd7", font=('HelveticaNeue', 11))  # blue
        self.privateChat_Button = Button(self.tabTopBar, text="Private Chat",
                                         command=lambda: self.saveTypeAndSwitchState("private Chat"), bg="#25D366",
                                         activebackground="#21B858", font=('HelveticaNeue', 11))  # lightgreen
        self.group_Button = Button(self.tabTopBar, text="    Group    ",
                                   command=lambda: self.saveTypeAndSwitchState("group"), bg="#34B7F1",
                                   activebackground="#0f9bd7", font=('HelveticaNeue', 11))  # lightblue

        self.confirm_Button = Button(self.tabTopBar, text="OK", command=lambda: self.saveTypeAndSwitchState("confirm"),
                                     bg="#25D366", activebackground="#21B858", font=('HelveticaNeue', 11))  # green
        self.back_Button = Button(self.tabTopBar, text="back", command=lambda: self.saveTypeAndSwitchState("back"),
                                  bg="white", font=('HelveticaNeue', 11), highlightcolor="white")  # green
        self.button_state = 0
        self.ButtonType = ""
        self.ButtonTask = ""
        self.BackTask = ""

        self.id_field = Entry(self.tabTopBar, textvariable=self.entry_field, state=NORMAL)  # readonly state
        self.id_field.bind("<Button-1>", lambda event: self.clear_on_entry("id_field"))
        self.id_field.bind('<Return>', lambda event: self.switchState())

    # --------- GRAPHICAL HELP FUNCTIONS ----------
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

    def write_dh_object_to_file(self, chatID):
        """ Write a dh-object to the diffie_hellman-file """
        dh = pyDH.DiffieHellman()
        with open(f"diffie_hellman_{chatID}", 'wb') as diffie_file:
            pickle.dump(dh, diffie_file)
            return dh

    def write_shared_private_key(self, partners_pubkey, chatID):
        """ Write a private key to the shared_key-file """
        dh = self.read_dh_object_from_file(chatID)
        shared_key = dh.gen_shared_key(partners_pubkey)
        with open(f"shared_key_{chatID}", 'wb') as shared_key_file:
            pickle.dump(shared_key, shared_key_file)
            return shared_key

    def write_partners_pubkey_to_file(self, pubkey, chatID):
        with open(f"partners_pubkey_{chatID}", 'wb') as partners_pubkey_file:
            pickle.dump(pubkey, partners_pubkey_file)

    def read_dh_object_from_file(self, chatID):
        """ Read the dh-object from the diffie_hellman-file """
        with open(f"diffie_hellman_{chatID}", 'rb') as diffie_file:
            dh = pickle.load(diffie_file)
            return dh

    def read_shared_key_from_file(self, chatID):
        """ Read the private key from the shared_key-file """
        with open(f"shared_key_{chatID}", 'rb') as shared_key_file:
            shared_key = pickle.load(shared_key_file)
            return shared_key

    def read_partners_public_key(self, chatID):
        """ Read the public key of the correspondent from file"""
        if os.path.isfile(f"partners_pubkey_{chatID}"):
            with open(f"partners_pubkey_{chatID}", 'rb') as partners_pubkey_file:
                return pickle.load(partners_pubkey_file)
        else:
            return 0

    def write_message_to_file(self, encrypted_message, chatID, timestamp, username, message_flag):
        """ Write the encrypted messages to a file"""
        timestamp = datetime.datetime.fromtimestamp(timestamp)
        timestamp_string = timestamp.strftime("%H:%M %d.%m.%Y")
        if not os.path.isfile(f"stored_messages_{chatID}.json"):  # create the file if it doesn't exist
            with open(f"stored_messages_{chatID}.json", 'w') as messages_file:
                self.messages = ["initial"]
                json.dump(self.messages, messages_file)

        self.stored_messages += 1
        with open(f"stored_messages_{chatID}.json", "r+") as stored_messages_file:
            self.messages = json.load(stored_messages_file)
            if self.messages[0] == "initial":
                self.messages = [(username, encrypted_message, timestamp_string, message_flag)]
                stored_messages_file.seek(0)
                json.dump(self.messages, stored_messages_file)
            else:
                self.messages.append((username, encrypted_message, timestamp_string, message_flag))
                stored_messages_file.seek(0)
                json.dump(self.messages, stored_messages_file)

    def read_messages_from_file(self, chatID):
        """ Read the encrypted messages from file """
        if os.path.isfile(f"stored_messages_{chatID}.json"):
            with open(f"stored_messages_{chatID}.json", 'r') as stored_messages_file:
                self.messages = json.load(stored_messages_file)

    def write_is_initiator(self, chatID):
        """ Write to file whether or not the user is the initiator of the conversation """
        with open(f"initiator_{chatID}", 'wb') as initiator_file:
            pickle.dump(self.is_initiator, initiator_file)

    def read_is_initiator(self, chatID):
        """ Read whether or not the user is the initiator of the conversation (True or False) """
        with open(f"initiator_{chatID}", 'rb') as initiator_file:
            self.is_initiator = pickle.load(initiator_file)

    def add(self, chatID):
        """ Responsible for handling the receiving part of the chat functionality
        Users always receive their own message as well."""

        # our attempt to cryptographically secure the groupchat-functionality
        # if chat_type == "group":
        #     self.groupchats.append(chatID)
        #     self.receive_group_messages(chatID)
        # else:
            # ...

        global key

        self.listBox1.delete(0, 'end')
        self.listBox2.delete(0, 'end')

        self.time = datetime.datetime.now()

        chat = self.chat_function.get_full_chat(chatID)
        chat_type = chat[0][0].split("#split:#")[3]  # get the type of the chat (private or group)

        # We only want to loop through the messages that are not already in the stored_messages_file
        # since we might not have the right private key to decrypt the message
        self.read_messages_from_file(chatID)  # self.messages reads the messages that were written to file
        if not os.path.isfile(f"shared_key_{chatID}") and len(chat) > 1:
            self.chat_messages_index = len(self.messages) + 1
        elif os.path.isfile(f"shared_key_{chatID}"):
            self.chat_messages_index = len(self.messages) + 2

        # decide whether the user is the initiator of the conversation
        if self.username == chat[0][0].split("#split:#")[0]:
            self.is_initiator = True
        else:
            self.is_initiator = False
        self.write_is_initiator(chatID)

        # creating a pubkey if none is available
        if not os.path.isfile(f"diffie_hellman_{chatID}"):
            dh = self.write_dh_object_to_file(chatID)
            self.pubkey = dh.gen_public_key()
        else:
            self.pubkey = self.read_dh_object_from_file(chatID).gen_public_key()

        # loop through all messages that are not already stored in messages-file
        for i in range(self.chat_messages_index, len(chat)):

            chat_message = chat[i][0].split(
                "#split:#")  # a chat-message is like: username#split:#message, so we need to split this two
            partner_username = chat_message[0]  # from who is the message
            message = chat_message[1]  # the real content / message
            message_flag = chat_message[2]
            key_flag = ""
            if len(chat_message) > 3:
                key_flag = chat_message[3]

            is_message_encrypted = False

            # get the key from the file
            if message_flag == "msg" or message_flag == "img":
                is_message_encrypted = True

            # if such a file doesn't exist, then the current message must have sent a key, which is then saved into
            # a file for further usage
            elif (message_flag == "msg" or message_flag == "img" or message_flag == "pdf") and key_flag == "key":
                is_message_encrypted = True

            if key_flag == "key":
                key = b64decode(chat_message[4])

            # if the event is an actual message and therefore is encrypted, the iv and the ciphertext are extracted and
            # the message is decrypted
            if is_message_encrypted:

                if "pubkey" in chat_message:
                    sender_pubkey = int(chat_message[-1])

                    # message is from other user
                    if sender_pubkey != self.pubkey:
                        self.write_partners_pubkey_to_file(sender_pubkey, chatID)
                        if self.is_initiator and not key_flag == "key":
                            self.write_shared_private_key(sender_pubkey, chatID)

                if os.path.isfile(f"shared_key_{chatID}") and not key_flag == "key":
                    shared_key = self.read_shared_key_from_file(chatID)
                    key = shared_key[0:32].encode()

                # separate the received message into the initiation vector and the ciphertext
                message_split = message.split(':')
                iv = b64decode(message_split[0])
                ct = b64decode(message_split[1])

                # decipher the message
                cipher = AES.new(key, AES.MODE_CBC, iv)
                message = unpad(cipher.decrypt(ct), AES.block_size).decode()

                # write the encrypted message to the message-file
                self.write_message_to_file(message, chatID, chat[i][1], partner_username, message_flag)

            # if the message is solely a member-message
            if len(chat_message) == 4:
                if chat_type == "private" and self.partner[0] == self.partner[1] and message_flag == "member":
                    for ind in range(len(self.person_list)):
                        if self.partner[1] == self.person_list[ind][1]:
                            self.person_list[ind][
                                0] = partner_username  # the creator of the group gets the name of his partner for the first time
                            self.partner[0] = partner_username
                            self.username_label.config(text=TextWrapper.shorten_name(self.partner[0], 34))
                continue

        self.print_messages_to_ui(chat_type)
        self.chat_messages_index = self.stored_messages + 2 if os.path.isfile(f"shared_key_{chatID}") else 1

    # def receive_group_messages(self, chatID):
    #
    #     global key
    #
    #     self.listBox1.delete(0, 'end')
    #     self.listBox2.delete(0, 'end')
    #
    #     self.time = datetime.datetime.now()
    #
    #     chat = self.chat_function.get_full_chat(chatID)
    #     chat_type = chat[0][0].split("#split:#")[3]  # get the type of the chat (private or group)
    #
    #     # We only want to loop through the messages that are not already in the stored_messages_file
    #     # since we might not have the right private key to decrypt the message
    #     self.read_messages_from_file(chatID)  # self.messages reads the messages that were written to file
    #     if not os.path.isfile(f"shared_key_{chatID}") and len(chat) > 1:
    #         self.chat_messages_index = len(self.messages) + 1
    #     elif os.path.isfile(f"shared_key_{chatID}"):
    #         self.chat_messages_index = len(self.messages) + 2
    #
    #     if self.username == chat[0][0].split("#split:#")[0]:
    #         self.is_initiator = True
    #     else:
    #         self.is_initiator = False
    #     self.write_is_initiator(chatID)
    #
    #     if not os.path.isfile(f"diffie_hellman_{chatID}"):
    #         dh = self.write_dh_object_to_file(chatID)
    #         self.pubkey = dh.gen_public_key()
    #     else:
    #         dh = self.read_dh_object_from_file(chatID)
    #         self.pubkey = dh.gen_public_key()
    #
    #     print(self.pubkey)
    #
    #     for i in range(self.chat_messages_index, len(chat)):
    #
    #         chat_message = chat[i][0].split(
    #             "#split:#")  # a chat-message is like: username#split:#message, so we need to split this two
    #         partner_username = chat_message[0]  # from who is the message
    #         message = chat_message[1]  # the real content / message
    #         message_flag = chat_message[2]
    #         key_flag = ""
    #         if len(chat_message) > 3:
    #             key_flag = chat_message[3]
    #
    #         is_message_encrypted = False
    #
    #         # get the key from the file
    #         if message_flag == "msg" or message_flag == "img":
    #             is_message_encrypted = True
    #
    #         # if such a file doesn't exist, then the current message must have sent a key, which is then saved into
    #         # a file for further usage
    #         elif (message_flag == "msg" or message_flag == "img" or message_flag == "pdf") and key_flag == "key":
    #             is_message_encrypted = True
    #
    #         if key_flag == "key":
    #             key = b64decode(chat_message[4])
    #
    #         # if the event is an actual message and therefore is encrypted, the iv and the ciphertext are extracted and
    #         # the message is decrypted
    #         if is_message_encrypted:
    #
    #             if partner_username == self.username:
    #                 if self.pubkey_dict:
    #                     message_written_to_file = False
    #                     for pubkey in self.pubkey_dict:
    #
    #                         shared_key = dh.gen_shared_key(pubkey)
    #                         key = shared_key[0:32].encode()
    #
    #                         # separate the received message into the initiation vector and the ciphertext
    #                         message_split = message.split(':')
    #                         iv = b64decode(message_split[0])
    #                         ct = b64decode(message_split[1])
    #
    #                         cipher = AES.new(key, AES.MODE_CBC, iv)
    #                         message = unpad(cipher.decrypt(ct), AES.block_size).decode()
    #
    #                         if not message_written_to_file:
    #                             self.write_message_to_file(message, chatID, chat[i][1], partner_username, message_flag)
    #                             message_written_to_file = True
    #                 else:
    #                     # separate the received message into the initiation vector and the ciphertext
    #                     message_split = message.split(':')
    #                     iv = b64decode(message_split[0])
    #                     ct = b64decode(message_split[1])
    #
    #                     cipher = AES.new(key, AES.MODE_CBC, iv)
    #                     message = unpad(cipher.decrypt(ct), AES.block_size).decode()
    #
    #                     self.write_message_to_file(message, chatID, chat[i][1], partner_username, message_flag)
    #
    #             else:
    #                 if partner_username in self.pubkey_dict:
    #                     if "pubkey" in chat_message:
    #                         sender_pubkey = int(chat_message[-1])
    #                         self.pubkey_dict[partner_username] = sender_pubkey
    #                     shared_key = dh.gen_shared_key(self.pubkey_dict[partner_username])
    #                     key = shared_key[0:32].encode()
    #
    #                 # separate the received message into the initiation vector and the ciphertext
    #                 message_split = message.split(':')
    #                 iv = b64decode(message_split[0])
    #                 ct = b64decode(message_split[1])
    #
    #                 cipher = AES.new(key, AES.MODE_CBC, iv)
    #                 message = unpad(cipher.decrypt(ct), AES.block_size).decode()
    #
    #                 self.write_message_to_file(message, chatID, chat[i][1], partner_username, message_flag)
    #
    #         if len(chat_message) == 4:
    #             if chat_type == "private" and self.partner[0] == self.partner[1] and message_flag == "member":
    #                 for ind in range(len(self.person_list)):
    #                     if self.partner[1] == self.person_list[ind][1]:
    #                         # the creator of the group gets the name of his partner for the first time
    #                         self.person_list[ind][0] = partner_username
    #                         self.partner[0] = partner_username
    #                         self.username_label.config(text=TextWrapper.shorten_name(self.partner[0], 34))
    #             continue
    #
    #     self.print_messages_to_ui(chat_type)
    #     self.chat_messages_index = self.stored_messages + 2 if os.path.isfile(f"shared_key_{chatID}") else 1

    def updateContent(self, chatID):
        self.add(chatID)
        self.addPartners()

    def print_messages_to_ui(self, chat_type):

        for message in self.messages:
            if message[0] != self.username:  # message from the partner(s)
                # print the message with white background:
                if chat_type == "group":
                    self.listBox1.insert('end', message[0] + ":")
                    try:
                        self.listBox1.itemconfig('end', bg='white',
                                                 foreground=Colorize.name_to_color(message[0]))
                    except:
                        self.listBox1.itemconfig('end', bg='white', foreground='#00a86b')
                    self.listBox2.insert('end', "")

                # message[3] = message_flag --> {"img", "pdf", "msg"}
                if message[3] == "pdf":
                    self.listBox1.insert('end', "Click to open pdf.")
                    self.listBox1.itemconfig('end', bg='white')
                    self.listBox2.insert('end', "")
                elif message[3] == "img":
                    self.listBox1.insert('end', "Click to open image.")
                    self.listBox1.itemconfig('end', bg='white')
                    self.listBox2.insert('end', "")
                else:
                    messages = TextWrapper.textWrap(message[1], 0)
                    for index in range(len(messages)):
                        self.listBox1.insert('end', messages[index])
                        self.listBox1.itemconfig('end', bg='white')
                        self.listBox2.insert('end', '')

                self.listBox1.insert('end', "{:<22}{:>16}".format("", message[2]))
                self.listBox1.itemconfig('end', bg='white', foreground="lightgrey")
                self.listBox2.insert('end', "")

                self.listBox1.yview(END)
                self.listBox2.yview(END)
                self.listBox1.insert('end', '')  # some space to enhance appeal
                self.listBox2.insert('end', '')

            else:  # username = self.username: message from the user
                # print the message with green background:
                if message[3] == "pdf":
                    self.listBox2.insert('end', "Click to open PDF. (" + str(i) + ")")
                    self.listBox2.itemconfig('end', bg='#dafac9')
                    self.listBox1.insert('end', '')
                elif message[3] == "img":
                    self.listBox2.insert('end', "Click to open image. (" + str(i) + ")")
                    self.listBox2.itemconfig('end', bg='#dafac9')
                    self.listBox1.insert('end', '')
                else:  # == msg
                    messages = TextWrapper.textWrap(message[1], 0)
                    for i in range(len(messages)):
                        self.listBox2.insert('end', messages[i])
                        self.listBox2.itemconfig('end', bg='#dafac9')
                        self.listBox1.insert('end', '')

                self.listBox2.insert('end', "{:<22}{:>16}".format("", message[2]))
                self.listBox2.itemconfig('end', bg='#dafac9', foreground="lightgrey")
                self.listBox1.insert('end', '')

                self.listBox2.yview(END)
                self.listBox1.yview(END)
                self.listBox2.insert('end', '')  # some space to enhance appeal
                self.listBox1.insert('end', '')

    def loadChat(self, chat=None):  # when the user clicks on Person in listBox3 this function is called and loads
        # the correct chat and sets up everything needed to start the communication
        if not chat:
            try:
                selection = self.listBox3.curselection()[0]  # this gives an int value: first element = 0
            except IndexError:
                return

            if selection or selection == 0:  # if something is selected
                self.partner[0] = self.person_list[int(selection)][0]
                self.partner[1] = self.person_list[int(selection)][1]
        else:
            if self.partner[0] != chat[0]:
                self.partner[0] = chat[0]
                self.partner[1] = chat[1]

        for i in range(len(self.person_list)):
            if self.person_list[i][1] == self.partner[1]:
                self.person_list[i][2] = time.time()

        chat_type = self.chat_function.get_full_chat(self.partner[1])[0][0].split("#split:#")[
            3]  # get the type of the chat (private or group)

        if chat_type == "private":
            self.username_label.config(text=TextWrapper.shorten_name(self.partner[0], 34))
        else:  # chat_type == "group"
            self.username_label.config(
                text=TextWrapper.shorten_name(self.partner[0], 27) + " (" + self.partner[1] + ")")

        self.updateContent(self.partner[1])

    def check_for_new_messages(self, person_nr):
        length = len(self.chat_function.get_chat_since(self.person_list[person_nr][2], self.person_list[person_nr][1]))
        unread_messages = length - self.count_users_in_chat(self.person_list[person_nr][1],
                                                            self.person_list[person_nr][2])
        return unread_messages

    def addPartners(self):
        if len(self.person_list) != 0:
            self.listBox3.delete(0, 'end')
            self.person_list.sort(key=lambda x: self.chat_function.get_full_chat(x[1])[-1][1], reverse=True)

            for i in range(len(self.person_list)):
                counter = self.check_for_new_messages(i)
                if self.partner[1] == self.person_list[i][1]:
                    counter = 0

                self.listBox3.insert('end', TextWrapper.mergeNameCounter(self.person_list[i][0], counter))

                if counter != 0:
                    self.listBox3.itemconfig(i, bg='#dfd')
                else:
                    self.listBox3.itemconfig(i, bg="white")

    def saveTypeAndSwitchState(self, Type):
        if Type == 'back':
            self.BackTask = Type
            # self.button_state = (self.button_state - 1) % 3
        elif self.button_state == 0:  # Type is 'create' or 'join':
            self.ButtonType = Type
            if Type == 'join':
                self.privateChat_Button.grid_remove()
                self.group_Button.grid_remove()
                self.join_Button.grid_remove()
                self.id_field.insert(0, "Enter ID here")
                self.confirm_Button.grid(row=0, column=1, sticky="ew")
                self.id_field.grid(row=0, column=0, sticky="ew")
                self.id_field.delete(0, END)
                self.ButtonTask == ""
                self.back_Button.grid(row=0, column=3, sticky="e")
                self.button_state = 2
        elif self.button_state == 1:  # Type is 'private Chat' or 'group':
            self.ButtonTask = Type
        elif self.button_state == 2:
            self.switchState(Type)
            return
        self.switchState()

    def switchState(self, Type=None):  # creates a menu like behaviour of the buttons
        # STATE = 0
        if self.button_state == 0:  # after first click (we now know the Button Type ('create' or 'join'))
            self.create_Button.grid_remove()
            self.join_Button.grid_remove()
            self.privateChat_Button.grid(row=0, column=1, sticky="ew")
            self.group_Button.grid(row=0, column=2, sticky="ew")
            self.back_Button.grid(row=0, column=3, sticky="e")  # add back button for second state

            self.button_state = 1  # only advance by one state when back button was not activated

        # STATE = 1
        elif self.button_state == 1:  # after second click  (we now know the Button Task ('private Chat' or 'group'))
            if self.BackTask != 'back':
                self.privateChat_Button.grid_remove()
                self.group_Button.grid_remove()
                self.confirm_Button.grid(row=0, column=1, sticky="ew")
                self.id_field.grid(row=0, column=0, sticky="ew")
                self.id_field.delete(0, END)
                if self.ButtonTask == 'group' and self.ButtonType == 'create':
                    self.id_field.insert(0, "Enter Group name here")
                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'create':
                    self.id_field.config(state='readonly')
                    self.entry_field.set(self.generate_ID())

                self.button_state = 2  # only advance by one state when back button was not activated

            else:  # we need to reset by one state
                self.BackTask = ""
                self.ButtonType = ""
                self.privateChat_Button.grid_remove()
                self.group_Button.grid_remove()
                self.back_Button.grid_remove()
                self.create_Button.grid(row=0, column=1, sticky="nsew")
                self.join_Button.grid(row=0, column=3, sticky="nsew")

                self.button_state = 0

        # STATE = 2
        else:  # self.button_state == 2: #after third click (reset to state = 0)
            error_type = 'None'
            if self.BackTask != 'back':
                if self.ButtonType == 'join':
                    if self.is_joinable(self.id_field.get()):
                        self.join_chat(self.id_field.get())
                    elif Type == 'confirm':
                        self.id_field.delete(0, END)
                        error_type = "try again: enter ID"
                    else:
                        self.id_field.delete(0, END)
                        error_type = "enter ID here"
                elif self.ButtonTask == 'group' and self.ButtonType == 'create':
                    if len(self.id_field.get()) <= 16 and self.id_field.get() != "" and self.id_field.get() != " ":
                        self.create_chat(self.generate_ID(), self.id_field.get())
                    else:
                        error_type = "Name must be < 17"

                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'create':
                    self.create_chat(self.id_field.get())

                if error_type == 'None':
                    self.BackTask = ""
                    self.ButtonType = ""
                    self.id_field.grid_remove()
                    self.confirm_Button.grid_remove()
                    self.id_field.config(state=NORMAL)
                    self.back_Button.grid_remove()

                    self.create_Button.grid(row=0, column=1, sticky="ew")
                    self.join_Button.grid(row=0, column=2, sticky="ew")

                    self.button_state = 0  # only advance by one state when back button was not activated

                else:  # 'error' occured
                    self.id_field.delete(0, END)
                    self.id_field.insert(0, error_type)
                    error_type = 'None'

            else:  # we need to reset by one state
                self.BackTask = ""
                self.id_field.delete(0, END)
                self.id_field.grid_remove()
                self.id_field.config(state=NORMAL)
                self.confirm_Button.grid_remove()

                if self.ButtonTask == 'group' or self.ButtonTask == 'private Chat':
                    self.ButtonTask = ""
                    self.privateChat_Button.grid(row=0, column=1, sticky="ew")
                    self.group_Button.grid(row=0, column=2, sticky="ew")
                    self.button_state = 1
                else:  # join was previously selected
                    self.ButtonTask = ""
                    self.back_Button.grid_remove()
                    self.create_Button.grid(row=0, column=1, sticky="ew")
                    self.join_Button.grid(row=0, column=2, sticky="ew")
                    self.button_state = 0
        if self.partner[1] != "":
            self.loadChat(self.partner)

    def clear_on_entry(self, field):
        if field == 'id_field':
            if self.id_field.get() == "Enter Group ID here" or self.id_field.get() == "try again: enter ID" or self.id_field.get() == "Name must be < 17" or self.id_field.get() == "enter ID here" or self.id_field.get() == "Enter Group name here":
                self.id_field.delete(0, 'end')
        elif field == 'text_field':
            if self.text_field.get() == "Sorry, given path could not be loaded, please try again!" or self.text_field.get() == "Sorry, file must not be < 100 KB" or self.text_field.get() == "Sorry, file does not exist, please try again!" or self.text_field.get() == "Sorry, given path does not exist, please try again!":
                self.text_field.delete(0, 'end')
        if self.partner[1] != "":
            self.loadChat(self.partner)

    # -------------- -------------- --------------

    # -------------- HELP FUNCTIONS --------------

    def check_and_save(self, message, chat_id):
        if self.partner[1] != "":
            count = 0  # check if the message consists of only spaces
            for i in range(len(message)):
                if message[
                    i] != " " and count == 0:  # check how many chars are not spaces. if we found one that is not a space, we can continue
                    count += 1

            if message == "" or count == 0 or not self.person_list or not self.partner:
                pass

            elif message[0:5] == 'img: ' or message[0:5] == 'pdf: ':
                file_type = message[0:3]
                file_path = message[5:]

                if os.path.isdir(file_path[0:file_path.rfind('/')]):  # check if path is a valid directory
                    if os.path.isfile(file_path):  # check if path has a file
                        file_string = self.encode_file(file_path)
                        file_name = file_path[file_path.rfind('/') + 1:]
                        length = len(file_string)
                        kilobyte = 1000  # a thousand chars fit into one kilobyte
                        if length > 100 * kilobyte:  # file too big
                            self.text_field.delete(0, 'end')
                            self.text_field.insert(0, "Sorry, file must not be > 100 KB")
                        elif length > kilobyte:  # if more than one KiloByte
                            partition_len = int(math.ceil(length / kilobyte))
                            for i in range(partition_len):
                                if i == int(partition_len) - 1:  # We arrived at last part
                                    self.save(file_string[i * kilobyte:] + "#split:#" + file_type + str(
                                        partition_len) + "_" + file_name, chat_id)
                                else:
                                    self.save(file_string[
                                              i * kilobyte:(i + 1) * kilobyte] + "#split:#filepart#split:#filepart",
                                              chat_id)

                        else:  # length <= 1000
                            self.save(file_string + "#split:#" + file_type + file_name, chat_id)
                    else:  # file not found
                        self.text_field.delete(0, 'end')
                        self.text_field.insert(0, "Sorry, file does not exist, please try again!")
                else:  # directory not found
                    self.text_field.delete(0, 'end')
                    self.text_field.insert(0, "Sorry, given path does not exist, please try again!")
            else:  # normal message recognized
                self.save(message + "#split:#msg", chat_id)
        else:
            self.text_field.delete(0, 'end')

    def save(self, message, chatID):
        """ This method is responsible for the sending side of chat-functionality"""

        # our attempt to cryptographically secure the groupchat-functionality
        # if len(self.groupchats) != 0 and chatID in self.groupchats:
        #     self.send_group_messages(message, chatID)
        # else:
            # ...

        send_initial_key = True

        # if there is no pubkey, one will be created
        if not os.path.isfile(f"diffie_hellman_{chatID}"):
            dh = self.write_dh_object_to_file(chatID)
            self.pubkey = dh.gen_public_key()
        else:
            self.pubkey = self.read_dh_object_from_file(chatID).gen_public_key()

        if message.split("#split:#")[1] == "msg" or message.split("#split:#")[1] == "img" or \
                message.split("#split:#")[
                    1] == "pdf":

            generated_key = get_random_bytes(16)

            # if there's no file with the key for the conversation, then the client has started the chat, thereby generates
            # the key and ups the flag telling program to send the key together with the first message
            if not os.path.isfile("key_" + chatID):
                file2write = open("key_" + chatID, 'wb')
                file2write.write(generated_key)
                file2write.close()

                send_initial_key = True

            to_be_encrypted = message.split("#split:#")[0]

            message_bytes = bytes(to_be_encrypted, 'utf-8')

            # if a shared private key exists
            if os.path.isfile(f"shared_key_{chatID}"):
                # if this sender is not the initiator we need to generate a new public key in order to create a new
                self.read_is_initiator(chatID)
                self.partners_pubkey = self.read_partners_public_key(chatID)
                if not self.is_initiator and self.send_pubkey:
                    dh = self.write_dh_object_to_file(chatID)
                    self.pubkey = dh.gen_public_key()
                    self.write_shared_private_key(self.partners_pubkey, chatID)

                shared_key = self.read_shared_key_from_file(chatID)
                generated_key = bytes(shared_key[0:32], 'utf-8')
                send_initial_key = False
            else:
                # if there is a partner_pubkey, we know at least 1 pair of messages was exchanged
                self.partners_pubkey = self.read_partners_public_key(chatID)
                if self.partners_pubkey != 0:
                    self.write_shared_private_key(self.partners_pubkey, chatID)
                    shared_key = self.read_shared_key_from_file(chatID)
                    generated_key = bytes(shared_key[0:32], 'utf-8')
                    send_initial_key = False

            cipher = AES.new(generated_key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(message_bytes, AES.block_size))

            # the initiation vector and the ciphertext message are concatenated and separated with a semicolon
            encrypted = b64encode(cipher.iv).decode('utf-8') + ":" + b64encode(ct_bytes).decode('utf-8')

            # all put back into the required format
            message = encrypted + message[len(message.split("#split:#")[0]):]

            # if this flag is raised, then the message is the first message of the conversation and thereby sends the
            # key which is henceforth used as the symmetric session key
            if send_initial_key:
                if self.send_pubkey:
                    message_pubkey = "#split:#pubkey#split:#" + str(self.pubkey)
                    message = message + "#split:#key#split:#" + b64encode(generated_key).decode(
                        'utf-8') + message_pubkey
                else:
                    message = message + "#split:#key#split:#" + b64encode(generated_key).decode('utf-8')
            else:
                if self.send_pubkey:
                    if os.path.isfile(f"initiator_{chatID}"):
                        self.read_is_initiator(chatID)
                        if self.is_initiator:
                            self.pubkey = self.write_dh_object_to_file(chatID).gen_public_key()

                    message = message + "#split:#pubkey#split:#" + str(self.pubkey)

            self.send_pubkey = False

        to_save = self.username + "#split:#" + message

        new_event = self.ecf.next_event('chat/saveMessage',
                                        {'messagekey': to_save, 'chat_id': chatID, 'timestampkey': time.time()})
        self.chat_function.insert_chat_msg(new_event)

        if self.partner[1] != "":
            self.loadChat(self.partner)  # updating chat, so the send message is also added in the listbox
        self.text_field.delete(0, 'end')

    # def send_group_messages(self, message, chatID):
    #
    #     send_initial_key = True
    #
    #     if not os.path.isfile(f"diffie_hellman_{chatID}"):
    #         dh = self.write_dh_object_to_file(chatID)
    #         self.pubkey = dh.gen_public_key()
    #     else:
    #         dh = self.read_dh_object_from_file(chatID)
    #         self.pubkey = self.read_dh_object_from_file(chatID).gen_public_key()
    #
    #     if message.split("#split:#")[1] == "msg" or message.split("#split:#")[1] == "img" or \
    #             message.split("#split:#")[
    #                 1] == "pdf":
    #
    #         generated_key = get_random_bytes(16)
    #
    #         # if there's no file with the key for the conversation, then the client has started the chat, thereby generates
    #         # the key and ups the flag telling program to send the key together with the first message
    #         if not os.path.isfile("key_" + chatID):
    #             file2write = open("key_" + chatID, 'wb')
    #             file2write.write(generated_key)
    #             file2write.close()
    #
    #             send_initial_key = True
    #
    #         to_be_encrypted = message.split("#split:#")[0]
    #
    #         message_bytes = bytes(to_be_encrypted, 'utf-8')
    #
    #         if self.pubkey_dict:
    #             if self.generate_new_pubkey:
    #                 dh = self.write_dh_object_to_file(chatID)
    #                 self.pubkey = dh.gen_public_key()
    #                 self.generate_new_pubkey = False
    #
    #             for partner_pubkey in self.pubkey_dict:
    #                 shared_key = dh.gen_shared_key(partner_pubkey)
    #                 generated_key = bytes(shared_key[0:32], 'utf-8')
    #                 send_initial_key = False
    #
    #                 cipher = AES.new(generated_key, AES.MODE_CBC)
    #                 ct_bytes = cipher.encrypt(pad(message_bytes, AES.block_size))
    #
    #                 # the initiation vector and the ciphertext message are concatenated and separated with a semicolon
    #                 encrypted = b64encode(cipher.iv).decode('utf-8') + ":" + b64encode(ct_bytes).decode('utf-8')
    #
    #                 # all put back into the required format
    #                 message = encrypted + message[len(message.split("#split:#")[0]):]
    #
    #                 # if this flag is raised, then the message is the first message of the conversation and thereby sends the
    #                 # key which is henceforth used as the symmetric session key
    #                 if send_initial_key:
    #                     if self.send_pubkey:
    #                         message_pubkey = "#split:#pubkey#split:#" + str(self.pubkey)
    #                         message = message + "#split:#key#split:#" + b64encode(generated_key).decode(
    #                             'utf-8') + message_pubkey
    #                     else:
    #                         message = message + "#split:#key#split:#" + b64encode(generated_key).decode('utf-8')
    #                 else:
    #                     if self.send_pubkey:
    #                         if os.path.isfile(f"initiator_{chatID}"):
    #                             self.read_is_initiator(chatID)
    #                             if self.is_initiator:
    #                                 self.pubkey = self.write_dh_object_to_file(chatID).gen_public_key()
    #
    #                         message = message + "#split:#pubkey#split:#" + str(self.pubkey)
    #
    #                 self.send_pubkey = False
    #
    #                 to_save = self.username + "#split:#" + message
    #
    #                 new_event = self.ecf.next_event('chat/saveMessage',
    #                                                 {'messagekey': to_save, 'chat_id': chatID, 'timestampkey': time.time()})
    #                 self.chat_function.insert_chat_msg(new_event)
    #
    #                 if self.partner[1] != "":
    #                     self.loadChat(self.partner)  # updating chat, so the send message is also added in the listbox
    #                 self.text_field.delete(0, 'end')
    #         else:
    #             cipher = AES.new(generated_key, AES.MODE_CBC)
    #             ct_bytes = cipher.encrypt(pad(message_bytes, AES.block_size))
    #
    #             # the initiation vector and the ciphertext message are concatenated and separated with a semicolon
    #             encrypted = b64encode(cipher.iv).decode('utf-8') + ":" + b64encode(ct_bytes).decode('utf-8')
    #
    #             # all put back into the required format
    #             message = encrypted + message[len(message.split("#split:#")[0]):]
    #
    #             # if this flag is raised, then the message is the first message of the conversation and thereby sends the
    #             # key which is henceforth used as the symmetric session key
    #             if send_initial_key:
    #                 if self.send_pubkey:
    #                     message_pubkey = "#split:#pubkey#split:#" + str(self.pubkey)
    #                     message = message + "#split:#key#split:#" + b64encode(generated_key).decode(
    #                         'utf-8') + message_pubkey
    #                 else:
    #                     message = message + "#split:#key#split:#" + b64encode(generated_key).decode('utf-8')
    #             else:
    #                 if self.send_pubkey:
    #                     if os.path.isfile(f"initiator_{chatID}"):
    #                         self.read_is_initiator(chatID)
    #                         if self.is_initiator:
    #                             self.pubkey = self.write_dh_object_to_file(chatID).gen_public_key()
    #
    #                     message = message + "#split:#pubkey#split:#" + str(self.pubkey)
    #
    #             self.send_pubkey = False
    #
    #     to_save = self.username + "#split:#" + message
    #
    #     new_event = self.ecf.next_event('chat/saveMessage',
    #                                     {'messagekey': to_save, 'chat_id': chatID, 'timestampkey': time.time()})
    #     self.chat_function.insert_chat_msg(new_event)
    #
    #     if self.partner[1] != "":
    #         self.loadChat(self.partner)  # updating chat, so the send message is also added in the listbox
    #     self.text_field.delete(0, 'end')

    def create_chat(self, ID, name=None):
        if not name:
            self.person_list.append([ID, ID, 0])
            self.partner[0] = ID
            self.partner[1] = ID
            self.save(self.username + "#split:#member#split:#private", ID)
        else:  # group was created
            self.person_list.append([name, ID, 0])  # it's a group so we do know the name
            self.partner[0] = name
            self.partner[1] = ID
            self.save(name + "#split:#member#split:#group", ID)
        self.addPartners()
        self.loadChat(self.partner)

    def join_chat(self, ID):
        if self.is_joinable(ID):
            self.person_list.append([ID, ID, 0])
            partnerName = self.chat_function.get_full_chat(ID)[0][0].split("#split:#")[
                1]  # taking the name of the partner for the frome the first message
            self.person_list[-1][0] = partnerName  # index -1 is the index of the last list-element
            self.partner[0] = partnerName
            self.partner[1] = ID
            self.save(self.username + "#split:#member#split:#chat", ID)
            self.addPartners()
            self.loadChat(self.partner)

    def count_users_in_chat(self, chatID, since=None):
        counter = 0
        if not since:
            chat = self.chat_function.get_full_chat(chatID)
        else:
            chat = self.chat_function.get_chat_since(since, chatID)

        for i in range(len(chat)):
            if len(chat[i][0].split("#split:#")) == 4:
                counter += 1

        return counter

    def is_joinable(self, chatID):
        if len(chatID) != 6:
            return False  # invalid input
        else:
            chat = self.chat_function.get_full_chat(chatID)

            if len(chat) == 0:
                return False  # the chat isn't even created

            if chat[0][0].split("#split:#")[3] == "private" and self.count_users_in_chat(
                    chatID) == 2:  # max. member for private chat: 2
                return False

            for i in range(len(self.person_list)):  # So the person cannot write with himself
                if self.person_list[i][1] == chatID:  # you are already in this chat
                    return False

        return True

    def assemble_file_parts(self, parts):

        assembled_content = ""

        for i in range(len(parts)):
            assembled_content = assembled_content + parts[i]

        return assembled_content

    def open_file1(self):
        global switch
        try:
            selection = self.listBox1.curselection()[0]  # this gives an int value: first element = 0
        except IndexError:
            return

        if selection or selection == 0:

            item = self.listBox1.get(selection)
            if len(item) >= 21 and (item[0:19] == "Click to open PDF. " or item[
                                                                           0:21] == "Click to open image. "):  # the content should be "Click to open the file. (index)"
                index = int(item[item.find("(") + 1:item.find(")")])  # getting the index
                messages = self.chat_function.get_full_chat(self.partner[1])
                part_as_string = messages[index][0].split("#split:#")

                sender_of_file = part_as_string[0]

                content_of_file = list()
                content_of_file.append(part_as_string[1])  # last part

                name_of_file = part_as_string[2]
                counter = int(name_of_file[3:name_of_file.find("_")]) - 1

                while counter != 0:
                    index -= 1
                    part_as_string = messages[index][0].split("#split:#")
                    if len(part_as_string) == 4 and part_as_string[0] == sender_of_file:
                        content_of_file.append(part_as_string[1])
                        counter -= 1

                type_of_file = ""
                if name_of_file[0:3] == "pdf":
                    type_of_file = "pdf"
                elif name_of_file[0:3] == "img":
                    type_of_file = "img"

                content_of_file.reverse()

                assembled_content = self.assemble_file_parts(content_of_file)

                self.open_file(assembled_content, name_of_file[name_of_file.find("_") + 1:], type_of_file)

    def open_file2(self):
        try:
            selection = self.listBox2.curselection()[0]  # this gives an int value: first element = 0
        except IndexError:
            return

        if selection or selection == 0:

            item = self.listBox2.get(selection)
            if len(item) >= 21 and (item[0:19] == "Click to open PDF. " or item[0:21] == "Click to open image. "):
                # the content should be "Click to open the file. (index)"
                index = int(item[item.find("(") + 1:item.find(")")])  # getting the index
                messages = self.chat_function.get_full_chat(self.partner[1])
                part_as_string = messages[index][0].split("#split:#")

                sender_of_file = part_as_string[0]

                content_of_file = list()
                content_of_file.append(part_as_string[1])  # last part

                name_of_file = part_as_string[2]
                counter = int(name_of_file[3:name_of_file.find("_")]) - 1

                while counter != 0:
                    index -= 1
                    part_as_string = messages[index][0].split("#split:#")
                    if len(part_as_string) == 4 and part_as_string[0] == sender_of_file:
                        content_of_file.append(part_as_string[1])
                        counter -= 1

                type_of_file = ""
                if name_of_file[0:3] == "pdf":
                    type_of_file = "pdf"
                elif name_of_file[0:3] == "img":
                    type_of_file = "img"

                content_of_file.reverse()

                assembled_content = self.assemble_file_parts(content_of_file)

                self.open_file(assembled_content, name_of_file[name_of_file.find("_") + 1:], type_of_file)

    @staticmethod
    def generate_ID():  # generates a secure random id
        ID = list(''.join(
            random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in
            range(6)))
        for i in range(len(ID)):
            if ID[i] == 'I' or ID[i] == 'l':  # to increase readibility we do not allow I
                # and l since they aren't differentiatable in out chosen Font
                ID[i] = str(random.randint(0, 9))
        return (''.join(ID))

    @staticmethod
    def encode_file(file_path):
        # Encode File (to String)
        with open(file_path, "rb") as _file:
            b64encoded_string = base64.b64encode(_file.read())
        file_string = b64encoded_string.decode("utf-8")  # Convert bytes to String
        return file_string

    @staticmethod
    def open_file(content_of_file, name_of_file, type_of_file):
        switch[0] = content_of_file
        switch[1] = name_of_file
        switch[2] = type_of_file
        root2 = Toplevel()
        app2 = DisplayFile(root2)

    # -------------- -------------- --------------


root = Tk()

# Add our BAC net Logo
logo_path = os.path.join(dirname, 'subChat/BAC_net_Logo.png')
name_path = os.path.join(dirname, 'subChat/BAC_net.png')
img = PhotoImage(file=logo_path)
root.iconphoto(True, img)

# Testing
probe = 'no_key'  # by default, there is no key and no name set
try:  # Try to get the key (if it works, then  we can skip the login and go directly to the chat)
    p = pickle.load(open(pickle_file_names[1], "rb"))  # try to load key and name
    probe = 'key_loaded_but_list_not'  # if loading the name didn't throw an error probe is set to 'no_key'
    p = pickle.load(open(pickle_file_names[0], "rb"))  # try to load personList
    probe = 'list_and_name_loaded'  # if loading the personList didn't throw an error probe is set to 'list'    
except:  # we need to login first      
    print("Key has NOT been found: You are redirected to 'Login' to create a User Profile first")
    # test stays 'name' or ""

# Check which case is true to prevent double loading of applications and to make sure everything is set up beforehad
if probe == 'no_key':  # this is only the case when there
    app = Login(master=root)
elif probe == 'key_loaded_but_list_not':  # if the key could be loaded but the list not, we need to assign it first
    List = list()
    pickle.dump(List, open(pickle_file_names[0], "wb"))  # create an empty object
    app = Chat(master=root)  # If there is already an exiting key, we can just login
elif probe == 'list_and_name_loaded':  # when everythingg is already set up, we can just start the Chat window
    app = Chat(master=root)  # If there is already an exiting key, we can just login

# Main Loop:
try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    pass

# Save settings with pickle
pickle.dump(app.person_list, open(pickle_file_names[0], "wb"))  # create an empty object
print("\"personList\" has been saved to \"" + pickle_file_names[0] + "\": personList = ", app.person_list)
