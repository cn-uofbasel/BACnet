# -*- coding: utf-8 -*-
"""
Created July 2021
@author: retok
"""

from tkinter import Tk, Label, Button, Listbox, E, W, S, N, filedialog, Toplevel, Entry, messagebox
from uiFunctions import *
from cryptography.exceptions import InvalidTag

"""
The UI class for the device handler UI
"""
class Ui:    
    def __init__(self, master):
        self.uf = UiFunctions()
        self.master = master
        self.master.title("BACnet Device Handler")
        self.master.geometry('+300+300')
        # default values for padding and sticky
        padyD = 5
        padxD = 5
        stickyD = E+W+S+N

        # Layout
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, pad=7)
        self.master.rowconfigure(3, weight=1)
        
        self.lblWelcome = Label(master, text="Welcome to BACnet Device Handler")
        self.lblWelcome.grid(row=0, sticky=stickyD, pady=padyD, padx=padxD)          
        
        self.lbxDevices = Listbox(master) 
        self.lbxDevices.grid(row=1, column=0, rowspan=3, sticky=stickyD, pady=padyD, padx=padxD)  
        self.update_device_list()
        
        self.btnCreateNew = Button(master, text="Export keys for new device", command=self.export_keys_to_new)
        self.btnCreateNew.grid(row=1, column=2, sticky=stickyD, pady=padyD, padx=padxD)  
        
        self.btnGetNew = Button(master, text="Import keys on new device", command=self.import_keys_from_old)
        self.btnGetNew.grid(row=2, column=2, sticky=stickyD, pady=padyD, padx=padxD)  
            
        # delete device??
    
    def export_keys_to_new(self):        
        dial = ExportToDialog(self.master, self.uf)
        self.master.wait_window(dial.top) # waiting for the popUp to be destroyed
        pw = dial.pw
        deviceName = dial.deviceName
        path = dial.path
        
    def import_keys_from_old(self):
        dial = ImportFromDialog(self.master, self.uf)
        self.master.wait_window(dial.top) # waiting for the popUp to be destroyed
        pw = dial.pw
        deviceName = dial.deviceName
        path = dial.path        
        
    def update_device_list(self):
        self.lbxDevices.insert(1, "Laptop")
        self.lbxDevices.insert(2, "Handy")
        self.lbxDevices.insert(3, "Tablet")

"""
Class for ExportToeDialog
Called from main window on clicking the Export button
"""      
class ExportToDialog:
    def __init__(self, master, uf):
        self.master = master
        self.uf = uf
        self.top = Toplevel(self.master)
        self.top.title("Export keys for new device")
        self.top.geometry('+350+350')
        ExportToDialog.path = ''  # static member variable, ramains on new button click as priviously selected
        self.pw = ''
        self.deviceName = ''
        # default values for padding and sticky
        padyD = 5
        padxD = 5      
        
        # Layout                
        self.lblName = Label(self.top, text="Name of new device")
        self.lblName.grid(row=0, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyName = Entry(self.top)
        self.etyName.grid(row=1, columnspan=3, sticky=W+E, pady=padyD, padx=padxD)
        
        self.lblPW = Label(self.top, text="Enter passphrase (Needed later on new device. Thus remember!")
        self.lblPW.grid(row=2, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyPw = Entry(self.top)
        self.etyPw.grid(row=3, columnspan=3, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.lblPwCheck = Label(self.top, text='')
        self.lblPwCheck.grid(row=4, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.lblPath = Label(self.top, text='Save Encrypted files to transport medium (e.g. USB-Stick):')
        self.lblPath.grid(row=5, columnspan=3, sticky=W+S, pady=padyD, padx=padxD) 
        
        self.lblPathDisplay = Label(self.top, text=ExportToDialog.path)
        self.lblPathDisplay.grid(row=6, columnspan=3, sticky=W+N, pady=padyD, padx=padxD) 
        
        self.btnCancle = Button(self.top, text="Cancle", command=self.cancle, width=16)
        self.btnCancle.grid(row=7, sticky=W, pady=padyD, padx=padxD) 

        self.btnPath = Button(self.top, text='Select path',command=self.change_path, width=16)
        self.btnPath.grid(row=7, column=1, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.btnOK = Button(self.top, text="OK",command=self.submit, width=16)
        self.btnOK.grid(row=7, column=2, sticky=E, pady=padyD, padx=padxD) 
        
        self.update()
        
    # check display loop
    def update(self):
        if len(self.etyPw.get()) > 0:  # avoid errors when nothing entered yet
            text, color = self.uf.pw_checker(self.etyPw.get())
            self.lblPwCheck.config(text=text, foreground = color)
        self.lblPathDisplay.config(text=ExportToDialog.path, font='Helvetica 8 bold')
        self.top.after(500, self.update) # call update() again after 500ms
        
    def change_path(self):
        ExportToDialog.path = filedialog.askdirectory()
        self.top.lift(aboveThis=self.master)  # lift the toplevel above master window again
        
    def cancle(self):
        self.top.destroy() 
        
    def submit(self):
        self.deviceName = self.etyName.get()
        self.pw = self.etyPw.get()
        
        # input check
        if len(self.pw) == 0:
            raise ExceptionMsg('No password provided', self.top, self.master)
        elif len(self.path) == 0:
            raise ExceptionMsg('No path selected', self.top, self.master)
        else:  
            try:
                self.uf.encrypt_private_keys(self.pw, self.path)
                self.top.destroy()   
                messagebox.showinfo('successfull', 'Data successfuly exportet to ' + self.path)
            except FileNotFoundError as error:
                raise ExceptionMsg(error, self.top, self.master)                   
            
            
            
"""
Class for ImportFromDialog
Called from main window on clicking the Import button
"""      
class ImportFromDialog:
    def __init__(self, master, uf):
        self.master = master
        self.uf = uf
        self.top = Toplevel(self.master)
        self.top.title("Import keys from old device")
        self.top.geometry('+350+350')
        ImportFromDialog.path = ''  # static member variable
        self.pw = ''
        self.deviceName = ''
        # default values for padding and sticky
        padyD = 5
        padxD = 5      
        
        # Layout                
        self.lblName = Label(self.top, text="Name of new device")
        self.lblName.grid(row=0, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyName = Entry(self.top)
        self.etyName.grid(row=1, columnspan=3, sticky=W+E, pady=padyD, padx=padxD)
        
        self.lblPW = Label(self.top, text="Enter passphrase to decrypte Files")
        self.lblPW.grid(row=2, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyPw = Entry(self.top)
        self.etyPw.grid(row=3, columnspan=3, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.lblPath = Label(self.top, text='Import files from transport medium (e.g. USB-Stick):')
        self.lblPath.grid(row=4, columnspan=3, sticky=W+S, pady=padyD, padx=padxD) 
        
        self.lblPathDisplay = Label(self.top, text=ImportFromDialog.path)
        self.lblPathDisplay.grid(row=5, columnspan=3, sticky=W+N, pady=padyD, padx=padxD) 
        
        self.btnCancle = Button(self.top, text="Cancle", command=self.cancle, width=16)
        self.btnCancle.grid(row=6, sticky=W, pady=padyD, padx=padxD) 

        self.btnPath = Button(self.top, text='Select path',command=self.change_path, width=16)
        self.btnPath.grid(row=6, column=1, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.btnOK = Button(self.top, text="OK",command=self.submit, width=16)
        self.btnOK.grid(row=6, column=2, sticky=E, pady=padyD, padx=padxD) 
        
        self.update()
        
    # check display loop
    def update(self):
        self.lblPathDisplay.config(text=ImportFromDialog.path, font='Helvetica 8 bold')
        self.top.after(500, self.update) # call update() again after 500ms
        
    def change_path(self):
        ImportFromDialog.path = filedialog.askdirectory()
        self.top.lift(aboveThis=self.master)  # lift the toplevel above master window again
        
    def cancle(self):
        self.top.destroy() 
        
    def submit(self):
        self.deviceName = self.etyName.get()
        self.pw = self.etyPw.get()
        
        # input check
        if len(self.pw) == 0:
            raise ExceptionMsg('No password provided', self.top, self.master)
        elif len(self.path) == 0:
            raise ExceptionMsg('No path selected', self.top, self.master)
        else:                
            try:
                # password verification happens as decryption with aes throws invalid tag exeption
                # if one of the elements (none, key, ...) is wrong. 
                # if key is wrong its a password problem, thus catch the InvalidTag Exception
                self.uf.decrypt_private_keys(self.pw, self.path)
                self.top.destroy() 
                messagebox.showinfo('successfull', 'Data successfuly importetd')                
            except FileNotFoundError as error:
                raise ExceptionMsg(error, self.top, self.master)                
            except InvalidTag:
                raise ExceptionMsg('The password is wrong', self.top, self.master)


"""
Class to display error messages raised from exceptions
"""
class ExceptionMsg(Exception):
    def __init__(self, msg, window=None, master=None):
        messagebox.showerror('Error', msg)
        if window is not None and master is not None:
            window.lift(aboveThis=master)         
        pass

"""
Entry point when running from console or other modules together
with main- Method called on execution
"""
def main():
    root = Tk()
    Ui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
        
    

