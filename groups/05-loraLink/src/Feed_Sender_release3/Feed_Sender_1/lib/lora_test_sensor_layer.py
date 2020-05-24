from lora_feed_layer import Lora_Feed_Layer


class Lora_Test_Sensor_Layer:

    def __init__(self, feed_layer):
        self.feed_layer = feed_layer
        self.feed_layer.subscribe(self.callback_new_events, 1)

    def callback_new_events(self, wired):
        print(wired)
