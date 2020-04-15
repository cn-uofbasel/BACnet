from tkinter import *
import datetime
import threading
import feed
import pcap
import string
import crypto
import event
import os

global username


class Chat(Frame):

    def save(self, contend):
        feed._appendIt(self.username, 'append', contend)

    def add(self, username, contend, event=None):
        self.time = datetime.datetime.now()
        if username != self.username: # user updated
            try:
                print("getting message from " + self.getPartner() + ":")
                self.listBox.insert('end', '[' + self.time.strftime("%H:%M:%S") + '] ' + username + ': ' + contend)
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
                            self.listBox.insert('end', '[' + self.time.strftime("%H:%M:%S") + '] ' + username + ': ' + contend)
                            self.text_field.delete(0, 'end')
                            self.save(contend)
                        break
            except:
                print("Something went wrong...")

    def updateContend(self, fromUser):
        #ContendArray = pcap.dumpIt(fromUser + '.pcap')
        #print(ContendArray[self.alreadyUpdatedIndex+1])
        while True:
            try:
                print(pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex+1])
                self.add(fromUser, pcap.dumpIt(fromUser + '.pcap')[self.alreadyUpdatedIndex+1])
                self.alreadyUpdatedIndex += 1
            except:
                print("No messages new found from: " + self.getPartner())
                break

    def getPartner(self):
        if self.username == 'alice':
            return 'bob'
        else:
            return 'alice'

    def createWidgets(self):
        print("connected as: \"" + self.username + "\"")
        self.canvas = Canvas(self.master, width=800, height=1100)  # , bg='#4f4f4f')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(column=0, row=0, columnspan=2, sticky=N + S + E + W)

        self.username_label = Label(self.canvas, text="connected as: " + self.username)
        self.username_label.grid(column=0, row=0, sticky=N + S + E + W)

        self.scrollbar = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.listBox = Listbox(self.canvas, height=30, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(column=2, row=0, sticky='ns')
        self.listBox.grid(column=0, row=1, sticky=N + S + E + W)

        self.text_field = Entry(self.canvas, textvariable=self.msg)
        self.text_field.bind('<Return>', lambda event: self.add(self.username, self.msg.get()))
        self.text_field.grid(column=0, row=2, sticky=N + S + E + W)
        self.send_button = Button(self.canvas, text='Send', command=lambda: self.add(self.username, self.msg.get()))
        self.send_button.grid(column=0, row=3, sticky=N + S + E + W)

        self.update_button = Button(self.canvas, text='Update', command=lambda: self.updateContend(self.getPartner()),
                                    bg='white')
        self.update_button.grid(column=0, row=4, sticky=N + S + E + W)

    def __init__(self, master=None):
        global username
        Frame.__init__(self, master)
        master.title("Subjective Chat")
        self.msg = StringVar()
        self.username = username
        self.partner = StringVar()
        self.alreadyUpdatedIndex = 0
        self.time = datetime.datetime.now()
        self.createWidgets()


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
        self.canvas = Canvas(self.master, width=400, height=300)  # , bg='#4f4f4f')
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
        self.send_button = Button(self.canvas, text='choose', command=lambda: self.adjust(self.msg.get()))

    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Login")
        self.msg = StringVar()
        self.createWidgets()


root = Tk()
app = Login(master=root)
try:
    root.mainloop()
    root.destroy()
    root.close()
except:
    pass
