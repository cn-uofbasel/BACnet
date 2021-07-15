import platform # used to determine operating system
import sys
import threading
import time
import serial.tools.list_ports # used to list open ports
from logMerge import LogMerge
from logMerge.PCAP import PCAP
from logMerge.eventCreationTool import EventCreationTool
from logMerge.eventCreationTool.Event import Event

sys.path.append(".BACnet/demo/lib")

# TODO: comments
# TODO: delete local feed if needed?
# TODO: if local feed is already stored, overwrite and dont initialize a new one

# Lists all ports currently open.
ports = list(serial.tools.list_ports.comports())
port = None

# macOS has its ports stored in the /dev/ directors
if "macOS" in platform.platform():
    for p in ports:
        if "usbmodem" in p.name:
            port = '/dev/' + str(p.name)
            break

# Windows uses COM ports.
elif "Windows" in platform.platform():
    for p in ports:
        print(p.description, p.name)
        if "USB Serial Device" in p.description:
            port = str(p.device)
            break
# TODO: change Port automatically
port = "COM3"

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
            #for each serial line, check for type of information
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
while True:
    # Login successful (key-card found)
    if uid is not None:
        # increase login counter
        login_counter = login_counter + 1
        # TODO: just for testing? prints when feeds gets appended
        print("writing to feed")
        # generate Message (Time, UID, LONG, LAT)
        # TODO: convert time.time() into Real Time
        msg_to_store = "Time: " + str(time.time()) + ", UID: " + str(uid) + ", LONG: " + str(longitude) + ", LAT: " +\
                       str(latitude)
        # this is our new event (feed)
        new_event = ecf.next_event("verificationTool/storeFeed", msg_to_store)
        # append the event to our event list
        event_list.append(new_event)
        PCAP.write_pcap('verificationTool', event_list)
        # reset uid to None --> script waits until next login
        uid = None
    # TODO: just for testing? prints all events
    # TODO: some function for syncing with BACnet? needed?
    if login_counter == 4:
        login_counter = 0
        events = PCAP.read_pcap('verificationTool.pcap')
        for event in events:
            event = Event.from_cbor(event)
            print("events: ", event.content.content[1])
