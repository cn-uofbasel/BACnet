import serial
import threading
import time

ser = serial.Serial('/dev/tty.usbmodem11401', 9600, timeout=1)
#USB PORT FOR MAC (varies when reconnected...)
#WINDOWS WOULD MOST LIKELY BE 'COM3'

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


