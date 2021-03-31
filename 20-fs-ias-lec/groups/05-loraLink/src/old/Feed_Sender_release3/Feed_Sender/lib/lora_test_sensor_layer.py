from lora_feed_layer import Lora_Feed_Layer


class Lora_Test_Sensor_Layer:

    def __init__(self, feed_layer):
        self.feed_layer = feed_layer
        self.feed_layer.create_event(self.feed_layer.get_sensor_feed_fid(), "['chat', 'Hi Bob 1']")
        self.feed_layer.create_event(self.feed_layer.get_sensor_feed_fid(), "['chat', 'Hi Bob 2']")
        self.feed_layer.create_event(self.feed_layer.get_sensor_feed_fid(), "['chat', 'Hi Bob 3']")
        self.feed_layer.subscribe(self.callback_new_events, 1)

    def callback_new_events(self, wired):
        print(wired)
