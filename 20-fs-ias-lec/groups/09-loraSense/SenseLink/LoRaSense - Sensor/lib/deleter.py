import os

class Deleter():
    def __init__(self):
        try:
            print("PCAPS DELETED")
            os.remove("Sensor_Feed.pcap")
            os.remove("Control_Feed.pcap")
        except:
            print("UNABLE TO DELETE PCAPS.")
            print(os.listdir())
            pass