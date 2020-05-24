from lora_feed_layer import Lora_Feed_Layer
import os


class Lora_Test_Sensor_Layer:

    def __init__(self, feed_layer):
        self.feed_layer = feed_layer

        # Get sensor feed id (so far hard coded in lora_feed_layer)
        fid = self.feed_layer.get_sensor_feed_fid()
        print("Sensor Feed ID is: "+ str(fid))

        # Get control feed id (so far hard coded in lora_feed_layer)
        cfid = self.feed_layer.get_control_feed_fid()
        print("Control Feed ID is: "+ str(cfid))

        # Create a new event: create_event(fid,payload)
        #   creates an event in cbor format, and adds it to pcap file in cbor format
        self.feed_layer.create_event(fid, "['Temperature', '30C']")
        self.feed_layer.create_event(fid, "['Test', '30C']")
        # self.feed_layer.create_event(fid, "['Temperature', '25C']")
        # self.feed_layer.create_event(fid, "['Temperature', '25C']")
        # self.feed_layer.create_event(fid, "['Temperature', '25C']")
        #self.feed_layer.create_event(fid, "['Temperature', '25C']")
        #self.feed_layer.create_event(fid, "['Temperature', '25C']")
        #self.feed_layer.create_event(fid, "['Temperature', '25C']")
        #self.feed_layer.create_event(fid, "['Temperature', '10C']")
        #self.feed_layer.create_event(fid, "['Temperature', '30C']")
        self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        # self.feed_layer.create_event(cfid, "['Intervall', '2s']")
        #self.feed_layer.create_event(cfid, "['Intervall', '5s']")

        # Get feed ids of all stored logs
        [pcap_list,fid_list] = self.feed_layer.get_fid_list()

        # subscribe to a feed:  needs callback and fid
        subscribe_state = self.feed_layer.subscribe_sensor_feed(self.callback_new_events)

        # get event from log: get_event_content(feed ID, sequence number)
        seq = 0
        e = self.feed_layer.get_event_content(fid, seq)
        print(e)

        # get last event from control log: get_event_content(feed ID, sequence number)
        seq = self.feed_layer.get_feed_length(cfid)-1   # latest sequence number = length-1
        e = self.feed_layer.get_event_content(cfid, seq)
        print(e)

        # get and print log
        f = self.feed_layer.get_feed_content(fid)
        f = self.feed_layer.get_feed_content(cfid)
        #print(os.listdir())

        # validate
        # may come later

        # unsubscribe # may come later
        #subscribe_state = self.feed_layer.unsubscribe(self.callback_new_events, 1)

        # delete feed
        #d = self.feed_layer.delete_feed(fid)
        #d = self.feed_layer.delete_feed(cfid)


    def callback_new_events(self, wired):
        print('wired: '+ str(wired))
