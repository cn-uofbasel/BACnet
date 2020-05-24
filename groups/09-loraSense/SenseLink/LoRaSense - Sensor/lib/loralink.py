from senselink import SenseLink
from lora_sync_layer import Lora_Sync_Layer
from lora_feed_layer import Lora_Feed_Layer
from lora_test_sensor_layer import Lora_Test_Sensor_Layer

class LoraLink:
    def __init__(self, sda="P3", scl="P4", als="P20", frequency=10, ssid = "", pw ="", debug=0): 
        try:
            os.remove("Sensor_Feed.pcap")
            os.remove("Control_Feed.pcap")
        except:
            pass
        self.feed_layer = Lora_Feed_Layer()
        self.sensor_layer = SenseLink(sda=sda, scl=scl, als=als,ssid=ssid, pw=pw, frequency=frequency, debug=debug, feed_layer=self.feed_layer)
        self.sync_layer = Lora_Sync_Layer(self.feed_layer, self.sensor_layer)