import lib.lorasense as lorasense
from lora_sync_layer import Lora_Sync_Layer
from lora_feed_layer import Lora_Feed_Layer
from lora_test_sensor_layer import Lora_Test_Sensor_Layer

try:
    os.remove("Sensor_Feed.pcap")
    os.remove("Control_Feed.pcap")
except:
    pass
self.feed_layer = Lora_Feed_Layer()
self.test_sensor_layer = LoraSense(feed_layer)
self.sync_layer = Lora_Sync_Layer(feed_layer)