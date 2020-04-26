from lora_link_layer import MeshNetwork
import os
import math
import time
import _thread

events_list = ["1", "2", "3", "4"]

class Gossip:

    def __init__(self):
        self.mesh = MeshNetwork(self.receive_msg_cb)
        #self.events_list = ["1", "2", "3"]
        length = str(len(events_list))

        #learn rsii from incoming messages
        _thread.start_new_thread(self.gossiping, ())


    def receive_msg_cb(self, msg):
        self.decode_msg(msg.decode('utf-8'))

    def decode_msg(self, msg):
        if (msg.startswith("gossip:")):
            #check if gossip ist new to this node.
            print("New Gossip")
            print(msg)
        elif (msg.startswith("feed:")):
            print("New Feed")
        #define a Message format.

    def send_events(self, msg):
        self.mesh.lora_send(msg)
        #events einzeln senden? Wie gross können einzelne Nachrichten sein?
        #Vor langen Nachrichten wird ein RTS versendet und ein CTS erwartet.
        #ACK für gewisse Packete anfordern. Diese Packete zwischenspeichern und mit einer Packetnummer (Zufallszahl oder durchnummerieren) versetzen.

    def gossiping(self):
        i = 0

        #Offer Feeds (Name and length)

        #measure time for transmitting max. payload.
        #use a random. uos.urandom(n) Return a bytes object with n random bytes.
        #Collision avoidance: RTS und CTS nur vor langen Nachrichten. Länge der Nachricht angeben.
        #Alle anderen Nachrichten sind nur kurz und werden periodisch wiederholt.
        #Wichtig: In welchen Intervallen sollen Gossip Nachrichten versendet werden?
        #Für gewisse Nachrichten ACKs anfordern.

        while True:
            random = int.from_bytes(os.urandom(1), "big")
            gossip_waiting = 10 + math.floor(random/256*5)
            print(gossip_waiting)
            time.sleep(gossip_waiting)

            feed_length = len(events_list)
            msg = "gossip:loraID=1||" + str(feed_length)
            print(msg)
            msg = msg.encode('utf-8')

            i = i + 1
            self.mesh.send_msg_buffer(msg)
