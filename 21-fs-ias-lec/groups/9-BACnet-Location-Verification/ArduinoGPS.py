import platform
import sys
import threading
import time
import serial.tools.list_ports
from eventCreationTool import EventCreationTool


sys.path.append(".BACnet/demo/lib")

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
ecf = EventCreationTool.EventFactory()
master_feed_id = EventCreationTool.EventFactory.get_feed_id(ecf)
print("master = ", master_feed_id)
#first_event = ecf.create_first_event("locTool", feedCtrl.generate_random_feed_id())

#def read_last_feed():
 #   if not os.path.isdir("data/testTool"):
  #      os.mkdir("data/testTool")

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


t1 = serialReadingThread(1, "t1")
t1.start()
test_calc = 0
while True:
    time.sleep(10)
    print("UID: ", uid)
    print("Latitude: ", latitude)
    print("Longitude: ", longitude)
    #if uid is not None:
     #   new_event = ecf.next_event("locTool/send", uid, latitude, longitude)
    #else:
     #   test_calc = test_calc + 1
      #  if test_calc % 2 == 0:
       #     print("...")

