from network import LoRa
#from gossip_layer import Gossip
import socket
import time
import os
import _thread
import binascii

class Lora_Link_Layer:

    def __init__(self, receive_msg_cb):
        print("Initializing Link Layer...")

        self.receive_msg_cb = receive_msg_cb
        self.msg_buffer_list = []

        self.incoming_cts_key = -1
        self.wait = False #Use other name, e.g. wait_for_channel
        self.wait_time = 0
        #use int instead of boolean. If multiple cts/rts arrive sum.

        self.lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.s.setblocking(False)
        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)

        self.lora_mac_address_b = binascii.hexlify(self.lora.mac())
        self.lora_mac_address = str(self.lora_mac_address_b, "utf-8")

        _thread.start_new_thread(self.process_msg_pipeline, ())


    def get_lora_mac(self):
        return self.lora_mac_address


    def lora_cb(self, lora):
        events = lora.events()
        if events & LoRa.RX_PACKET_EVENT:

            msg = self.s.recv(250)
            #print(msg)
            #unpack message and pass meta information (like mac address or protocol) as parameter
            #meta, data = self.unpack_frame(msg.decode("utf-8"))
            #msg_utf8 = data
            #msg_1 = msg.decode("utf-8")
            #print('Link Layer: Lora packet received. ' + str(msg_utf8, "utf-8"))

            #if (msg_1.startswith("cts")):
            #    self.handle_incoming_cts(msg_1)

            #elif (msg_1.startswith("rts")):
            #    self.handle_incoming_rts(msg_1)
                #send cts. what if cts gets lost? Ignore? CSMA sending messages
                #only one rts at a time. identify rts if it is repeated.
            #else:
            print('Link Layer: Passing received data to Network Layer')
            self.receive_msg_cb(msg)

        #if events & LoRa.TX_PACKET_EVENT:
            #print('Lora packet sent')


    def append_msg_to_pipeline(self, msg, use_ca):
        self.msg_buffer_list.append([msg, use_ca])

        #Buffer Länge definieren und Nachrichten verwerfen oder auf Teilpackete aufteilen.
        #Time on air -> vielfaches (zufällig) warten, falls Kanal nicht frei.

    def process_msg_pipeline(self):
        while True:
            if (len(self.msg_buffer_list) > 0):
                msg_and_ca = self.msg_buffer_list.pop(0)
                msg = msg_and_ca[0]
                use_ca = msg_and_ca[1]

                self.lora_send_csma_ca(msg, use_ca)

                time.sleep(1)


    def lora_send_csma_ca(self, msg, use_ca):
        if (use_ca):
            print("Link Layer: using CA")

            #do not send rts if wait = true
            rts_random_key_b = binascii.hexlify(os.urandom(2))
            rts_random_key = str(rts_random_key_b, "utf-8")
            rts = "rts." + rts_random_key

            while not (rts_random_key == self.incoming_cts_key): #and not wait. Probably?
                #maximum repetition
                if not self.wait:
                    self.lora_send_csma(rts)
                    print("Link Layer: Waiting for cts. expected: " + str(rts_random_key) + " received: " + str(self.incoming_cts_key))
                else:
                    print("Link Layer: Waiting..." + str(self.wait_time))
                #change delay randomly/exponential
                #Wie lange warten? cts soll nicht mit nächstem rts versuch überlagert werden?
                time.sleep(2)

        else:
            print("Link Layer: NOT using CA")

        #blocking function
        self.lora_send_csma(msg)


    def lora_send_csma(self, msg):
        #Semtech LoRa: High sensitivity  -111 to -148dBm (Datasheet: https://semtech.my.salesforce.com/sfc/p/#E0000000JelG/a/2R0000001OKs/Bs97dmPXeatnbdoJNVMIDaKDlQz8q1N_gxDcgqi7g2o)
        while not self.lora.ischannel_free(-100,100):
            #max rep.
            print("Link Layer: channel not free")

        print("Link Layer: channel free (CSMA). Sending data...")
        self.lora_send(msg)


    def lora_send(self, msg):
        #frame = self.pack_frame("c", msg)
        frame = msg
        print("Link Layer | Sending data: " + str(frame))
        self.s.send(frame)


    def handle_incoming_cts(self, incoming_cts):
        print("Link Layer: CTS received. Key=" + incoming_cts)
        self.incoming_cts_key = str(incoming_cts.split(".")[1], "utf-8")
        #Important: Wait also if CTS is for other lora. Use MAC adress as identifier
        #Combine with incoming RTS


    def handle_incoming_rts(self, incoming_rts):
        incoming_rts_key = str(incoming_rts.split(".")[1], "utf-8")
        print("Link Layer: RTS received. Key=" + incoming_rts_key)
        #send cts. what if cts gets lost? Ignore? CSMA sending messages
        #only one rts at a time. identify rts if it is repeated.
        #check if rts is new. Problem: other lora did not receive cts. Important: Waiting time
        if (not self.wait):
            _thread.start_new_thread(self.wait_timer, (5,))
            print("Link Layer: CTS other lora. Waiting for other lora...")
            #save mac address of other lora and wait until packet from this lora arrived or max
            cts = "cts." + incoming_rts_key
            #self.lora_send_csma(cts.encode("utf-8"))
            self.lora_send_csma(cts)


    def wait_timer(self, wait_time):
        self.wait_time = wait_time
        self.wait = True
        print("Wait timer")

        while self.wait_time > 0:
            time.sleep(1)
            self.wait_time = self.wait_time - 1
            print(str(self.wait_time))

        self.wait = False


    #This field states whether the frame is a data frame or it is used for control functions like error and flow control or link management etc.
    def pack_frame(self, type, data):
        #Use single bits for control and 8 bytes for MAC without delimiters. character delimiters can cause problems and need much space.
        frame = type + "::" + self.get_lora_mac() + "::" + data
        print("Link Layer:" + frame)
        return frame


    def unpack_frame(self, frame):
        meta = [frame.split("::")[0], frame.split("::")[1]]
        data = frame.split("::")[2]
        return meta, data
