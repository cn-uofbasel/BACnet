#Version 15:57

# -------------------------------IMPORT SECTION---------------------------------

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

#-------------
# WHAT YOU NEED TO DO:
#    we haven't implemented an automatic installation of the following 
#    libraries yet so you'll need to install them manually.
#    Here are the commands for Linux:

#prerequisite: # apt install python3-pip
import pickle  # pip install pickle-mixin
import pyglet  # pip install pyglet
from PIL import ImageTk, Image # sudo apt-get install python3-pil python3-pil.imagetk
import base64  # pip install pybase64
#-------------


# Libraries which are included:

import os
import os.path
import sys
import random
import hashlib 
import webbrowser
import secrets
import string
import platform
import time
import datetime

# determine platform
system = platform.system() # currently only supports Linux (works on other platforms but the look and feel is not the same)

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

# Import our (gruppe03) libraries
import TextWrapper
import HexMex

# Import from gruppe04
folderG4 = os.path.join(dirname, '../../04-logMerge/eventCreationTool')
sys.path.append(folderG4)
import EventCreationTool

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../07-logStore/src/logStore')
sys.path.append(folderG7)
from downConnection.DatabaseConnector import DatabaseConnector
from functions.Event import Event, Meta, Content
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from testfixtures import LogCapture
from upConnection.ChatFunction import Chatfunction

# Load Fonts
# Helvetica Neue:
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeue.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueBd.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueIt.ttf'))

# -----------------------------------------------------------------------------

class Login(Frame):

    def open_Chat(self):
        global app, root
        root.destroy()  # close old window
        root = Tk()  # create new Tk
        root.config(bg="lightgrey")
        app = Chat(master=root)  # create chat window
        # root2 = Toplevel()
        # app2 = Chat(root2)

    def register(self, username=None):
        if username != "" and len(username) <= 16:
            private_key = secrets.token_bytes(32)
            self.dictionary = {
                'username': username,
                'private_key': private_key
            }
            pickle.dump(self.dictionary, open(pickle_file_names[1], "wb"))  # save username and key  #TODO: Add "self.username = pickle.load(open("usnam.pkl", "rb"))" to Chat() __init__ to set username
            print("Your username has been saved:", username)

            self.open_Chat()
        else:
            self.usernameField.delete(0, 'end')
            self.usernameField.insert(0, 'Username must be < 17 letters')

    def clear_on_entry(self):
        if self.usernameField.get() == 'Enter your name here' or self.usernameField.get() == 'Username must be < 16 letters':
            self.usernameField.delete(0, 'end')

    def createWidgets(self):
        self.loginFrame = Frame(self.master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # "REGISTER"
        self.username_label = Label(self.loginFrame, text='Here, a key will be created in case \nthere isn\'t one present on your machine\n\n\nchoose a Username:', bg = '#e9fbf0')
        self.usernameField = Entry(self.loginFrame, textvariable=self.R_username)
        self.usernameField.insert(0, "Enter your name here")
        self.usernameField.bind("<Button-1>", lambda event: self.clear_on_entry())
        self.usernameField.bind('<Return>', lambda event: self.register(self.R_username.get()))
        
        # Spacer
        self.spacer1 = Label(self.loginFrame, bg = '#e9fbf0')
        self.spacer2 = Label(self.loginFrame, bg = '#e9fbf0')

        # Button
        self.button = Button(self.loginFrame, text='register', command=lambda: self.register(self.R_username.get()),bg="#25D366", activebackground="#21B858")
        
        # Grid
        self.loginFrame.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)
        self.username_label.grid(column=0, row=1, sticky=N + S + E + W)
        self.usernameField.grid(column=0, row=2, sticky=N + S + E + W)
        self.spacer1.grid(column=0, row=3, sticky=N + S + E + W)
        self.button.grid(column=0, row=4, sticky=N + S + E + W)
        self.spacer2.grid(column=0, row=5, sticky=N + S + E + W)

    def __init__(self, master=None):
        print("Registration started")
        self.R_username = StringVar()
        Frame.__init__(self, master)
        master.title("Login")
        master.config(bg="#e9fbf0")
        self.createWidgets()

class display_file(Frame):
    
    def decode(self):
        pass

    def createWidgets(self):
        print("before but inside widgets")
        global switch      
         
        # Where the files will be saved
        dirname = os.path.abspath(os.path.dirname(__file__))
        image_folder = os.path.join(dirname, 'Images/')
        pdf_folder = os.path.join(dirname, 'Pdfs/')
        try: # try to create a directory
            os.mkdir(image_folder)
            os.mkdir(pdf_folder)
        except FileExistsError: # if this gives an error, then we know the file already exists.
            pass
        
        file_string = self.file
        
        # Convert back from hex String to bytes 
        byte_string = file_string.encode("utf-8") 
    
        # Decode
        decoded_string = base64.b64decode(byte_string)
        
        # Display an image
        if self.file_type == 'img':
            #filename = 'example2.jpg' TODO: suppport multiple formats not just jpg
            filename = str(self.file_name +  "[" + str(datetime.datetime.now())+'].' + self.file_ending) #TODO: make sure it does not save twice
            file_path = os.path.join(image_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded_string)
    
            raw_img = Image.open(file_path)
            render_img = ImageTk.PhotoImage(raw_img)
        
            img = Label(self.frame, image = render_img)
            img.image = render_img
            img.pack(side = "bottom", fill = "both", expand = "yes")
        
        # Display a pdf
        elif self.file_type == 'pdf':
            filename = str(self.file_name + "[" + str(datetime.datetime.now())+'].' + self.file_ending) #TODO: make sure it does not save twice
            file_path = os.path.join(pdf_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded_string)
            webbrowser.open(file_path)
            
        print("after widgets")
        
    def __init__(self, master=None):
        global app
        print("init")
        Frame.__init__(self, master)
        self.master.title("File")
        
        self.master.configure(height=24, width=50)
        self.frame = Frame(self.master)
        self.frame.pack(fill='both', expand=True)
        self.file = switch[0]
        self.file_name = switch[1][0:switch[1].rfind('.')]
        self.file_type = switch[2]
        self.file_ending = switch[1][switch[1].rfind('.')+1:]

        print("before widgets")
        self.createWidgets()
        

class Chat(Frame):

    def check_and_save(self, message, chatID):
        #global switch
        
        # check if the message consists of only spaces
        count = 0
        for i in range(len(message)):
            if message[i] != " " and count == 0: # check how many chars are not spaces. if we found one that is not a space, we can continue
                count  +=1
        #if message == "": #TODO: Remove !
            #message = 'pdf: /home/ken/Desktop/Prototyp/Pdfs/example.pdf'
            #message = 'img: /home/ken/Desktop/Prototyp/Images/example.jpg' #TODO: remove
        if message == "" or count == 0:
            pass #TODO: so isches wie whatrsapp.... oder sölls:   self.text_field.delete(0, 'end')  , mache wenn me Leerschläg sendet?
            
        elif message[0:5] == 'img: ' or message[0:5] == 'pdf: ':
            file_type = message[0:3]
            file_path = message[5:]
            print(file_path)
            print("File recognized:",file_type)
            
            if os.path.isdir(file_path[0:file_path.rfind('/')]): #check if path is a valid directory
                print("-->valid directory")
                if os.path.isfile(file_path): #check if path has a file
                    print("-->file found inside given directory")
                    file_string = self.encode_file(file_path)
                    length = len(file_string)
                    #partitions = ""
                    #if length > 1500:
                    #    partitions = [file_string[i:i+n] for i in range(0, len(file_string), 1500)]
                    #print(partitions)
                        
                    file_name = file_path[file_path.rfind('/')+1:]
                    #switch[1] = file_name  #TODO: remove just for me
                    #switch[2] = message[0:3] #TODO: remove...
                    self.save(file_string+"#split:#"+file_type+file_name, chatID)
                else:
                    print("-->file not found!")
                    self.text_field.delete(0, 'end')
                    self.text_field.insert(0, "Sorry, given path could not be loaded, please try again!")
            else:
                print("-->directory not found!")
                self.text_field.delete(0, 'end')
                self.text_field.insert(0, "Sorry, given path could not be loaded, please try again!")

        else:
            print("normal message recognized")
            self.save(message + "#split:#msg", chatID)
            
    def encode_file(self, file_path):
        #global switch
        print("start of encode")
        # Encode File (to String)
        with open(file_path, "rb") as _file:
            b64encoded_string = base64.b64encode(_file.read())
        file_string = b64encoded_string.decode("utf-8")  # Convert bytes to String
        #switch[0] = file_string  #TODO: Delete
        print("end of encode")
        return file_string
            
    def clear_it_entry(self): #TODO: insert   self.text_field.bind("<Button-1>", lambda event: self.clear_it_entry())   
        if self.text_field.get() == "Sorry, given path could not be loaded, please try again!":
            self.text_field.delete(0, 'end')

    def save(self, message, chatID): 

        toSave = self.username+"#split:#"+message
        
        signing_key = SigningKey(self.feed_id)
        public_key_feed_id = signing_key.verify_key.encode(encoder=HexEncoder)
        content = Content('chat/saveMessage', {'messagekey': toSave, 'chat_id': chatID, 'timestampkey': time.time()})
        hash_of_content = hashlib.sha256(content.get_as_cbor()).hexdigest()
        hash_of_prev = None
        meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
        signature = signing_key.sign(meta.get_as_cbor())._signature
        event = Event(meta, signature, content).get_as_cbor()
        self.chatfunction.insert_chat_msg(event)

        self.loadChat(self.partner) #updating chat, so the send message is also added in the listbox
        self.text_field.delete(0, 'end')
        
    def generate_ID(self):  #generates a secure random id
        ID = list(''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(6)))
        for i in range(len(ID)):
            if ID[i] == 'I' or ID[i] == 'l':  #to increase readibility we do not allow I and l since they aren't differentiatable in out chosen Font
                ID[i] = str(random.randint(0,9))
        return(''.join(ID))

    def add(self, chatID):

        self.listBox1.delete(0, 'end')
        self.listBox2.delete(0, 'end')

        self.time = datetime.datetime.now()
        timezone = 7200 # +2h, so we have the european time in the most simplistic way

        chat = self.chatfunction.get_full_chat('chat', self.feed_id, chatID)

        chat_type = chat[0][0].split("#split:#")[3] #get the type of the chat (private or group)

        for i in range(1, len(chat)):

            chatMessage = chat[i][0].split("#split:#") # a chat-message is like: username#split:#message, so we need to split this two
            username = chatMessage[0] #from who is the message
            message = chatMessage[1] #the real content / message
            additional_msg = chatMessage[2]


            if len(chatMessage) == 4:

                if chat_type == "private" and self.partner[0] == self.partner[1]:
                    for i in range(len(self.personList)):
                        if self.partner[1] == self.personList[i][1]:
                            self.personList[i][0] = username  #the creator of the group gets the name of his partner for the first time
                            self.partner[0] = username
                            self.username_label.config(text=TextWrapper.shorten_name(self.partner[0],34))

            else: # length of message == 3 #TODO: special clause for BILD and PDF_

                if username != self.username: #message from the partner(s)
                    #print the message with white background:

                    if chat_type == "group":
                        self.listBox1.insert('end', username+":")
                        try:
                            self.listBox1.itemconfig('end', bg='white', foreground=HexMex.name_to_color(username))
                        except:
                            self.listBox1.itemconfig('end', bg='white', foreground=HexMex.name_to_color("randomName"))
                        self.listBox2.insert('end', "")
                    
                    if additional_msg[0:3] == "pdf":
                        self.listBox1.insert('end', "Click to open pdf. ("+str(i)+")")
                    elif additional_msg[0:3] == "img":
                        self.listBox1.insert('end', "Click to open image. ("+str(i)+")")
                    else:
                        self.listBox1.insert('end', message)

                    self.listBox1.itemconfig('end', bg='white')
                    self.listBox1.insert('end', "{:<16}{:>16}".format("",time.strftime("%H:%M %d.%m.%Y", time.gmtime(chat[i][1]+timezone))))    
                    self.listBox1.itemconfig('end', bg='white', foreground="lightgrey")
                
                    for i in range(2): self.listBox2.insert('end', "")  # add 2 empty lines to balance both sides
                    self.listBox1.yview(END)
                    self.listBox2.yview(END)
                    self.listBox1.insert('end', '')  # some space to enhance appeal
                    self.listBox2.insert('end', '')

                else: #username = self.username: message from the user
                #print the message with green background:

                    if additional_msg[0:3] == "pdf":
                        self.listBox2.insert('end', "Click to open PDF. ("+str(i)+")")
                    elif additional_msg[0:3] == "img":
                        self.listBox2.insert('end', "Click to open image. ("+str(i)+")")
                    else: # == msg
                        self.listBox2.insert('end', message)

                    self.listBox2.itemconfig('end', bg='#dafac9')
                    self.listBox2.insert('end', "{:<16}{:>16}".format("",time.strftime("%H:%M %d.%m.%Y", time.gmtime(chat[i][1]+timezone))))
                    self.listBox2.itemconfig('end',bg='#dafac9', foreground="lightgrey")

                    for i in range(2): self.listBox1.insert('end', "")  # add 2 empty lines to balance both sides
                    self.listBox2.yview(END)
                    self.listBox1.yview(END)
                    self.listBox2.insert('end', '')  # some space to enhance appeal
                    self.listBox1.insert('end', '')

    def open_file(self, File, Type):
        print("start of open_file")
        root2 = Toplevel()
        app2 = display_file(root2) 
        self.file_name = File #TODO: add variable into __init__ as   self.file_name = ""
        self.file_type = Type   #TODO: same...
        print("end of open_file") 
        
    def updateContent(self, chatID):
        '''
        print("start of updateContend")
        if switch[0] != "":
            print("opening file...")
            #switch[1] = file_name
            for i in range(len(self.personList)):
                if chatID == self.personList[i][1]:
                    partner = self.personList[i][0]
                    switch[3] = partner
            self.open_file(switch[0], switch[2])
            print("passed open_file")
        self.add(chatID)
        self.addPartners()
        print("end of updateContend")
        '''
        self.add(chatID)
        self.addPartners()

    # these methods ensure that when the user scrolls with his mouse instead of the scrollbar, that both list boxes are synced and move at the same time up and down
    def scroll1(self, *args):  # when the user scrolls the listBox1, then this method ensures the position of listBox2 is synced
        if self.listBox2.yview() != self.listBox1.yview():  # when the listBox2 is out of sync...
            self.listBox2.yview_moveto(args[0])  # ...adjust the yview of listBox2
        # self.scrollbar.set(*args)  # sync the scrollbar with the mouse wheel position

    def scroll2(self, *args):  # when the user scrolls the listBox2, then this method ensures the position of listBox1 is synced
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
        self.username_label.configure(bg="#ededed", font=('HelveticaNeue', 14))

        # Chat: chatfield
        self.scrollbar = Scrollbar(self.middleFrameChat, orient="vertical")
        self.scrollbar.config(command=self.yview)

        self.listBox1 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll1)
        self.listBox1.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))
        self.listBox1.bind("<<ListboxSelect>>", lambda x: self.open_file1(self.partner[1]))


        self.listBox2 = Listbox(self.middleFrameChat, height=30, width=25, yscrollcommand=self.scroll2)
        self.listBox2.configure(bg='#e3dbd4', font=('HelveticaNeue', 10))
        self.listBox2.bind("<<ListboxSelect>>", lambda x: self.open_file2(self.partner[1]))

        # ---Tab Section---
        self.tabScrollbar = Scrollbar(self.tabFrame, orient="vertical")
        self.listBox3 = Listbox(self.tabFrame, height=23, width=25, yscrollcommand=self.tabScrollbar.set, selectbackground="#ededed")
        self.tabScrollbar.config(command=self.listBox3.yview)
        self.listBox3.configure(bg='white', font=('HelveticaNeue', 15, 'bold'))
        self.listBox3.bind("<<ListboxSelect>>", lambda x: self.loadChat())

        # Chat: actions
        self.text_field = Entry(self.bottomFrameChat, textvariable=self.msg, font=('HelveticaNeue', 10))
        self.text_field.configure(bg='#f0f0f0')
        self.text_field.bind('<Return>', lambda event: self.check_and_save(self.msg.get(), self.partner[1]))  
        self.text_field.bind("<Button-1>", lambda event: self.clear_it_entry()) 
        self.send_button = Button(self.bottomFrameChat, text='Send', command=lambda: self.check_and_save(self.msg.get(), self.partner[1]), bg="#25D366", activebackground="#21B858", font=('HelveticaNeue', 10))	
        self.update_button = Button(self.bottomFrameChat, text='Update', command=lambda: self.loadChat(self.partner), bg="white", font=('HelveticaNeue', 10))	
        self.create_Button = Button(self.tabTopBar, text="   create   ",command=lambda: self.saveTypeAndSwitchState("create"), bg="#25D366", activebackground="#21B858",  font=('HelveticaNeue', 11)) #green	
        self.join_Button = Button(self.tabTopBar, text="           join             ", command=lambda: self.saveTypeAndSwitchState("join"), bg="#34B7F1", activebackground="#0f9bd7",  font=('HelveticaNeue', 11)) #blue	
        self.privateChat_Button = Button(self.tabTopBar, text="Private Chat", command=lambda: self.saveTypeAndSwitchState("private Chat"), bg="#25D366", activebackground="#21B858",  font=('HelveticaNeue', 11)) #lightgreen	
        self.group_Button = Button(self.tabTopBar, text="    Group    ", command=lambda: self.saveTypeAndSwitchState("group"),  bg="#34B7F1", activebackground="#0f9bd7",  font=('HelveticaNeue', 11)) #lightblue	
        	
        self.confirm_Button = Button(self.tabTopBar, text="OK",command=lambda: self.saveTypeAndSwitchState("confirm"), bg="#25D366", activebackground="#21B858",  font=('HelveticaNeue', 11)) #green	
        self.back_Button = Button(self.tabTopBar, text="back",command=lambda: self.saveTypeAndSwitchState("back"), bg="white",  font=('HelveticaNeue', 11), highlightcolor="white") #green	
        self.button_state = 0	
        self.ButtonType = ""	
        self.ButtonTask = ""	
        self.BackTask = ""	
        	
        self.idField = Entry(self.tabTopBar, textvariable=self.entry_field, state=NORMAL)  # readonly state	
        self.idField.bind("<Button-1>", lambda event: self.clear_on_entry())	
        self.idField.bind('<Return>', lambda event: self.switchState())	

    def clear_on_entry(self):	
        if self.idField.get() == "Enter Group ID here" or self.idField.get() == "Enter Chat ID here" or self.idField.get() == "Enter Group name here" or self.idField.get() == "try again: enter Group ID" or self.idField.get() == "try again: enter Chat ID" or self.idField.get() == "Name must be < 17 letters":	
            self.idField.delete(0, 'end')

    def create_chat(self, ID, name=None):
            
        if not name:
            self.personList.append([ID, ID, 0])
            self.partner[0]=ID
            self.partner[1]=ID
            self.save(self.username+"#split:#created#split:#private", ID)
        else: #group was created
            self.personList.append([name, ID, 0]) # it's a group so we do know the name
            self.partner[0]=name
            self.partner[1]=ID
            self.save(name+"#split:#created#split:#group", ID)
        self.addPartners()
        self.loadChat(self.partner)

    def join_chat(self, ID):
        
        if self.is_joinable(ID):
            self.personList.append([ID, ID, 0])
            partnerName = self.chatfunction.get_full_chat('chat', self.feed_id, ID)[0][0].split("#split:#")[1] # taking the name of the partner for the frome the first message
            self.personList[-1][0] = partnerName #index -1 is the index of the last list-element
            self.partner[0]=partnerName
            self.partner[1]=ID
            self.save(self.username+"#split:#joined#split:#chat", ID)
            self.addPartners()
            self.loadChat(self.partner) #TODO: change when personList-remapping impemented :partner adden wie oben und dann self.partner

    def saveTypeAndSwitchState(self, Type):
        if Type == 'back':
            self.BackTask = Type
            #self.button_state = (self.button_state - 1) % 3 
        elif self.button_state == 0: #Type is 'create' or 'join':
            print("self.ButtonType is set to:", Type)
            self.ButtonType = Type
        elif self.button_state == 1: #Type is 'private Chat' or 'group':
            print("self.ButtonTask is set to:", Type)
            self.ButtonTask = Type

        self.switchState()

    def count_users_in_chat(self, chatID, since=None):
        counter = 0
        if not since:
            chat = self.chatfunction.get_full_chat('chat', self.feed_id, chatID)
        else: 
            chat = self.chatfunction.get_chat_since('chat', since, self.feed_id, chatID)

        for i in range(len(chat)):
            if len(chat[i][0].split("#split:#")) == 4:
                counter += 1

        return counter
        
    def is_joinable(self, chatID):

        if len(chatID) != 6:
            return False # invalid input
        
        else: #[0][0].split("#split:#")
            chat = self.chatfunction.get_full_chat('chat', self.feed_id, chatID)

            if len(chat) == 0: 
                return False # the chat isn't even created
            
            if chat[0][0].split("#split:#")[3] == "private" and self.count_users_in_chat(chatID) == 2: # max. member for private chat: 2
                return False
            
            #TODO: Uncomment:
            '''
            for i in range(len(self.personList)):
                if self.personList[i][1] == chatID: # you are already in this chat
                    return False
            '''

        return True
    
    def switchState(self):  # 0 = new/join , 1 = create/confirm, 2 = reset to normal
        # STATE = 0
        if self.button_state == 0: #after first click (we now know the Button Type ('create' or 'join'))
            self.create_Button.grid_remove()
            self.join_Button.grid_remove()
            self.privateChat_Button.grid(row=0, column=1, sticky="ew")
            self.group_Button.grid(row=0, column=2, sticky="ew")
            self.back_Button.grid(row=0, column=3, sticky="e")  #add back button for second state
                
            self.button_state = (self.button_state + 1) % 3 #only advance by one state when back button was not activated


        # STATE = 1
        elif self.button_state == 1: #after second click  (we now know the Button Task ('private Chat' or 'group'))
            if not self.BackTask:
                self.privateChat_Button.grid_remove()
                self.group_Button.grid_remove()
                self.confirm_Button.grid(row=0, column=1, sticky="ew")
                self.idField.grid(row=0, column=0, sticky="ew")
                self.idField.delete(0, END)
                if self.ButtonTask == 'group' and self.ButtonType == 'join':
                    self.idField.insert(0, "Enter Group ID here")
                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'join':
                    self.idField.insert(0, "Enter Chat ID here")
                elif self.ButtonTask == 'group' and self.ButtonType == 'create':
                    self.idField.insert(0, "Enter Group name here")
                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'create':
                    print(self.ButtonTask, self.ButtonType)
                    self.idField.config(state='readonly') 
                    self.entry_field.set(self.generate_ID())
                
                self.button_state = (self.button_state + 1) % 3  #only advance by one state when back button was not activated
                
            else: # we need to reset by one state
                print("<-- back")
                #print("ButtonTask has been reset")
                self.BackTask = ""
                
                self.privateChat_Button.grid_remove()
                self.group_Button.grid_remove()
                self.back_Button.grid_remove()
                self.create_Button.grid(row=0, column=1, sticky="nsew")
                self.join_Button.grid(row=0, column=3, sticky="nsew")
                
                self.button_state = (self.button_state - 1) % 3


        # STATE = 2
        else:  #self.button_state == 2: #after third click (reset to state = 0)
            if not self.BackTask:
                if self.ButtonTask == 'group' and self.ButtonType == 'join':
                    if self.is_joinable(self.idField.get()) == True:
                        self.join_chat(self.idField.get())
                    else:
                        self.idField.delete(0, END)
                        self.idField.insert(0, "try again: enter Group ID") 
                        return
                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'join':
                    if self.is_joinable(self.idField.get()) == True:
                        self.join_chat(self.idField.get())
                    else:
                        self.idField.delete(0, END)
                        self.idField.insert(0, "try again: enter Chat ID")
                        return
                elif self.ButtonTask == 'group' and self.ButtonType == 'create':
                    if len(self.idField.get()) <=16:	
                        self.create_chat(self.generate_ID(), self.idField.get())	
                    else:	
                        self.idField.delete(0, END)	
                        self.idField.insert(0, "Name must be < 17 letters")
                elif self.ButtonTask == 'private Chat' and self.ButtonType == 'create':
                    #self.entry_field.set(self.generate_ID())
                    self.create_chat(self.idField.get())
                
                self.idField.grid_remove()
                self.confirm_Button.grid_remove()
                self.idField.config(state = NORMAL)
                self.back_Button.grid_remove()
                self.create_Button.grid(row=0, column=1, sticky="ew")
                self.join_Button.grid(row=0, column=2, sticky="ew")
                
                self.button_state = (self.button_state + 1) % 3  #only advance by one state when back button was not activated
                
            else:  # we need to reset by one state
                #self.ButtonType = ""
                #print("ButtonType has been reset")
                self.BackTask = ""
                
                self.idField.delete(0, END)
                self.idField.grid_remove()
                self.confirm_Button.grid_remove()
                
                self.idField.config(state = NORMAL)
                
                self.privateChat_Button.grid(row=0, column=1, sticky="ew")
                self.group_Button.grid(row=0, column=2, sticky="ew")                
                
                self.button_state = (self.button_state - 1) % 3

    def open_file1(self, chatID):
        global switch
        if self.listBox1.curselection()[0] or self.listBox1.curselection()[0] == 0:
            selection = self.listBox1.curselection()[0]  # this gives an int value: first element = 0
        
            item = self.listBox1.get(selection)
            if len(item) >= 21 and (item[0:19] == "Click to open PDF. " or item[0:21] == "Click to open image. "): #the content should be "Click to open the file. (index)"
                index = item[item.find("(")+1:item.find(")")] #getting the index
                file_as_string = self.chatfunction.get_full_chat('chat', self.feed_id, self.partner[1])[int(index)][0].split("#split:#")
                content_of_file = file_as_string[1]
                name_of_file = file_as_string[2]
                
                type_of_file = ""
                if name_of_file[0:3] == "pdf": 
                    type_of_file = "pdf"
                elif name_of_file[0:3] == "img":
                    type_of_file = "img"
                    
                switch[0] = content_of_file 
                switch[1] = name_of_file[3:]
                switch[2] = type_of_file
                self.open_file(content_of_file, type_of_file)
        else:
            print("Nothing was selected, should not get here... (Test)")

    def open_file2(self, chatID):
        if self.listBox2.curselection()[0] or self.listBox2.curselection()[0] == 0:
            selection = self.listBox2.curselection()[0]  # this gives an int value: first element = 0

            item = self.listBox2.get(selection)
            if len(item) >= 21 and (item[0:19] == "Click to open PDF. " or item[0:21] == "Click to open image. "): #the content should be "Click to open the file. (index)"
                index = item[item.find("(")+1:item.find(")")] #getting the index
                file_as_string = self.chatfunction.get_full_chat('chat', self.feed_id, self.partner[1])[int(index)][0].split("#split:#")
                content_of_file = file_as_string[1]
                name_of_file = file_as_string[2]
                
                type_of_file = ""                
                if name_of_file[0:3] == "pdf": 
                    type_of_file = "pdf"
                elif name_of_file[0:3] == "img":
                    type_of_file = "img"
                    
                switch[0] = content_of_file 
                switch[1] = name_of_file[3:]
                switch[2] = type_of_file                    
                self.open_file(content_of_file, type_of_file)
        else:
            print("Nothing was selected, should not get here... (Test)")


    def loadChat(self, chat=None):  # when the user clicks on Person in listBox3 this function is called and loads the correct chat and sets up everything needed to start the communication
        if not chat:
            if self.listBox3.curselection()[0] or self.listBox3.curselection()[0] == 0:
                selection = self.listBox3.curselection()[0]  # this gives an int value: first element = 0  
            else:
                print("Nothing was selected, should not get here... (Test)")
            
            if selection or selection == 0: # if something is selected
                print("Field Nr.",str(selection),"was selected")
                self.partner[0] = self.personList[int(selection)][0]
                self.partner[1] = self.personList[int(selection)][1]
                #TODO: han das uskommentiert zm teste
        else:
            if self.partner[0] != chat[0]:
                self.partner[0] = chat[0]
                self.partner[1] = chat[1]
                
        for i in range(len(self.personList)):
            if self.personList[i][1] == self.partner[1]:
                self.personList[i][2] = time.time()

        chat_type = self.chatfunction.get_full_chat('chat', self.feed_id, self.partner[1])[0][0].split("#split:#")[3] #get the type of the chat (private or group)  
        
        if chat_type == "private":
            self.username_label.config(text=TextWrapper.shorten_name(self.partner[0],34))
        else: #chat_type == "group"
            self.username_label.config(text=TextWrapper.shorten_name(self.partner[0],27)+" ("+self.partner[1]+")")
        
        self.updateContent(self.partner[1])


    def check_for_new_messages(self, person_nr):
        length = len(self.chatfunction.get_chat_since('chat', self.personList[person_nr][2], self.feed_id, self.personList[person_nr][1]))
        unread_messages = length - self.count_users_in_chat(self.personList[person_nr][1], self.personList[person_nr][2])
        return unread_messages

    def get_time_of_last_message(self, chatID):
        return self.chatfunction.get_full_chat('chat', self.feed_id, chatID)[-1][1]

    
    def addPartners(self):
        self.listBox3.delete(0, 'end')
        self.personList.sort(key = lambda x: self.get_time_of_last_message(x[1]), reverse = True)

        for i in range(len(self.personList)):
            counter = self.check_for_new_messages(i)
            if self.partner[1] == self.personList[i][1]:
                counter = 0
            
            self.listBox3.insert('end', TextWrapper.mergeNameCounter(self.personList[i][0], counter, 25))

            if counter != 0:
                self.listBox3.itemconfig(i, bg='#dfd')
            else:
                #print("No new messages in chat",i)
                self.listBox3.itemconfig(i, bg="white")

            #self.listBox3.insert('end', '')   # TODO: hans usegnoh zum teste

        # Opening the first Chat by default
        if len(self.personList) != 0:
            #set the first person as partner:
            if self.partner[0] == "":
                self.loadChat(self.personList[0])
            
        else: # personlist empty or variable partner isn't empty
            self.username_label.config(text="")

    def __init__(self, master=None):
        global username
        Frame.__init__(self, master)
        master.title("Subjective Chat")

        # Set Variables
        self.msg = StringVar()
        self.dictionary = pickle.load(open(pickle_file_names[1], "rb"))
        #print("-->",self.dictionary)
        self.username = self.dictionary['username']
        self.feed_id = self.dictionary['private_key'] 
        #print("-->", self.username)
        self.partner = list() #empty partner as default... tuple: name, chatID
        self.partner.append("")
        self.partner.append("")
        self.entry_field = StringVar()
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.lastMessage = list()
        self.chatfunction = Chatfunction()

        # set self.personList:
        try:  # Try to load the Variable: if it works, we know we can load it and assign it
            x = pickle.load(open(pickle_file_names[0], "rb"))  # if it fails then we know we have not populated our pkl file yet
            self.personList = pickle.load(open(pickle_file_names[0], "rb"))
            #print("Variable sucessfully loaded: personList = ", self.personList)
        except:  # if we can't load the variable, we need to assign and dump it first
            List = list()
            pickle.dump(List, open(pickle_file_names[0], "wb"))  # create an empty object
            self.personList = pickle.load(open(pickle_file_names[0], "rb"))  # loading and setting it now
            print("File didn't exist, I created it for you: personList = ", self.personList)

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
   
root = Tk()
app = None     
pickle_file_names = ['personList.pkl','username.pkl'] #use to reset user or create new one
switch = ["","",""]

# Try to get the key	
try: # we can skip the login and go directly to the chat	
    dictionary = pickle.load(open(pickle_file_names[1], "rb"))  # works only if there is already a file	
    #self.ecf = EventCreationTool.EventFactory()	
    #my_id = ids_list[0]	
    #my_id = dictionary['private_key']	
    #connector = DatabaseConnector()	
    #most_recent_event = connector.get_event(my_id, 0)	
    #print("Most Recent Event: ",most_recent_event)	
    # self.ecf = EventCreationTool.EventFactory(most_recent_event)  # damit wieder gleiche Id benutzt wird	
    app = Chat(master=root)  # If there is already an exiting key, we can just login	

    print("Key has been found: Chat is staring, you are beinng logged in...")	
except:  # we need to login first	
    if not app:
        app = Login(master=root)		
    print("Key has NOT been found: You are redirected to Login to create a User Profile first")		

try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    # exit()
    pass

# Save settings with pickle
pickle.dump(app.personList, open(pickle_file_names[0], "wb"))  # create an empty object
print("\"personList\" has been saved to \"" + pickle_file_names[0] + "\": personList = ", app.personList)
# TODO: save username for automatic login when keyfile is present


