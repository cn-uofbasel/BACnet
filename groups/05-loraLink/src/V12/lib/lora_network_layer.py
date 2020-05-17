from lora_link_layer import Lora_Link_Layer
import os
import math
import time
import _thread
import json


class Gossip:

    def __init__(self):
        self.link_layer = Lora_Link_Layer(self.receive_msg_cb)

        #self.events_list = ["1", "2", "3"]
        self.events_list = [[0, "Hallo1"], [1, "Hallo2"], [2, "Hallo3"], [3, "Hallo4"], [4, "Hallo3"], [5, "Hallo4"]]
        #length = str(len(events_list))

        self.incoming_data = []
        self.incoming_ack = []

        #learn rsii from incoming messages
        _thread.start_new_thread(self.gssp_send_broadcast, ())


    def receive_msg_cb(self, msg):
        self.decode_msg(msg.decode('utf-8'))

    def decode_msg(self, msg):
        if (msg.startswith("gssp-bc")):
            print("New Broadcast")
            data = msg.split("//")[1]
            self.gssp_handle_bc(data)

        elif (msg.startswith("gssp-get")):
            print("New Get")
            data = msg.split("//")[1]
            self.gssp_handle_get(data)

        elif (msg.startswith("gssp-data")):
            print("New Feed")
            data = msg.split("//")[1]
            self.gssp_handle_data(data)

        elif (msg.startswith("gssp-ack")):
            print("New ack")
            data = msg.split("//")[1]
            self.gssp_handle_ack(data)



    def gssp_handle_bc(self, msg):
        #start thread: -> send get (repeat) -> receive data (multiple) -> send ack (repeat)
        print("Handle incoming_broadcast")
        if (int(msg) > len(self.events_list)):
            _thread.start_new_thread(self.thread_acquire_event, (len(self.events_list),))

    def gssp_handle_get(self, msg):
        #start thread: -> send data (repeat) -> receive ack (multiple?)
        if (int(msg) < len(self.events_list)):
            event = self.events_list[int(msg)]
            self.gssp_send_feed(json.dumps(event))
            #_thread.start_new_thread(self.thread_deliver_event, (int(msg),))

    def gssp_handle_data(self, msg):
        self.incoming_data.append(json.loads(msg))
        print(self.incoming_data)
        #check if data usefull and append to feeds
        #check if data already received (but ack lost) and send ack again

    def gssp_handle_ack(self, msg):
        self.incoming_ack.append(int(msg))


    def thread_acquire_event(self, event_nr):
        acquiring_event = True
        while acquiring_event:
            self.gssp_send_get(event_nr)
            print("Acquiring event:" + str(event_nr))
            time.sleep(20)

            for event in self.incoming_data:
                print(str(event))
                print(str(event_nr))
                if (event[0] == event_nr): #check if already appended
                    if (len(self.events_list) == event_nr):
                        self.events_list.append(event)
                        self.gssp_send_ack(event_nr)
                        acquiring_event = False
                        print("Acquired event:" + str(event_nr))
                    else:
                        acquiring_event = False
        print(str(self.events_list))
        #send ack if data received -> delete data, keep meta
        #if data is sent again, send ack again
        #options start new thread or use the same
        #what if ack gets lost? data is sent again! send ack again! keep in mind, which data received.


    def thread_deliver_event(self, meta):
        delivering_event = True
        while delivering_event:
            print("Delivering event")
            event = self.events_list[meta]
            self.gssp_send_feed(json.dumps(event))
            time.sleep(20)

            for ack in self.incoming_ack:
                if (ack == event_nr):
                    delivering_event = False
                    print("Delivered event:" + str(event_nr))


    def gssp_send_get(self, event_nr):
        msg = "gssp-get//" + str(event_nr)
        self.link_layer.append_msg_to_pipeline(msg, True)

    def gssp_send_ack(self, event_nr):
        msg = "gssp-ack//" + str(event_nr)
        self.link_layer.append_msg_to_pipeline(msg, True)

    def gssp_send_feed(self, msg):
        msg = "gssp-data//" + str(msg)
        self.link_layer.append_msg_to_pipeline(msg, True)
        #events einzeln senden? Wie gross können einzelne Nachrichten sein?

    def gssp_send_broadcast(self):
        i = 0
        while True:
            random = int.from_bytes(os.urandom(1), "big")
            gossip_waiting = 20 + math.floor(random/256*5)
            print(gossip_waiting)
            time.sleep(gossip_waiting)

            ##feed_length = len(events_list)
            msg = "gssp-bc//" + str(len(self.events_list))
            print(msg)
            #msg = msg.encode('utf-8')

            i = i + 1
            self.link_layer.append_msg_to_pipeline(msg, True)
        #measure time for transmitting max. payload.
        #use a random. uos.urandom(n) Return a bytes object with n random bytes.
        #Collision avoidance: RTS und CTS nur vor langen Nachrichten. Länge der Nachricht angeben.
        #Alle anderen Nachrichten sind nur kurz und werden periodisch wiederholt.
        #Wichtig: In welchen Intervallen sollen Gossip Nachrichten versendet werden?
        #Für gewisse Nachrichten ACKs anfordern.
