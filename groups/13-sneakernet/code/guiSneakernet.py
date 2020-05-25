import PySimpleGUI as sg
# import sys
# insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '/home/leonhard/PycharmProjects/BACnet/groups/13-sneakernet/code')
import sneakernet_functions
import webbrowser
# This will be the main file for the active gui for the sneakernet.

running = False  # this keeps track of the program and if it is done (probably not needed later)

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
                 [sg.Button('Import'), sg.Button('Export'), sg.Button('Settings'), sg.Button('Close')]]

# TODO: all print statements need to be replaced by their commented functionality as soon as import works correctly
# maybe check if fields are empty inside windows and if user is actually part of users.txt
# maybe try to access (and display) the state of the flash drive. (or if needed the state of current user)
# TODO: Other gui functionality missing inside import/export?
# general visual and functional improvements for usability. Also cleaning up code and comments.

# creates first window
windowStartup = sg.Window('BACNet', layoutStartup)
event, values = windowStartup.read(close=True)  # that closes itself
if event == 'Submit Path':
    path = values['path']
    windowWelcome = sg.Window('Sneakernet', layoutWelcome)
    while True:
        event, values = windowWelcome.read()
        if event == 'Not yet part of BACnet?':
            # TODO: where should this link lead? maybe https://github.com/cn-uofbasel/BACnet/blob/master/doc/README.md
            webbrowser.open('https://example.com')
        if event == 'Login':
            name = values['name']
            print('User: ', name, path)
            # user = sneakernet_functions.User(name, path)
            running = True
            break
        if event is None:
            break
    windowWelcome.close()

# creates the main actions window which you should be able to stay inside and come back to
if running:
    windowActions = sg.Window('Sneakernet', layoutActions)  # creates a new window
    while True:
        event, values = windowActions.read()
        if event in (None, 'Close'):
            windowActions.close()
            break

        if event == 'Import':
            windowImport = sg.Window('Import',
                                     [[sg.Text('Do you wish to import files from the flash drive to your BACNet?')],
                                      [sg.Button('Import'), sg.Button('Cancel')]])
            event, values = windowImport.read(close=True)
            if event == 'Import':
                print('trying to import files')  # can we show how much is on drive or will be imported?
                # sneakernet_functions.importing(user)
                sg.popup('Files imported successfully')

        if event == 'Export':
            windowExport = sg.Window('Export',
                                     [[sg.Text('Please specify the maximum amount of events you wish to export')],
                                      [sg.Slider(range=(1, 100), default_value=30, orientation='h', key='maxEvents')],
                                      [sg.Button('Export'), sg.Button('Cancel')]])
            event, values = windowExport.read(close=True)
            if event == 'Export':
                maxEvents = values['maxEvents']
                print('trying to export up to', maxEvents, 'events')
                # sneakernet_functions.exporting(user, maxEvents)
                sg.popup('Files exported successfully')

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
                        print(name)
                if event == 'Change Path':
                    windowChangePath = sg.Window('Change Path', [[sg.Text('Select a different path')],
                                                                 [sg.In(path),
                                                                  sg.FolderBrowse(initial_folder=path, key='newPath')],
                                                                 [sg.Button('Save new path'), sg.Button('Cancel')]])
                    event, values = windowChangePath.read(close=True)
                    if event == 'Save new path':
                        path = values['newPath']
                        print(path)