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
        self.msg_buffer_list = [["msg1", True], ["msg2", False]]

        self.incoming_cts_key = -1
        self.cts_other_lora = False

        self.lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.s.setblocking(False)
        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)

        # self.lora_mac_address = int.from_bytes(self.lora.mac(), "big")
        self.lora_mac_address_hex = binascii.hexlify(self.lora.mac())
        self.lora_mac_address = str(self.lora_mac_address_hex)

        _thread.start_new_thread(self.lora_send_csmaca, ())


    def get_lora_mac(self):
        return self.lora_mac_address


    def lora_cb(self, lora):
        events = lora.events()
        if events & LoRa.RX_PACKET_EVENT:

            print('Link Layer: Lora packet received')

            msg = self.s.recv(64)
            #unpack message and pass meta information (like mac address or protocol) as parameter
            msg_utf8 = msg.decode("utf-8")

            if (msg_utf8.startswith("cts")):
                self.handle_incoming_cts(msg_utf8)

            elif (msg_utf8.startswith("rts")):
                self.handle_incoming_rts(msg_utf8)
                #send cts. what if cts gets lost? Ignore? CSMA sending messages
                #only one rts at a time. identify rts if it is repeated.
            else:
                print('Link Layer: Passing received data to Network Layer')
                self.receive_msg_cb(msg)


            #print(self.lora.stats())
        #if events & LoRa.TX_PACKET_EVENT:
            #print('Lora packet sent')


    def send_msg_buffer(self, msg, use_rts):
        #for long packets activate RTS (length of packet). Use Random byte sequence to identify corresponding CTS
        #pack msg in link_layer package with mac adress

        #use tuple [msg, rts_true] and append

        #frame = self.pack_frame("d", msg)
        self.msg_buffer_list.append([msg, use_rts])
        #check if Thread is not empty and start thread
        #Is a thread necessary? Probably use cts if many msgs in buffer. for multiple events send_msg_buffer_array
        #layers are independent with thread. Non-blocking function

        #Thread lock necessary if lora send does pop?
        #Buffer Länge definieren und Nachrichten verwerfen.
        #Wie gross können Nachrichten sein? Max payload 64 bytes?
        #Time on air -> vielfaches (zufällig) warten, falls Kanal nicht frei.


    def lora_send_csmaca(self):
        #Thread pause falls buffer leer?
        while True:
            if (not self.cts_other_lora):

                if (len(self.msg_buffer_list) > 0):
                    msg_and_rts = self.msg_buffer_list.pop(0)
                    msg = msg_and_rts[0]
                    use_rts = msg_and_rts[1]

                    #check if rts necessary. Long message or many messages.
                    #blocking function rts_and_wait_for_cts
                    if (use_rts):
                        print("using RTS")
                        self.rts_and_wait_for_cts(True)
                    else:
                        print("not using RTS")

                    #CSMA
                    self.lora_send_csma(msg)

                time.sleep(1)

            else:
                time.sleep(5)
                self.cts_other_lora = False

        #Wie gross können Datenpackete tatsächlich sein? Was muss unser Netzwerk können?


    def lora_send_csma(self, msg):
        wait_for_channel = True

        while wait_for_channel:
            if self.ischannel_free():
                print("Link Layer: channel free")
                wait_for_channel = False
            else:
                print("Link Layer: channel not free")

        print("Link Layer: sending data")
        self.s.send(msg)


    def ischannel_free(self):
        return self.lora.ischannel_free(-100,100)
        #Signal to noise ratio erheben. Use: lora.stats()
        #Idea: Scan network for a time interval and calculate ratio
        #Semtech LoRa: High sensitivity  -111 to -148dBm (Datasheet: https://semtech.my.salesforce.com/sfc/p/#E0000000JelG/a/2R0000001OKs/Bs97dmPXeatnbdoJNVMIDaKDlQz8q1N_gxDcgqi7g2o)


    def rts_and_wait_for_cts(self, cts_active):
        #cts_random_key = int.from_bytes(os.urandom(2), "big")
        cts_random_key = str(binascii.hexlify(os.urandom(2)), "utf-8")

        while not (cts_random_key == self.incoming_cts_key):
            #maximum repetition
            rts = "rts." + cts_random_key
            self.s.send(rts.encode('utf-8'))
            print("Link Layer: Waiting for cts. expected: " + str(cts_random_key) + " received: " + str(self.incoming_cts_key))
            #change delay randomly/exponential
            #Wie lange warten? cts soll nicht mit nächstem rts versuch überlagert werden?
            time.sleep(2)

        self.cts_random_key = -1


    def handle_incoming_rts(self, incoming_rts):
        incoming_rts_key = int(msg_utf8.split(".")[1])
        print("Link Layer: RTS received. Key=" + incoming_rts_key)
        #send cts. what if cts gets lost? Ignore? CSMA sending messages
        #only one rts at a time. identify rts if it is repeated.
        #check if rts is new. Problem: other lora did not receive cts. Important: Waiting time
        self.cts_other_lora = True
        print("Link Layer: CTS other lora. Waiting for other lora...")
        #save mac address of other lora and wait until packet from this lora arrived or max
        cts = "cts." + str(incoming_rts_key)
        self.lora_send_csma(cts.encode("utf-8"))


    def handle_incoming_cts(self, incoming_cts):
        #Possible ValueError: invalid syntax for integer with base 10. Probably if data is changed during transmition
        #Use hexcode instead
        print("Link Layer: CTS received. Key=" + incoming_cts)
        self.incoming_cts_key = str(incoming_cts.split(".")[1], "utf-8")


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
