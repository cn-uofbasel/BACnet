import PySimpleGUI as sg
# import sys
# insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '/home/leonhard/PycharmProjects/BACnet/groups/13-sneakernet/code')
import sneakernet_functions
import webbrowser
import os
# This will be the main file for the active gui for the sneakernet.

running = False  # this keeps track of the program and if it is done (probably not needed later)
user = None
path = None
# basic layouts for the needed windows
layoutStartup = [[sg.Text('Welcome to the Sneakernet')],
                 [sg.Text('Please give the path to the flash drive you wanna use')],
                 [sg.In(), sg.FolderBrowse(key='path')],
                 [sg.Button('Submit Path')]]

layoutWelcome = [[sg.Text('Welcome to the BACnet')],
                 [sg.Text('Please log in with your username')],
                 [sg.Text('Username'), sg.In(size=(20, None), key='name'), sg.Button('Login')],
                 [sg.Button('Not yet part of BACnet?')]]

layoutActions = [[sg.Text('Please choose an action')],
                 [sg.Button('Update'), sg.Button('Settings'), sg.Button('Close')]]

# TODO: Settings currently not really needed (remove them or add the functionality e.g. change username)
# TODO: Change import/export to only update?
# Check if user is actually part of users.txt?
# maybe try to access (and display) the state of the flash drive. (or if needed the state of current user)
# general improvements and cleaning up of code and comments.

# creates first window
windowStartup = sg.Window('BACNet', layoutStartup)
while True:
    event, values = windowStartup.read()
    if event is None:
        break
    if event == 'Submit Path':
        path = values['path']
        if path != "":
            windowStartup.close()
            windowWelcome = sg.Window('Sneakernet', layoutWelcome)
            while True:
                event, values = windowWelcome.read()
                if event is None:
                    break
                if event == 'Not yet part of BACnet?':
                    webbrowser.open('https://github.com/cn-uofbasel/BACnet/blob/master/doc/README.md')
                if event == 'Login':
                    name = values['name']
                    if name != "":
                        user = sneakernet_functions.User(name, path)
                        running = True
                        break
            windowWelcome.close()
            break

# creates the main actions window which you should be able to stay inside and come back to
if running:
    windowActions = sg.Window('Sneakernet', layoutActions)  # creates a new window
    while True:
        event, values = windowActions.read()
        if event in (None, 'Close'):
            windowActions.close()
            break
        if event == 'Update':
            windowExport = sg.Window('Update',
                                     [[sg.Text('Please specify the amount of files you wish to export')],
                                      [sg.Text('To export all files drag the slider to -1')],
                                      [sg.Slider(range=(-1, 100), default_value=30, orientation='h', key='maxEvents')],
                                      [sg.Button('Update'), sg.Button('Cancel')]])
            event, values = windowExport.read(close=True)
            if event == 'Update':
                maxEvents = values['maxEvents']
                user.exporting(maxEvents)
                dirIsEmpty = True
                for file in os.listdir(path):
                    if file.endswith('.pcap'):
                        dirIsEmpty = False
                if dirIsEmpty:
                    sg.popup('Update successful but you are all up to date')
                else:
                    sg.popup('Files updated successfully')

        if event == 'Settings':
            windowSettings = sg.Window('Settings', [[sg.Button('Change Username'), sg.Button('Change Path')],
                                                    [sg.Button('Done')]])
            while True:
                event, values = windowSettings.read()
                if event in (None, 'Done'):
                    windowSettings.close()
                    break
                if event == 'Change Username':
                    windowChangeName = sg.Window('Change Username', [[sg.Text('Choose a new Username')],
                                                                     [sg.InputText(default_text=name, key='newName')],
                                                                     [sg.Button('Save new name'), sg.Button('Cancel')]])
                    event, values = windowChangeName.read(close=True)
                    if event == 'Save new name':
                        name = values['newName']
                        user.changename(name)
                if event == 'Change Path':
                    windowChangePath = sg.Window('Change Path', [[sg.Text('Select a different path')],
                                                                 [sg.In(path),
                                                                  sg.FolderBrowse(initial_folder=path, key='newPath')],
                                                                 [sg.Button('Save new path'), sg.Button('Cancel')]])
                    event, values = windowChangePath.read(close=True)
                    if event == 'Save new path':
                        path = values['newPath']
                        print(path)
