import serial
import threading
import time
import serial.tools.list_ports
import platform

ports = list(serial.tools.list_ports.comports())
port = None

if "macOS" in platform.platform():
    
    for p in ports:
        if "usbmodem" in p.name:
            port = '/dev/' + str(p.name)
            break


elif "Windows" in platform.platform():
    for p in ports:
        if "USB Serial Device" in p.description:
            port = str(p.device)
            break


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

t1 = serialReadingThread(1,"t1")
t1.start()

while True:
    time.sleep(10)
    print("UID: ", uid)
    print("Latitude: ", latitude)
    print("Longitude: ", longitude)


