import PySimpleGUI as sg
# from .sneakernet_functions import *

# This will be the real active gui for the sneakernet.

# importing functions from sneakernet_functions doesn't work properly yet.

# basic layouts for the needed windows
layout = [[sg.Text('Please choose an action')],
          [sg.Button('Import'), sg.Button('Export'), sg.Button('New User'), sg.Button('Cancel')]]

layout1 = [[sg.Text('Do you wish to import files from the flash drive to your BACNet?')],
           [sg.Button('Import'), sg.Button('Cancel')]]

layout2 = [[sg.Text('Please specify the maximum amount of events you wish to export')],
           [sg.Slider(orientation='h', key='maxEvents')],
           [sg.Button('Export'), sg.Button('Cancel')]]

layout3 = [[sg.Text('Choose a Username')],
           [sg.InputText(key='name')],
           [sg.Button('Add me to BACNet'), sg.Button('Cancel')]]

# creates first window
window = sg.Window('Sneakernet', layout)

# that will close itself after being read
event, values = window.read(close=True)
if event == 'Import':
    window = sg.Window('Import', layout1)  # creates a new window
if event == 'Export':
    window = sg.Window('Export', layout2)  # creates a new window
if event == 'New User':
    window = sg.Window('New User', layout3)  # creates a new window

while True:
    event, values = window.read()
    if event in (None, 'Cancel'):
        break
    if event == 'Import':
        # importing()
        sg.popup('Files Imported successfully')
        break
    if event == 'Export':
        # exporting(values['maxEvents'])
        sg.popup(values['maxEvents'], 'Files exported successfully')
        break
    if event == 'Add me to BACNet':
        # newUser(values['name'])
        sg.popup('New User', values['name'], 'added to BACNet')
        break

window.close()

