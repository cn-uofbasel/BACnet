from lora_link_layer import Lora_Link_Layer
from lora_feed_layer import Lora_Feed_Layer
import os
import math
import time
import _thread
import json

import crypto
import feed
import binascii
import event
import pcap
import sys
from struct import unpack


class Lora_Sync_Layer:

    def __init__(self, feed_layer, sensor_layer):
        self.link_layer = Lora_Link_Layer(self.receive_msg_cb)
        self.feed_layer = feed_layer
        self.sensor_layer = sensor_layer
        self.sensor_fid = self.sensor_layer.getFid()
        self.sensor_cfid = self.sensor_layer.getCfid()

        self.currentSwitch = self.sensor_layer.switchState()

        #self.events_list = [[0, "Hallo1"], [1, "Hallo2"], [2, "Hallo3"], [3, "Hallo4"]]

        self.verbose = 1 # write a lot of comments
        self.gossip_wait = int(self.sensor_layer.getFrequency()/ 2)
        self.send_gossip()


    def receive_msg_cb(self, msg):
        self.decode_msg(msg)

    def decode_msg(self, msg):
        control_int = msg[0] * 1
        fid = msg[1:9]

        #msg = str(msg, "utf-8")

        if (control_int == 0):
            print("Sync Layer | New gossip received")
            feed_len_int = msg[9] * 256 + msg[10]
            self.handle_incoming_gossip(feed_len_int,fid)

        elif (control_int == 1):
            print("Sync Layer | New event received")
            feed_len_int = msg[9] * 256 + msg[10]
            data = msg[11:len(msg)]
            self.handle_incoming_event(feed_len_int,data,fid)


    def handle_incoming_gossip(self, msg,fid):
        print("Sync Layer | Handle incoming gossip")
        if (msg < self.feed_layer.get_feed_length(fid)):
            print("Sync Layer | Sending event nr " + str(msg))

            search = msg + 1

            e_wired = self.feed_layer.get_wired_event(fid, search)
            print("Sync Layer | Sending event: Length=" + str(len(e_wired)))
            control_b = (1).to_bytes(1, 'big')
            feed_len_b = search.to_bytes(2, 'big')

            #wait random time before sending
            random = int.from_bytes(os.urandom(1), "big")
            gossip_waiting = self.gossip_wait + math.floor(random/256*5)
            if self.verbose:
                print('send_gossip waiting for '+ str(gossip_waiting))
            time.sleep(gossip_waiting)

            self.send_event(control_b + fid + feed_len_b + e_wired)


    def handle_incoming_event(self, seq,msg,fid):
        print("Sync Layer | Event data: " + str(msg))

        #if (incoming_event[0] == len(self.events_list)): #check if already appended
            #self.events_list.append(incoming_event)
            #print("Acquired event:" + str(incoming_event[0]))
        #fid = self.feed_layer.get_sensor_feed_fid()
        self.feed_layer.append(fid,seq, msg)

        print("Sync Layer | Feed length:" + str(self.feed_layer.get_feed_length(fid)))
        #if data is needed automatically append data.
        #else if it could be used later, store to a buffer.
        #check if data usefull and append to feeds or append to buffer if event in between is missing


    def send_event(self, msg):
        self.link_layer.append_msg_to_pipeline(msg, False)
        #events einzeln senden? Wie gross können einzelne Nachrichten sein?

    def send_gossip(self):
        while True:

            # get current feeds
            [pcap_list,fid_list] = self.feed_layer.get_fid_list()

            random = int.from_bytes(os.urandom(1), "big")
            gossip_waiting = int(self.sensor_layer.getFrequency()/ 2)
            self.feed_layer.create_event(self.sensor_fid, self.sensor_layer.createEvent())

            for fi in fid_list:
                if self.verbose:
                    print('send_gossip waiting for '+ str(gossip_waiting))
                time.sleep(gossip_waiting)
                control_b = (0).to_bytes(1, 'big')
                feed_len = self.feed_layer.get_feed_length(fi)
                feed_len_b = feed_len.to_bytes(2, 'big')

                gossip = control_b + fi + feed_len_b

                if self.verbose:
                    [name,type] = self.feed_layer.get_name(fi)
                    print("Sync Layer | Send gossip: 0 " + name + " " + str(feed_len))


            # control_b = (0).to_bytes(1, 'big')
            # fid = self.feed_layer.get_sensor_feed_fid()
            # feed_len = self.feed_layer.get_feed_length(fid)
            # feed_len_b = feed_len.to_bytes(2, 'big')
            #
            # gossip = control_b + feed_len_b
            #
            # #a = str(gossip[0], 'big')
            # #b = str(gossip[1:2], 'big')
            # feed_len_int = feed_len_b[0] * 256 + feed_len_b[1]
            # control_int = control_b[0] * 1

            #print("Sync Layer | Feed lenght: " + str(len(self.feed)))
            #msg = "gssp-bc//" + str(feed_len)
            #print(msg)

                self.link_layer.append_msg_to_pipeline(gossip, False)
