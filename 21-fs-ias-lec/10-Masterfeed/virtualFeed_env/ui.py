# -*- coding: utf-8 -*-
'''
Created July 2021
@author: retok
'''

from tkinter import Tk, Label, Button, Listbox, E, W, S, N, filedialog, Toplevel, Entry, END, NONE, messagebox
from tkinter.messagebox import WARNING
from uiFunctions import UiFunctions
from cryptography.exceptions import InvalidTag

'''
The UI class for the device handler UI
'''
class Ui:    
    def __init__(self, master):
        self.uf = UiFunctions()
        self.master = master
        # method on closing the window
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing) 
        self.master.title('BACnet Device Handler')
        self.master.geometry('+300+300')
        # default values for padding and sticky
        padyD = 5
        padxD = 5
        stickyD = E+W+S+N

        # Layout
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, pad=7)
        self.master.rowconfigure(1, weight=1)
        self.master.rowconfigure(7, weight=1)
        
        self.welcomeText = 'Welcome to BACnet Device Handler\n' + 'This Device is named: '
        
        self.lblWelcome = Label(master, text=self.welcomeText + self.uf.thisDevName)
        self.lblWelcome.grid(row=0, sticky=W, pady=padyD, padx=padxD)          

        self.lblDevices = Label(master, text='Active Devices:')
        self.lblDevices.grid(row=1, sticky=W+S, pady=padyD, padx=padxD)  
        
        self.lbxDevices = Listbox(master, activestyle = NONE) 
        self.lbxDevices.grid(row=2, column=0, rowspan=4, sticky=stickyD, pady=padyD, padx=padxD)  
        self.lbxDevices.bind('<FocusOut>', self.lbxDevices.selection_clear(0, END))
        
        self.lblDevicesBlocked = Label(master, text='Former Devices now blocked:')
        self.lblDevicesBlocked.grid(row=6, sticky=W+S, pady=padyD, padx=padxD)  

        self.lbxDevicesBlocked = Listbox(master, activestyle = NONE) 
        self.lbxDevicesBlocked.grid(row=7, column=0, rowspan=3, sticky=stickyD, pady=padyD, padx=padxD)  
        self.lbxDevicesBlocked.bind('<FocusOut>', self.lbxDevicesBlocked.selection_clear(0, END))

        self.update_device_list()

        self.btnCreateNew = Button(master, text='Change Device Name', command=self.change_device_name)
        self.btnCreateNew.grid(row=2, column=2, sticky=stickyD, pady=padyD, padx=padxD) 
        
        self.btnImport = Button(master, text='Import Data', command=self.import_keys_from_old)
        self.btnImport.grid(row=3, column=2, sticky=stickyD, pady=padyD, padx=padxD)  
        
        self.btnExport = Button(master, text='Export Data for new Device', command=self.export_keys_to_new)
        self.btnExport.grid(row=4, column=2, sticky=stickyD, pady=padyD, padx=padxD)   

        self.btnBlock = Button(master, text='Block a Device after loss', command=self.block_device)
        self.btnBlock.grid(row=5, column=2, sticky=stickyD, pady=padyD, padx=padxD)          
    
    def change_device_name(self):
        dial = ChangeDeviceName(self.master, self.uf)
        self.master.wait_window(dial.top) # waiting for the popUp to be destroyed
        self.update_device_list()
        self.lblWelcome.config(text=self.welcomeText + self.uf.thisDevName)
    
    def export_keys_to_new(self):        
        dial = ExportToDialog(self.master, self.uf)
        self.master.wait_window(dial.top) # waiting for the popUp to be destroyed
        
    def import_keys_from_old(self):
        dial = ImportFromDialog(self.master, self.uf)
        self.master.wait_window(dial.top) # waiting for the popUp to be destroyed
        self.update_device_list()
        
    def block_device(self):
        # get selected element from Listbox
        selected = self.lbxDevices.curselection()  # returns python tuple (), not list []
        if selected == ():
            raise ExceptionMsg('No device selected from list!')
            return
        # change status
        name = self.lbxDevices.get(selected[0])
        if name == self.uf.thisDevName:
            self.lbxDevices.selection_clear(0, END)
            raise ExceptionMsg('Unable to block the device you are on')
            return        
        answer = messagebox.askokcancel('Warning!', 'Do you want to block ' + name +'?\n This can not be undone!', icon = WARNING)
        if answer:
            self.uf.change_device_status(name)
            self.update_device_list()
               
    def update_device_list(self):
        # delete lines first in listbox
        self.lbxDevices.delete(0, self.lbxDevices.size())
        self.lbxDevicesBlocked.delete(0, self.lbxDevicesBlocked.size())
        # i and j position in each lbx
        i =0; j=0
        for dev in self.uf.devDict.keys():  
            if self.uf.devDict.get(dev).get('status') == 'active':
                self.lbxDevices.insert(i, self.uf.devDict.get(dev).get('deviceName'))
                i += 1
            else:
                self.lbxDevicesBlocked.insert(j, self.uf.devDict.get(dev).get('deviceName') + ' (blocked)')
                j += 1
                
    def on_closing(self):
        # export dictionary on closing to save situation
        self.uf.write_dict_to_json()    
        self.master.destroy()
            

'''
Class for Change Device name
Called from main window on clicking the Change name button
'''      
class ChangeDeviceName:
    def __init__(self, master, uf):
        self.master = master
        self.uf = uf
        self.top = Toplevel(self.master)
        self.top.title('Change Device Name')
        self.top.geometry('+350+350')
        # default values for padding and sticky
        padyD = 5
        padxD = 5      
        
        # Layout                
        self.lblName = Label(self.top, text='Name of new device')
        self.lblName.grid(row=0, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyName = Entry(self.top)
        self.etyName.grid(row=1, columnspan=3, sticky=W+E, pady=padyD, padx=padxD)    
        
        self.btnCancle = Button(self.top, text='Cancle', command=self.cancle, width=16)
        self.btnCancle.grid(row=7, sticky=W, pady=padyD, padx=padxD) 
        
        self.btnOK = Button(self.top, text='OK',command=self.submit, width=16)
        self.btnOK.grid(row=7, column=2, sticky=E, pady=padyD, padx=padxD) 
        
    def cancle(self):
        self.top.destroy() 
        
    def submit(self):
        if len(self.etyName.get()) == 0:  # avoid errors when nothing entered yet
            try:
                raise ExceptionMsg('No user Name Provided!', self.top, self.master)
            except Exception:
                pass
        else:
            self.uf.update_device_name(self.etyName.get())   
            self.top.destroy() 
                              

'''
Class for ExportDialog
Called from main window on clicking the Export button
'''      
class ExportToDialog:
    def __init__(self, master, uf):
        self.master = master
        self.uf = uf
        self.top = Toplevel(self.master)
        self.top.title('Export keys for new device')
        self.top.geometry('+350+350')
        ExportToDialog.path = ''  # static member variable, ramains on new button click as priviously selected
        # default values for padding and sticky
        padyD = 5
        padxD = 5      
        
        # Layout                
        self.lblPW = Label(self.top, text='Enter passphrase (Needed later on new device. Thus remember!')
        self.lblPW.grid(row=0, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyPw = Entry(self.top)
        self.etyPw.grid(row=1, columnspan=3, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.lblPwCheck = Label(self.top, text='')
        self.lblPwCheck.grid(row=2, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.lblPath = Label(self.top, text='Save Encrypted files to transport medium (e.g. USB-Stick):')
        self.lblPath.grid(row=3, columnspan=3, sticky=W+S, pady=padyD, padx=padxD) 
        
        self.lblPathDisplay = Label(self.top, text=ExportToDialog.path)
        self.lblPathDisplay.grid(row=4, columnspan=3, sticky=W+N, pady=padyD, padx=padxD) 
        
        self.btnCancle = Button(self.top, text='Cancle', command=self.cancle, width=16)
        self.btnCancle.grid(row=5, sticky=W, pady=padyD, padx=padxD) 

        self.btnPath = Button(self.top, text='Select path',command=self.change_path, width=16)
        self.btnPath.grid(row=5, column=1, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.btnOK = Button(self.top, text='OK',command=self.submit, width=16)
        self.btnOK.grid(row=5, column=2, sticky=E, pady=padyD, padx=padxD) 
        
        self.update()
        
    # update display loop to show things that have changed sinze first creating GUI
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
        pw = self.etyPw.get()
        
        # input check
        if len(pw) == 0:
            raise ExceptionMsg('No password provided', self.top, self.master)
        elif len(ExportToDialog.path) == 0:
            raise ExceptionMsg('No path selected', self.top, self.master)
        else:  
            try:
                self.uf.encrypt_private_keys(pw, ExportToDialog.path)
                self.uf.export_other_files(ExportToDialog.path)
                self.top.destroy()   
                messagebox.showinfo('successfull', 'Data successfuly exportet to ' + self.path)
            except FileNotFoundError as error:
                try:
                    raise ExceptionMsg(error, self.top, self.master) from None  
                except Exception:
                    pass                
                      
            
'''
Class for ImportDialog
Called from main window on clicking the Import button
'''      
class ImportFromDialog:
    def __init__(self, master, uf):
        self.master = master
        self.uf = uf 
        self.top = Toplevel(self.master)
        self.top.title('Import keys from old device')
        self.top.geometry('+350+350')
        ImportFromDialog.path = ''  # static member variable
        # default values for padding and sticky
        padyD = 5
        padxD = 5      
        
        # Layout                       
        self.lblPW = Label(self.top, text='Enter passphrase to decrypte Files')
        self.lblPW.grid(row=0, columnspan=3, sticky=W, pady=padyD, padx=padxD) 
        
        self.etyPw = Entry(self.top)
        self.etyPw.grid(row=1, columnspan=3, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.lblPath = Label(self.top, text='Import files from transport medium (e.g. USB-Stick):')
        self.lblPath.grid(row=2, columnspan=3, sticky=W+S, pady=padyD, padx=padxD) 
        
        self.lblPathDisplay = Label(self.top, text=ImportFromDialog.path)
        self.lblPathDisplay.grid(row=3, columnspan=3, sticky=W+N, pady=padyD, padx=padxD) 
        
        self.btnCancle = Button(self.top, text='Cancle', command=self.cancle, width=16)
        self.btnCancle.grid(row=4, sticky=W, pady=padyD, padx=padxD) 

        self.btnPath = Button(self.top, text='Select path',command=self.change_path, width=16)
        self.btnPath.grid(row=4, column=1, sticky=W+E, pady=padyD, padx=padxD) 
        
        self.btnOK = Button(self.top, text='OK',command=self.submit, width=16)
        self.btnOK.grid(row=4, column=2, sticky=E, pady=padyD, padx=padxD) 
        
        self.update()
        
    # update display loop to show things that have changed sinze first creating GUI
    def update(self):
        self.lblPathDisplay.config(text=ImportFromDialog.path, font='Helvetica 8 bold')
        self.top.after(500, self.update) # call update() again after 500ms
        
    def change_path(self):
        ImportFromDialog.path = filedialog.askdirectory()
        self.top.lift(aboveThis=self.master)  # lift the toplevel above master window again
        
    def cancle(self):
        self.top.destroy() 
        
    def submit(self):
        pw = self.etyPw.get()
        
        # input check
        if len(pw) == 0:
            raise ExceptionMsg('No password provided', self.top, self.master)
        elif len(ImportFromDialog.path) == 0:
            raise ExceptionMsg('No path selected', self.top, self.master)
        else:                
            try:
                # password verification happens as decryption with aes throws invalid tag exeption
                # if one of the elements (none, key, ...) is wrong. 
                # if key is wrong its a password problem, thus catch the InvalidTag Exception
                self.uf.decrypt_private_keys(pw, ImportFromDialog.path)
                self.uf.import_other_files(ImportFromDialog.path)
                self.top.destroy() 
                messagebox.showinfo('successfull', 'Data successfuly importetd') 
                pass
            except FileNotFoundError as error:
                try:
                    raise ExceptionMsg(error, self.top, self.master) from None
                except Exception:
                    pass
            except InvalidTag:
                try:
                    raise ExceptionMsg('The provided password is wrong', self.top, self.master) from None
                except Exception:
                    pass


'''
Class to display error messages raised from exceptions
'''
class ExceptionMsg(Exception):
    def __init__(self, msg, window=None, master=None):
        messagebox.showerror('Error', msg)
        # lift error causing window back to top
        if window is not None and master is not None:
            window.lift(aboveThis=master)  
        pass


'''
Entry point when running from console or other modules together
with main- Method called on execution
'''
def main():
    root = Tk()
    Ui(root)
    root.mainloop()

if __name__ == '__main__':
    main()
        
    

