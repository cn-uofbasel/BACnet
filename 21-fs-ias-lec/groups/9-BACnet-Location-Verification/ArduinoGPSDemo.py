import os
import platform
import shutil
import sys
import threading
import time
import serial.tools.list_ports

from lib import feed, crypto

# running version of ArduinoGPS
# creates feed in new folder data/sender. data is located in same folder where you running the script
# feed gets updated, everytime a login happens (keycard is on reader)
# implemented with demo libraries from BACNet project
# TODO: add SSB? use functions from last year project?
# local stored feed gets outprinted, after every 5 logins.
# TODO: store file on USB-stick, deciding drive (where is usb-stick located)
# TODO: don't overwrite feed on usb-stick, append it!
# if user enter "printUSB" after local stored feed was seen, script will print stored feed on usb-drive



ports = list(serial.tools.list_ports.comports())
port = None

if "macOS" in platform.platform():

    for p in ports:
        if "usbmodem" in p.name:
            port = '/dev/' + str(p.name)
            break


elif "Windows" in platform.platform():
    for p in ports:
        print(p.description, p.name)
        if "USB Serial Device" in p.description:
            port = str(p.device)
            break

port = "COM4"

ser = serial.Serial(port, 9600, timeout=1)

uid, latitude, longitude = None, None, None


class serialReadingThread(threading.Thread):
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        global uid, latitude, longitude
        while True:
            data_raw = ser.readline().decode().strip()
            if data_raw.startswith("x1uid"):
                uid = data_raw[6:]
            elif data_raw.startswith("x2lon"):
                longitude = data_raw[5:]
            elif data_raw.startswith("x3lat"):
                latitude = data_raw[5:]
            else:
                pass


digestmod = "sha256"
sender_h, sender_signer = None, None
receiver_h, receiver_signer = None, None

if not os.path.isdir("data"):
    os.mkdir("data")
if not os.path.isdir("data/sender"):
    os.mkdir("data/sender")
# TODO: change to USB-Stick location
if not os.path.isdir("data/usb-stick"):
    os.mkdir("data/usb-stick")

if not os.path.isfile("data/sender/sender-secret.key"):
    print("create secret key (sender-side)")
    sender_h = crypto.HMAC(digestmod)
    sender_h.create()
    with open("data/sender/sender-secret.key", "w") as f:
        f.write('{\n ' + (',\n '.join(sender_h.as_string().split(','))[1:-1]) + '\n}')
        sender_signer = crypto.HMAC(digestmod, sender_h.get_private_key())
print("Reading Secret key (sender-side)")
with open("data/sender/sender-secret.key", 'r') as f:
    print("created sender key pair")
    key = eval(f.read())
    sender_h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
    sender_signer = crypto.HMAC(digestmod, bytes.fromhex(sender_h.get_private_key()))
print("create sender feed")
sender_feed = feed.FEED(fname="data/sender/sender-feed.pcap", fid=sender_h.get_feed_id(), signer=sender_signer,
                        create_if_notexisting=True, digestmod=digestmod)


def store_uid_and_long_lat_in_feed():
    print("writing message to feed")
    sender_feed.write(["ArduinoGPS/locTool", time.time(), uid, latitude, longitude])


# TODO: change to USB-Location
def store_feed_on_usb():
    shutil.copy("data/sender/sender-feed.pcap", "data/usb-stick/sender-feed.pcap")


# TODO: needed?, sync usb with sender folder or with 'new' folder (like receiver folder)
def sync_usb_with_folder():
    print("get data from usb to pc")
    shutil.copy("data/usb-stick/sender-feed.pcap", "data/receiver/sender-feed.pcap")


def print_feeds(sender_feed_1):
    print("\n Logins:\n")
    logins = []
    for event in sender_feed_1:
        if event.content()[0] == "ArduinoGPS/locTool":
            logins.append({"time": event.content()[1], "UID": event.content()[2], "LAT": event.content()[3],
                           "LONG": event.content()[4]})
    logins.sort(key=lambda msg: msg["time"])
    print("starting...")
    for log in logins:
        print(log["time"], ", ", log["UID"], ", ", log["LAT"], ", ", log["LONG"])
    print("...ending")


t1 = serialReadingThread(1, "t1")
t1.start()
test_calc = 0
uid_temp = uid
while True:

    if uid is not None:
        test_calc = test_calc + 1
        store_uid_and_long_lat_in_feed()
        uid = None
    if os.path.isdir("data/usb-stick"):
        # TODO:dont overwrite feed on usb --> append it!
        store_feed_on_usb()
    if test_calc % 5 == 0 and test_calc != 0:
        test_calc = 0
        print("printing locally stored feed")
        print_feeds(sender_feed)
        if os.path.isdir("data/usb-stick"):
            in_msg = input("Please Enter 'printUSB' for printing feed from BACnet or 'quit')")
            if in_msg == "printUSB":
                usb_feed = feed.FEED(fname="data/usb-stick/sender-feed.pcap", fid=sender_h.get_feed_id(),
                                     signer=sender_signer,
                                     create_if_notexisting=True, digestmod=digestmod)
                print_feeds(usb_feed)
            elif in_msg != "quit":
                print("invalid input, waiting for logins...")
