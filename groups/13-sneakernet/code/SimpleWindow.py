import PySimpleGUI as sg

# this is the first draft of a window without any actual implementation of the code. Final window will probably
# be in a different file. This SimpleWindow file will for now be used as reference only probably be removed later.

# sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('Please choose an action')],
          [sg.Button('Import'), sg.Button('Export'), sg.Button('New User'), sg.Button('Cancel')],
          [sg.Slider((None, None), 0, None, None, 'h', False, None, None, False, False, False, (None, None), None, None, None, None, None, None, True, None)]]

layout2 = [[sg.Text('Enter File Path to BACNET')],
           [sg.In(), sg.FileBrowse()],
           [sg.Open(), sg.Cancel()]]

layout3 = [[sg.Text('Choose a Username')],
           [sg.InputText(key='newUser')],
           [sg.Button('Add me to BACNet'), sg.Button('Cancel')]]

path = '/home/leonhard'

# Create the Window
window = sg.Window('USB Logfiles', layout)

event, values = window.read(close=True)
if event == 'Import':
    path = sg.popup_get_folder('Path to BACNet', 'Import', default_path=path, initial_folder=path)
    print(path)
if event == 'Export':
    path = sg.popup_get_folder('Path to BACNet', 'Export', default_path=path, initial_folder=path)
    print(path)
if event == 'New User':
    window = sg.Window('New User', layout3)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break
    if event == 'Add me to BACNet':
        sg.popup('Not Implemented yet')
        print(values['newUser'])

window.close()
