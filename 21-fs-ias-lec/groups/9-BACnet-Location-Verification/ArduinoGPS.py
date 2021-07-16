import platform  # used to determine operating system
import sys
import threading

import serial.tools.list_ports  # used to list open ports

from datetime import datetime
from logMerge import LogMerge
from logMerge.PCAP import PCAP
from logMerge.eventCreationTool import EventCreationTool
from logMerge.eventCreationTool.Event import Event

sys.path.append(".BACnet/demo/lib")

# locationVerificationTool
# used to store logins from the gps-gadget to Feeds
#
# to use this script, make sure you connected the arduino
# after every successful login (key-card on key-card-reader) date, time, uid, long, lat is stored in a pcap file
# after every successful 5th login, all stored events in the pcap file gets outprinted
#
# to share the information with other BACnet users: use feed_control.py and guiSneakernet.py from HS20-project

# Lists all ports currently open.
ports = list(serial.tools.list_ports.comports())
port = None
port_list = []
arduino_found = False
# macOS has its ports stored in the /dev/ directors
if "macOS" in platform.platform():
    for p in ports:
        if "usbmodem" in p.name:
            port = '/dev/' + str(p.name)
            break

# Windows uses COM ports.
elif "Windows" in platform.platform():
    for p in ports:
        if "Arduino" in p.description or "USB Serial Device" in p.description:
            port = str(p.device)
            port_list.append(port)
            arduino_found = True

    # no Arduino found
    if not arduino_found:
        if "Arduino" not in p.description:
            print("No Arduino found")
            print("no port chosen")
    # multiple Arduino found
    elif len(port_list) > 1:
        print("multiple Arduino's found. Please input wished ports:")
        for p in port_list:
            print("Ports: ", p)
        port = input("Enter port: ")
        print("chosen port: ", port)
    # only one Arduino found
    else:
        print("chosen port: ", port)
# linux users have to enter their port manually
elif "Linux" in platform.platform():
    port = input("please enter port:")
    print("chosen port: ", port)

# Initialize serial connection with chosen port
ser = serial.Serial(port, 9600, timeout=1)

# initialize uid, lat, long
uid, latitude, longitude = None, None, None

# creating first feed with EventFactory from logMerge-Project (HS2020)
lm = LogMerge.LogMerge()
ecf = EventCreationTool.EventFactory()
master_feed_id = EventCreationTool.EventFactory.get_feed_id(ecf)
# this is our first Event.
first_event = ecf.first_event("verificationTool", master_feed_id)


#
# Reading information from Arduino and store uid, long, lat into global variables.
# if location or uid is changed, change global variables
#
class SerialReadingThread(threading.Thread):

    # standard thread __init__
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        # access global variables for further processing
        global uid, latitude, longitude
        while True:
            # for each serial line, check for type of information
            data_raw = ser.readline().decode().strip()
            if data_raw.startswith("x1uid"):
                uid = data_raw[6:]
            elif data_raw.startswith("x2lon"):
                longitude = data_raw[5:]
            elif data_raw.startswith("x3lat"):
                latitude = data_raw[5:]
            else:
                pass


t1 = SerialReadingThread(1, "t1")
t1.start()
# value for counting logins
login_counter = 0
# list of our events. gets appended every login
event_list = [first_event]


#
# prints all feeds stored in a PCAP file (named verificationTool.pcap)
# make sure this PCAP file exists. Function is called, after every 5th successful login
# pcap files exists from first successful login
#
def print_events():
    events = PCAP.read_pcap('verificationTool.pcap')
    for event in events:
        event = Event.from_cbor(event)
        print("events: ", event.content.content[1])


#
# actually script: reacts if key-card is found (login). store events in a event list and write them to a pcap file
# printing every 5th login all events in the pcap file
# runs until script is stopped manually or arduino is disconnected
#
while True:
    print("waiting for Login...")
    # Login successful (key-card found)
    if uid is not None:
        # increase login counter
        login_counter = login_counter + 1
        print("successful Login: writing feed")
        # generate Message (Time, UID, LONG, LAT)
        msg_to_store = "Date / Time: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ", UID: " + str(uid) + \
                       ", LONG: " + str(longitude) + ", LAT: " + str(latitude)
        # this is our new event (feed)
        new_event = ecf.next_event("verificationTool/storeFeed", msg_to_store)
        # append the event to our event list
        event_list.append(new_event)
        PCAP.write_pcap('verificationTool', event_list)
        # reset uid to None --> script waits until next login
        uid = None
    # print every 5th successful login all stored feeds
    if login_counter == 5:
        login_counter = 0
        print_events()
