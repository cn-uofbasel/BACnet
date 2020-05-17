from lora_link_layer import Lora_Link_Layer
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


try:
    os.remove("Feed.pcap")
    os.remove("secret.key")
except:
    pass


class Lora_Sync_Layer:

    def __init__(self):
        self.link_layer = Lora_Link_Layer(self.receive_msg_cb)

        #self.events_list = [[0, "Hallo1"], [1, "Hallo2"], [2, "Hallo3"], [3, "Hallo4"]]

        _thread.start_new_thread(self.send_gossip, ())

        self.feed = feed.FEED("Feed.pcap", None, None, True)




    def receive_msg_cb(self, msg):
        self.decode_msg(msg)

    def decode_msg(self, msg):
        control_int = msg[0] * 1
        #msg = str(msg, "utf-8")

        if (control_int == 0):
            print("New Gossip")
            feed_len_int = msg[1] * 256 + msg[2]
            self.handle_incoming_gossip(feed_len_int)

        elif (control_int == 1):
            print("New Event")
            data = msg[1:len(msg)]
            self.handle_incoming_event(data)


    def handle_incoming_gossip(self, msg):
        print("Handle incoming gossip")
        if (msg < len(self.feed)):
            print("Sending event " + str(msg))

            search = msg + 1
            for e in self.feed:
                signature1 = e.get_metabits(self.signer.get_sinfo())
                print(str(e))
                if (e.seq == search):
                    e_trans = e
                    print("Sync Layer | Sending event:" + str(e.content()))
                    signature = e_trans.get_metabits(self.signer.get_sinfo())
                    e_wired = e_trans.to_wire(signature)
                    print(len(e_wired))
                    control_b = (1).to_bytes(1, 'big')
                    self.send_event(control_b + e_wired)
                    #wait random time before sending


    def handle_incoming_event(self, msg):
        incoming_event = msg
        print(str(incoming_event))

        #if (incoming_event[0] == len(self.events_list)): #check if already appended
            #self.events_list.append(incoming_event)
            #print("Acquired event:" + str(incoming_event[0]))
        self.feed._append(msg)

        print("Sync Layer | Feed length:" + str(len(self.feed)))
        #if data is needed automatically append data.
        #else if it could be used later, store to a buffer.
        #check if data usefull and append to feeds or append to buffer if event in between is missing


    def send_event(self, msg):
        self.link_layer.append_msg_to_pipeline(msg, False)
        #events einzeln senden? Wie gross können einzelne Nachrichten sein?

    def send_gossip(self):
        while True:
            random = int.from_bytes(os.urandom(1), "big")
            gossip_waiting = 5 + math.floor(random/256*5)
            print(gossip_waiting)
            time.sleep(gossip_waiting)

            control_b = (0).to_bytes(1, 'big')
            feed_len = len(self.feed)
            feed_len_b = feed_len.to_bytes(2, 'big')
            gossip = control_b + feed_len_b

            #a = str(gossip[0], 'big')
            #b = str(gossip[1:2], 'big')
            feed_len_int = feed_len_b[0] * 256 + feed_len_b[1]
            control_int = control_b[0] * 1
            print("Sync Layer | Send gossip: " + str(control_int) + " " + str(feed_len_int))


            #print("Sync Layer | Feed lenght: " + str(len(self.feed)))
            #msg = "gssp-bc//" + str(feed_len)
            #print(msg)

            self.link_layer.append_msg_to_pipeline(gossip, False)



    def create_keyfile(self):
        h = crypto.HMAC("md5")
        h.create()
        print("# new HMAC_MD5: share it ONLY with trusted peers")
        print('{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}')
        keyfile = '{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}'

        f = open('secret.key', 'w')
        f.write(keyfile)
        f.close()

    def load_keyfile(self, fn):
        with open(fn, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'hmac_md5':
            #fid = bytes.fromhex(key['feed_id'])
            fid = binascii.unhexlify(key['feed_id'])
            #signer = crypto.HMAC256(bytes.fromhex(key['private']))
            signer = crypto.HMAC("md5", binascii.unhexlify(key['private']))
        return fid, signer
