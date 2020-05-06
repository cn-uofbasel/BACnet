try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import feed
import pcap
import datetime
import TextWrapper
# import platform

import os.path
import pyglet  # pip install pyglet

import QuickSort

import SchnittstellenHelper #TODO: delete

# system = platform.system()  # determine platform

# Load Fonts
dirname = os.path.abspath(os.path.dirname(__file__))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeue.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueBd.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueIt.ttf'))


class Login(Frame):

    def open_Chat(self):
        #global app, root
        #root.destroy()  # close old window
        #root = Tk()  # create new Tk
        #root.config(bg="lightgrey")
        #app = Chat(master=root)  # create chat window
        root2 = Toplevel()
        app2 = Chat(root2)

    def chooseUsername(self, name):
        global username
        username = name
        self.open_Chat()

    '''
    def choseUsername(self):  # ToDo: if one wants to choose a custom username
        if not feed.checkKey(self.msg.get() + '.key'):
            feed._appendIt(self.msg.get(), 'create', '')
        if not pcap.checkPcap(self.msg.get()):
            pass
        self.usernameField.delete(0, 'end')
        self.chooseUsername(self.msg.get())
    '''

    def registrationAttempt(self, R_username, R_password):
        print("login Attempt with: \n", R_username, "\n", R_password)
        self.chooseUsername(R_username)
        self.open_Chat()
    '''
        if gruppe07.registrationAttempt(username, password):
            self.chooseUsername(self.msg.get())
            # Eventuell noch eigenes pcap file hier laden falls Gruppe 7 dies nicht macht
            self.open_Chat()
        else:
            self.username_label.text.set("\n\n\nTry Again: Username already taken, please try again.\nchoose Username:")
            self.usernameField.delete(0, 'end')
            self.usernamePassword.delete(0, 'end')
    '''

    def register(self, R_username=None, R_password=None):
        if R_username != "" and R_password != "":
            self.loginAttempt(R_username, R_password)
        else:  # ToDO: depending on how Tunahan implements the Login layout: if it's in one screen, we need to differentiate between login and registration (for the label change at the correct spot) if not, we're good.
            self.username_label.config(text="\nTry Again: Please Enter both Password and Username\nEnter Username:")
            self.usernameField.delete(0, 'end')
            self.usernamePassword.delete(0, 'end')

    def loginAttempt(self, username, password):  # Uncomment when Groupd 7 functions are ready
        print("login Attempt with: \n", username, "\n", password)
        self.chooseUsername(username)
        self.open_Chat()
    '''
        if gruppe07.loginAttempt(username, password):
            self.chooseUsername(self.msg.get())
            # Eventuell noch eigenes pcap file hier laden falls Gruppe 7 dies nicht macht
            self.open_Chat()
        else:
            self.username_label.text.set("\n\n\nTry Again: Wrong Combination of Username and Password.\nEnter Username:")
            self.usernameField.delete(0, 'end')
            self.usernamePassword.delete(0, 'end')
    '''

    def login(self, username=None, password=None):
        if username != "" and password != "":
            self.loginAttempt(username, password)
        else:  # ToDO: depending on how Tunahan implements the Login layout: if it's in one screen, we need to differentiate between login and registration (for the label change at the correct spot) if not, we're good.
            self.username_label.config(text="\nTry Again: Please Enter both Password and Username\nEnter Username:")
            self.usernameField.delete(0, 'end')
            self.usernamePassword.delete(0, 'end')


    def createWidgets(self):
        self.loginFrame = Frame(self.master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.loginFrame.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)

        # -------
        # Buttons /labels (to remove)
        self.username_label = Label(self.loginFrame, text='Choose a username:')
        self.username_label.grid(column=0, row=0, sticky=N + S + E + W)
        self.bob_button = Button(self.loginFrame, text='Bob', command=lambda: self.chooseUsername('bob'))
        self.bob_button.grid(column=0, row=1, sticky=N + S + E + W)
        self.alice_button = Button(self.loginFrame, text='Alice', command=lambda: self.chooseUsername('alice'))
        self.alice_button.grid(column=0, row=2, sticky=N + S + E + W)
        # -------

        # LOGIN:
        # Username
        self.username_label = Label(self.loginFrame, text='\n\n\nEnter Username:')
        self.username_label.grid(column=0, row=3, sticky=N + S + E + W)
        self.usernameField = Entry(self.loginFrame, textvariable=self.username)
        self.usernameField.bind('<Return>', lambda event: self.login(self.username.get(), self.password.get()))
        self.usernameField.grid(column=0, row=4, sticky=N + S + E + W)

        # Password
        self.password_label = Label(self.loginFrame, text='\nEnter Password:')
        self.password_label.grid(column=0, row=5, sticky=N + S + E + W)
        self.usernamePassword = Entry(self.loginFrame, textvariable=self.password)
        self.usernamePassword.bind('<Return>', lambda event: self.login(self.username.get(), self.password.get()))
        self.usernamePassword.grid(column=0, row=6, sticky=N + S + E + W)

        # Button
        self.login_button = Button(self.loginFrame, text='login', command=lambda: self.login(self.username.get(), self.password.get()))
        self.login_button.grid(column=0, row=7, sticky=N + S + E + W)

        # REGISTER
        # Register Username  # --> In separatem Fenster? ToDo: Tunahan
        self.R_username_label = Label(self.loginFrame, text='\n\n\nNot registered yet?\n\nchoose Username:')
        self.R_username_label.grid(column=0, row=8, sticky=N + S + E + W)
        self.R_usernameField = Entry(self.loginFrame, textvariable=self.R_username)
        self.R_usernameField.bind('<Return>', lambda event: self.register(self.R_username.get(), self.R_password.get()))
        self.R_usernameField.grid(column=0, row=9, sticky=N + S + E + W)

        # RegisterPassword
        self.R_password_label = Label(self.loginFrame, text='\nchoose Password:')
        self.R_password_label.grid(column=0, row=10, sticky=N + S + E + W)
        self.R_password = Entry(self.loginFrame, textvariable=self.R_password)
        self.R_password.bind('<Return>', lambda event: self.register(self.R_username.get(), self.R_password.get()))
        self.R_password.grid(column=0, row=11, sticky=N + S + E + W)

        # Button
        self.R_button = Button(self.loginFrame, text='register', command=lambda: self.register(self.R_username.get(), self.R_password.get()))
        self.R_button.grid(column=0, row=12, sticky=N + S + E + W)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Login")
        self.msg = StringVar()
        self.username = StringVar()
        self.password = StringVar()
        self.R_username = StringVar()
        self.R_password = StringVar()
        self.createWidgets()


class Chat(Frame):

    def save(self, content):
        feed._appendIt(self.username, 'append', content)

    def addAll(self, username, content, event=None):
        #try:
        #allMessges = SchnittstellenHelper.returnAll()#gruppe07.returnAll()
        #for i in range(len(allMessges)):
        #    if allMessges[i][2] != self.username: #sender if the content of the current entry at the index of the sender is not myself
        #        pass
        #except:
        self.add(username, content)

    def add(self, username, content, event=None):
        # self.updateContent(self.getPartner())  # instead of an update button, it checks for new incoming messages when/before when you send a new message: currently results in errors (Aborted (core dumped)): seems like an infinite loop
        self.time = datetime.datetime.now()
        # self.lastMessage[chatNumber] = self.time #Update last message sent from this person
        if username != self.username:  # user updated
            try:
                wrappedContent = TextWrapper.textWrap(content, 0)
                print("getting message from " + self.getPartner() + ":")
                self.listBox1.insert('end', '[' + self.time.strftime("%H:%M:%S") + ']')
                self.listBox1.insert('end', wrappedContent[0])
                for i in range(2): self.listBox2.insert('end', "")  # add 2 empty lines to balance both sides
                self.listBox1.itemconfig(self.listBoxItem, bg='white', foreground="lightgrey")
                self.listBox1.itemconfig(self.listBoxItem + 1, bg='white')

                self.listBox1.yview(END)
                self.listBox2.yview(END)
                self.listBox1.insert('end', '')  # some space to enhance appeal
                self.listBox2.insert('end', '')
                self.listBoxItem += 1  # adjust index

                self.listBoxItem += 2  # 2 new items added (update index accordingly)
            except:
                print("no new messages available from " + self.getPartner())
        else:  # user typed something
            lastEntry = ''
            try:
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
                            self.listBox1.insert('end',
                                                 '')  # adjust the other listbox for them to by synced on the same height
                            self.listBox2.itemconfig(self.listBoxItem, bg='#dafac9',
                                                     foreground="lightgrey")  # dafac9 = light green (coloring for sender messaages)
                            self.listBoxItem += 1
                            wrappedContent = TextWrapper.textWrap(content, 0)
                            print(".", wrappedContent)
                            for i in range(len(wrappedContent)):
                                self.listBox2.insert('end', wrappedContent[i])
                                self.listBox1.insert('end', '')  # adjust the other listbox for them to by synced on the same height
                                self.listBox2.itemconfig(self.listBoxItem, bg='#dafac9')
                                self.listBox1.yview(END)
                                self.listBox2.yview(END)

                                self.listBoxItem += 1

                            self.listBox1.yview(END)
                            self.listBox2.yview(END)
                            self.listBox1.insert('end', '')  # some space to enhance appeal
                            self.listBox2.insert('end', '')
                            self.listBoxItem += 1  # adjust index

                            self.text_field.delete(0, 'end')
                            self.save(content)
                        break
            except:
                print("Something went wrong...")  # ToDo: handle this exception by reprinting all of the content
                # exit()

    def updateContent(self, fromUser, chatNumber):
        # ContentArray = pcap.dumpIt(fromUser + '.pcap')
        # print(ContentArray[self.alreadyUpdatedIndex+1])
        while True:
            try:
                print(pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex + 1])
                self.addAll(fromUser, pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex + 1], chatNumber)
                self.alreadyUpdatedIndex += 1
            except:
                print("   No new messages found from: " + self.getPartner())
                break

    def getPartner(self): # get name of current partner
        if self.username == 'alice':
            return 'bob'
        else:
            return 'alice'

    # these methods ensure that when the user scrolls with his mouse instead of the scrollbar, that both list boxes are synced and move at the same time up and down
    def scroll1(self,
                *args):  # when the user scrolls the listBox1, then this method ensures the position of listBox2 is synced
        if self.listBox2.yview() != self.listBox1.yview():  # when the listBox2 is out of sync...
            self.listBox2.yview_moveto(args[0])  # ...adjust the yview of listBox2
        #self.scrollbar.set(*args)  # sync the scrollbar with the mouse wheel position

    def scroll2(self,
                *args):  # when the user scrolls the listBox2, then this method ensures the position of listBox1 is synced
        if self.listBox1.yview() != self.listBox2.yview():  # when the listBox1 is out of sync...
            self.listBox1.yview_moveto(args[0])  # ...adjust the yview of listBox1
        #self.scrollbar.set(*args)  # sync the scrollbar with the mouse wheel position

    def yview(self, *args):  # self configured yview command. the only job is to trigger both sync methods from abouve
        self.listBox1.yview(*args)
        self.listBox2.yview(*args)

    def createWidgets(self):
        print("connected as: \"" + self.username + "\"")
        # window title: shows by what username you are connected to the application
        self.master.title("Subjective Chat: " + self.username.upper())

        # Chat: title bar: shows to who you are currently writing
        self.username_label = Label(self.topFrameChat, text=self.getPartner())
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
        self.chatNumber = 0  # TODO: last input is chatNumber: we need to be able to differentiate between chats and assign numbers to each one of them to somehow acess them. currently there is only 1 chat (=0)
        self.text_field = Entry(self.bottomFrameChat, textvariable=self.msg, font=('HelveticaNeue', 10))
        self.text_field.configure(bg='#f0f0f0')
        self.text_field.bind('<Return>', lambda event: self.addAll(self.username, self.msg.get(), self.chatNumber))
        self.send_button = Button(self.bottomFrameChat, text='Send', command=lambda: self.addAll(self.username, self.msg.get(), self.chatNumber), bg="#25D366", activebackground="#21B858", font=('HelveticaNeue', 10))
        self.update_button = Button(self.bottomFrameChat, text='Update', command=lambda: self.updateContent(self.getPartner(), self.chatNumber), bg="white", font=('HelveticaNeue', 10))  # TODO: getPartner() method is just a temporary fixx
        self.newChatButtonState = 0 #-------------------------
        self.newMessageButton = Button(self.tabTopBar, text = "new Chat", command=lambda: self.switchState(self.newChatButtonState), bg="#25D366") #----------------
        self.newMessageField = Entry(self.tabTopBar, textvariable=self.newMessageAddressant) # ------------------
        self.newMessageField.insert(0,"Enter Recepient here") # ------------------

    def switchState(self, nr): # 0 = new chat , 1 = create chat   # ------------------
        if nr == 0:
            self.newMessageField.grid(row=0, column=0, sticky="ew")
            self.newMessageButton.config(text="create Chat")
            self.newChatButtonState = (self.newChatButtonState + 1) % 2 # switch state between 0 and 1
        if nr == 1:
            self.newMessageField.delete(0, 'end')
            self.newMessageField.insert(0,"Enter Recepient here")
            self.newMessageField.grid_remove()
            self.newMessageField.config(bg="white")
            self.newMessageButton.config(text="new Chat")
            self.newChatButtonState = (self.newChatButtonState + 1) % 2 # switch state between 0 and 1
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
                self.newMessageField.insert(0,"Enter Recepient here")
                self.newMessageField.grid_remove()
                self.newMessageButton.config(text="new Chat")
                self.newChatButtonState = (self.newChatButtonState + 1) % 2 # switch state between 0 and 1
            else: # username not found
                self.newMessageField.insert(0,"Recepient not found...")
                self.newMessageField.config(bg="#ffc2b3")
            '''
    
    def loadChat(self):  # when the user clicks on Person in listBox3 this function is called and loads the correct chat and sets up everything needed to start the communication
        selection = self.listBox3.curselection()[0]
        if self.getPartner != self.personList[selection]:
            item = self.listBox3.get(self.listBox3.curselection()[0])
            person = self.personList[selection]
        # item = self.listBox3.get(self.listBox3.curselection()[0])
        # if item == "":
        #    item = self.listBox3.get(self.listBox3.curselection()[0]-1)  # if empty string is present, return the string before that ToDo: this will ultimately not be an empty string, best case, we 
    

    def addPartners(self):
        self.newMessageCounter = 9  # TODO: this needs to be a dictionary (with the key as partnerName and value as counter) which is automatically updated when new messages arrive thath haven't been read (increase counter)
        self.personList.append(self.getPartner())  # TODO: remove as soon as the personList is implemented and updates automatically
        self.personList.append("bill")
        for i in range(len(self.personList)):
            self.listBox3.insert('end', self.personList[i])  # with counter number TextWrapper.mergeNameCounter(self.personList[i], self.newMessageCounter,45)
            if(self.newMessageCounter != 0):
                self.listBox3.itemconfig(0, bg='#dfd')
            else:
                self.listBox3.itemconfig(0, bg="white")  # TODO: right now there are only two partners so index will always be 0 but this needs to be dynamic
            self.listBox3.insert('end', '')
        for i in range(100):
            self.listBox3.insert('end',i)

    def loadTabPersonList(self):
        #gruppe7.getAllFeedNames()
        #for now, we create a fixed list contining all created pcap files:
        #TODO: this needs to be sorted automatically so the person who wrote the last message will appear first in this list

        FeedList = ["bob","alice","bill"] #TODO: Group chats will be in here as well? if no then they'll be in here and have multiple recepients so we have to filter those out first and add them to a separate list where all group chats are
        GroupChatList = [["bob","alice","bill"]]



    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Subjective Chat")

        # Set Variables
        self.msg = StringVar()
        self.username = username
        self.partner = StringVar()
        #self.dictionary = {"me":0}  # dictionary which gives the index of the personList List when called with a name
        self.personList = list()  # TODO: this is the list which holds all the message partners in descending order (person who las wrote me first). This list needs to be updated automatically when new messages arrive (are updated))
        self.loadTabPersonList()
        self.newMessageAddressant = "" #----------------
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.listBoxItem = 0
        self.lastMessage = list()

        # Configure Application layout
        self.master.configure(height=24, width=50)
        self.tabFrame = Frame(self.master)
        self.tabFrame.pack(side='left', fill = 'both', expand = True)
        self.chatFrame = Frame(self.master)
        self.chatFrame.pack(side='right', fill = 'both', expand = True)

        #TabFrame new message area
        self.tabTopBar = Frame(self.tabFrame)


        # ---Chat Section---
        # Configure Frames
        self.topFrameChat = Frame(self.chatFrame)
        self.topFrameChat.pack(fill = 'both', expand = True)

        self.middleFrameChat = Frame(self.chatFrame)
        self.middleFrameChat.pack(fill = 'both', expand = True)

        self.bottomFrameChat = Frame(self.chatFrame)
        self.bottomFrameChat.pack(fill = 'both', expand = True)

        # Place Widgets
        self.createWidgets()

        self.addPartners()

        # Configure Subframes
        # TODO: try to pack 3 items empty like in the middleFrame and then columnspan = 3: maybe this finally makes the send button fill the whole frame...

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
        #self.scrollbar.grid(column=2, row=1, sticky='ns') #TODO: Frage an Ken: wegloh ?
        self.text_field.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.send_button.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.update_button.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.tabTopBar.grid(row=0, column=0, columnspan=3, sticky="nsew") # ------
        self.newMessageButton.grid(row=0, column=1, sticky="e")  #----------------

root = Tk()
app = Login(master=root)

try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    exit()
    # pass

