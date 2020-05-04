try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import feed
import pcap
import string
import crypto
import event
import os

import datetime
import TextWrapper
#import platform

import os.path
import pyglet # pip install pyglet

#system = platform.system()  # determine platform

#Load Fonts
dirname = os.path.abspath(os.path.dirname(__file__))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeue.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueBd.ttf'))
pyglet.font.add_file(os.path.join(dirname, 'Font/helveticaneue/HelveticaNeueIt.ttf'))



class Login(Frame):

    def open_Chat(self):
        root2 = Toplevel()
        app2 = Chat(root2)

    def chooseUsername(self, name):
        global username
        username = name
        self.open_Chat()

    def choseUsername(self): # ToDo: if one wants to choose a custom username
        if not feed.checkKey(self.msg.get()+'.key'):
            feed._appendIt(self.msg.get(), 'create', '')
        if not pcap.checkPcap(self.msg.get()):
            pass
        self.text_field.delete(0, 'end')
        self.chooseUsername(self.msg.get())

    def adjust(self, name):
        if name[0] == 'b' or name[0] =='B':
            self.chooseUsername('bob')
        else:
            self.chooseUsername('alice')

    def createWidgets(self):
        self.canvas = Canvas(self.master, width=400, height=300)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)

        self.username_label = Label(self.canvas, text='Choose a username:')
        self.username_label.grid(column=0, row=0, sticky=N + S + E + W)
        self.bob_button = Button(self.canvas, text='Bob', command=lambda: self.chooseUsername('bob'))
        self.bob_button.grid(column=0, row=1, sticky=N + S + E + W)
        self.bob_button = Button(self.canvas, text='Alice', command=lambda: self.chooseUsername('alice'))
        self.bob_button.grid(column=0, row=2, sticky=N + S + E + W)

        self.username_label = Label(self.canvas, text='\nChoose a username manually:')
        self.username_label.grid(column=0, row=3, sticky=N + S + E + W)
        self.text_field = Entry(self.canvas, textvariable=self.msg)
        self.text_field.bind('<Return>', lambda event: self.adjust(self.msg.get()))
        self.text_field.grid(column=0, row=4, sticky=N + S + E + W)
        self.button = Button(self.canvas, text='choose', command=lambda: self.adjust(self.msg.get()))

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Login")
        self.msg = StringVar()
        self.createWidgets()


class Chat(Frame):

    def save(self, contend):
        feed._appendIt(self.username, 'append', contend)

    def add(self, username, contend, chatNumber, event=None):
        #self.updateContend(self.getPartner())  # instead of an update button, it checks for new incoming messages when/before when you send a new message: currently results in errors (Aborted (core dumped)): seems like an infinite loop
        self.time = datetime.datetime.now()
        #self.lastTime[chatNumber] = self.time #Update last message sent from this person
        if username != self.username: # user updated
            try:
                wrappedContend = TextWrapper.textWrap(contend, 0)
                print("getting message from " + self.getPartner() + ":")
                self.listBox1.insert('end', '[' + self.time.strftime("%H:%M:%S") + ']')
                self.listBox1.insert('end', wrappedContend[0])
                for i in range(2): self.listBox2.insert('end',"")  # add 2 empty lines to balance both sides
                self.listBox1.itemconfig(self.listBoxItem, bg ='white', foreground = "lightgrey")
                self.listBox1.itemconfig(self.listBoxItem + 1, bg = 'white')
                
                self.listBox1.yview(END)
                self.listBox2.yview(END)
                self.listBox1.insert('end', '')  #some space to enhance appeal
                self.listBox2.insert('end', '')
                self.listBoxItem += 1 #adjust index
                
                self.listBoxItem += 2  # 2 new items added (update index accordingly)
            except:
                print("no new messages available from " + self.getPartner())
        else: # user typed something
            lastEntry = ''
            try:
                index = 0
                ContendArray = pcap.dumpIt(username + '.pcap')
                while True: # while not at the end of the list (we want to get the last entry)
                    try:
                        lastEntry = ContendArray[index+1]
                        lastEntry = lastEntry[2: len(ContendArray[index+1]) - 2] #removing the [""]
                        index += 1
                    except:
                        print("Arrived at last message: \"" + lastEntry + "\"")
                        if contend != '':
                            self.listBox2.insert('end', '[' + self.time.strftime("%H:%M:%S") + ']')
                            self.listBox1.insert('end', '') # adjust the other listbox for them to by synced on the same height
                            self.listBox2.itemconfig(self.listBoxItem, bg = '#dafac9', foreground = "lightgrey") #dafac9 = light green (coloring for sender messaages)
                            self.listBoxItem += 1
                            wrappedContend = TextWrapper.textWrap(contend, 0)
                            print(".",wrappedContend)
                            for i in range(len(wrappedContend)):
                                self.listBox2.insert('end', wrappedContend[i])
                                self.listBox1.insert('end', '') # adjust the other listbox for them to by synced on the same height
                                self.listBox2.itemconfig(self.listBoxItem, bg = '#dafac9')
                                self.listBox1.yview(END)
                                self.listBox2.yview(END)
                                
                                self.listBoxItem += 1
                            	
                            self.listBox1.yview(END)
                            self.listBox2.yview(END)
                            self.listBox1.insert('end', '')  #some space to enhance appeal
                            self.listBox2.insert('end', '')
                            self.listBoxItem += 1 #adjust index 
                            
                            self.text_field.delete(0, 'end')
                            self.save(contend)
                        break
            except:
                print("Something went wrong...") #ToDo: handle this exception by reprinting all of the contend
                #exit()

    def updateContend(self, fromUser, chatNumber):
        # ContendArray = pcap.dumpIt(fromUser + '.pcap')
        # print(ContendArray[self.alreadyUpdatedIndex+1])
        while True:
            try:
                print(pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex+1])
                self.add(fromUser, pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex+1], chatNumber)
                self.alreadyUpdatedIndex += 1
            except:
                print("No new messages found from: " + self.getPartner())
                break

    def getPartner(self):
        if self.username == 'alice':
            return 'bob'
        else:
            return 'alice'
            
    #these methods ensure that when the user scrolls with his mouse instead of the scrollbar, that both list boxes are synced and move at the same time up and down
    def scroll1(self, *args): #when the user scrolls the listBox1, then this method ensures the position of listBox2 is synced
        if self.listBox2.yview() != self.listBox1.yview(): #when the listBox2 is out of sync...
            self.listBox2.yview_moveto(args[0])  #...adjust the yview of listBox2
        self.scrollbar.set(*args) #sync the scrollbar with the mouse wheel position

    def scroll2(self, *args):  #when the user scrolls the listBox2, then this method ensures the position of listBox1 is synced
        if self.listBox1.yview() != self.listBox2.yview(): #when the listBox1 is out of sync...
            self.listBox1.yview_moveto(args[0])  #...adjust the yview of listBox1
        self.scrollbar.set(*args) #sync the scrollbar with the mouse wheel position

    def yview(self, *args): #self configured yview command. the only job is to trigger both sync methods from abouve
        self.listBox1.yview(*args)
        self.listBox2.yview(*args)

    def createWidgets(self):
        print("connected as: \"" + self.username + "\"")        
        #window title: shows by what username you are connected to the application
        self.master.title("Subjective Chat: " + self.username.upper())
        
        #Chat: title bar: shows to who you are currently writing
        self.username_label = Label(self.topCanvasChat, text=self.getPartner())
        self.username_label.configure(bg="#ededed")

	#Chat: chatfield
        self.scrollbar = Scrollbar(self.middleCanvasChat, orient="vertical")
        self.scrollbar.config(command=self.yview)
        
        self.listBox1 = Listbox(self.middleCanvasChat, height=30, width=25, yscrollcommand=self.scroll1)
        self.listBox1.configure(bg='#e3dbd4',  font=('HelveticaNeue',10))
        
        self.listBox2 = Listbox(self.middleCanvasChat, height=30, width=25, yscrollcommand=self.scroll2)
        self.listBox2.configure(bg='#e3dbd4', font=('HelveticaNeue',10))

        #Chat: actions
        self.chatNumber = 0  #ToDo: last input is chatNumber: we need to be able to differentiate between chats and assign numbers to each one of them to somehow acess them. currently there is only 1 chat (=0)
        self.text_field = Entry(self.bottomCanvasChat, textvariable=self.msg, font=('HelveticaNeue',10))
        self.text_field.configure(bg='#f0f0f0')
        self.text_field.bind('<Return>', lambda event: self.add(self.username, self.msg.get(), self.chatNumber)) 
        self.send_button = Button(self.bottomCanvasChat, text='Send', command=lambda: self.add(self.username, self.msg.get(), self.chatNumber), bg="#25D366", activebackground="#21B858", font=('HelveticaNeue',10)) 
        self.update_button = Button(self.bottomCanvasChat, text='Update', command=lambda: self.updateContend(self.getPartner(), self.chatNumber), bg="white", font=('HelveticaNeue',10)) # ToDo: getPartner() method is just a temporary fixx

    def mergeNameCounter(self, name, counter, space):
        output = ""
        if len(name) == space - len(str(counter)) - 2:  # if the length of the name is not too long to leave no space for the counter (inclusive brackets)
            output = ''.join([name,"(",str(counter),")"])  # join the two and save it as output
        elif space > len(name) + len(str(counter)) + 2: # name needs to be extended (too short)
            extendBy = space - len(name) - len(str(counter)) - 2  # how many spaces we need to balance it and show the counter at the end of the line
            oldOutput = list(name)
            for i in range(extendBy):  # add spaces to the name
                oldOutput.append(" ")
            output = ''.join(oldOutput) 
            output = ''.join([output,"(",str(counter),")"])
        else:  # name needs to be cut (too long)
            nameSpace = space - len(str(counter)) - 2 - 3 # space the name is allowed to occupy (plus the space 3 dots will occupy to indicate the name was cut off)
            oldOutput = list(name)
            del oldOutput[nameSpace:]  # delete chars of the name
            output = ''.join(oldOutput) 
            output = ''.join([output,"...(",str(counter),")"])
        return output

    def loadChat(self):  # when the user clicks on Person in listBox3 this function is called and loads the correct chat and sets up everything needed to start the communication
        selection = self.listbox3.curselection()
        person = self.personList[selection]
        #item = self.listBox3.get(self.listBox3.curselection()[0])
        #if item == "":
        #    item = self.listBox3.get(self.listBox3.curselection()[0]-1)  # if empty string is present, return the string before that ToDo: this will ultimately not be an empty string, best case, we 

        
    def addPartners(self):
        self.newMessageCounter = 9 # ToDo: this needs to be a dictionary (with the key as partnerName and value as counter) which is automatically updated when new messages arrive thath haven't been read (increase counter)
        self.personList.append(self.getPartner()) # ToDo: remove as soon as the personList is implemented and updates automatically
        for i in range(len(self.personList)):
            self.listBox3.insert('end', self.mergeNameCounter(self.getPartner(), self.newMessageCounter, 45))  #ToDo: last number needs to be adjusted to the final font size
            self.listBox3.itemconfig(0, bg="white") #ToDo: right now there are only two partners so index will always be 0 but this needs to be dynamic
            self.listBox3.insert('end','')    
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Subjective Chat")
        
        #Set Variables
        self.msg = StringVar()
        self.username = username
        self.partner = StringVar()
        self.personList = list() # ToDo: this is the list which holds all the message partners in descending order (person who las wrote me first). This list needs to be updated automatically when new messages arrive (are updated))
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.listBoxItem = 0
        self.lastTime = list()
        
        #Configure Application layout
        self.tabFrame = Frame(self.master)
        self.tabFrame.pack(side='left', fill="both", expand=True)
        self.chatFrame = Frame(self.master)
        self.chatFrame.pack(side='right', fill="both", expand=True)
        
        #---Tab Section---
        self.tabCanvas = Canvas(self.tabFrame)
        self.tabCanvas.grid(column=0, row=0, sticky=N + S + E + W)
        self.tabScrollbar = Scrollbar(self.tabCanvas, orient="vertical")
        self.listBox3 = Listbox(self.tabCanvas, height=30, width=25, yscrollcommand=self.tabScrollbar.set)
        self.tabScrollbar.config(command=self.listBox3.yview)
        self.listBox3.configure(bg='white', font=('HelveticaNeue',15,'bold'))
        self.listBox3.grid(column=0, row=0, sticky=N + S + E + W)
        
        self.addPartners() 
            
        self.listBox3.bind("<<ListboxSelect>>", lambda x: self.loadChat())   
        
        #---Chat Section---
        #Configure Frames
        self.topFrameChat = Frame(self.chatFrame)
        #self.topFrame.configure(bg='#f0f0f0')
        self.topFrameChat.pack()
        
        self.middleFrameChat = Frame(self.chatFrame)
        #self.middleFrame.configure(bg='#f0f0f0')
        self.middleFrameChat.pack()
        
        self.bottomFrameChat = Frame(self.chatFrame)
        #self.bottomFrame.configure(bg='#f0f0f0')
        self.bottomFrameChat.pack()
        
        #Configure Subframes
        #ToDo: try to pack 3 items empty like in the middleFrame and then columnspan = 3: maybe this finally makes the send button fill the whole frame...
        
        #Configure Canvases
        self.topCanvasChat = Canvas(self.topFrameChat)
        self.middleCanvasChat = Canvas(self.middleFrameChat)
        self.bottomCanvasChat = Canvas(self.bottomFrameChat)
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        #self.topCanvas.configure(bg='#f0f0f0')
        #self.middleCanvas.configure(bg='#f0f0f0')
        #self.bottomCanvas.configure(bg='#f0f0f0')
        
        #Place Widgets
        self.createWidgets()
        
        #Pack the title bar and the send button
        #self.username_label.pack(side='top', fill="both", expand=True)
        #self.send_button.pack(fill="both", expand=True)
        
        #Placement
        #position top canvas and it's widgets
        self.topCanvasChat.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        self.username_label.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        #position middle canvas and it's widgets
        self.middleCanvasChat.grid(column=0, row=1, columnspan=3, sticky=N + S + E + W)
        self.listBox1.grid(column=0, row=1, sticky=N + S + E + W)
        self.listBox2.grid(column=1, row=1, sticky=N + S + E + W)
        self.scrollbar.grid(column=2, row=1, sticky='ns')
        #position bottom Canvas and it's widgets
        self.bottomCanvasChat.grid(column=0, row=2, columnspan=3, sticky=N + S + E + W)
        self.text_field.grid(column=0, row=2, columnspan=3, sticky=N + S + E + W)
        self.send_button.grid(column=0, row=3, columnspan=3, sticky=N + S + E + W)
        self.update_button.grid(column=0, row=4, columnspan=3, sticky=N + S + E + W)
        

root = Tk()
root.config(bg="lightgrey")
app = Login(master=root)
#username= "alice"
#app = Chat(master=root)
try:
    root.mainloop()
    root.destroy()
    root.close()
    exit()
except:
    exit()
    #pass
