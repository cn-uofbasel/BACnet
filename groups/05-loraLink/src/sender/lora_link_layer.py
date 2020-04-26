from network import LoRa
#from gossip_layer import Gossip
import socket
import time
import _thread

class MeshNetwork:

    def __init__(self, receive_msg_cb):
        print("starting network...")

        self.receive_msg_cb = receive_msg_cb
        self.msg_buffer_list = ["msg1", "msg2", "msg3", "msg4"]
        self.wait_for_cts = True
        self.cts = False

        self.lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.s.setblocking(False)
        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self.lora_cb)

        _thread.start_new_thread(self.lora_send, ())


    def ischannel_free(self):
        return self.lora.ischannel_free(-100,100)
        #Signal to noise ratio erheben. Use: lora.stats()
        #Semtech LoRa: High sensitivity  -111 to -148dBm (Datasheet: https://semtech.my.salesforce.com/sfc/p/#E0000000JelG/a/2R0000001OKs/Bs97dmPXeatnbdoJNVMIDaKDlQz8q1N_gxDcgqi7g2o)

    def lora_send(self):
        #Thread pause falls buffer leer?
        while True:
            if (len(self.msg_buffer_list) > 0):
                msg = self.msg_buffer_list.pop(0)
                #check if rts necessary
                self.cts = False

                while not self.cts:
                    #maximum repetition
                    self.s.send("rts")
                    print("waiting for cts")
                    time.sleep(2)

                #Problem if channel not free
                if (self.ischannel_free()):
                    self.s.send(msg)
                    print("sending data")
                else:
                    print("ischannel_free=false")

            time.sleep(1)
        #Wie gross können Datenpackete tatsächlich sein? Was muss unser Netzwerk können?

    def send_msg_buffer(self, msg):
        #for long packets activate RTS (length of packet). Use Random byte sequence to identify corresponding CTS
        self.msg_buffer_list.append(msg)
        #Thread lock necessary if lora send does pop?
        #Buffer Länge definieren und Nachrichten verwerfen.
        #Wie gross können Nachrichten sein? Max payload 64 bytes?
        #Time on air -> vielfaches (zufällig) warten, falls Kanal nicht frei.


    def lora_cb(self, lora):
        events = lora.events()
        if events & LoRa.RX_PACKET_EVENT:
            #detect RTS and answer with packets
            #detect CTS for self and others and send or wait
            msg = self.s.recv(64)
            msg_utf8 = msg.decode("utf-8")
            if (msg_utf8.startswith("cts")):
                self.cts = True
                print("cts received")
            else:
                print('Lora packet received')

            self.receive_msg_cb(msg)
            #print(self.lora.stats())
        #if events & LoRa.TX_PACKET_EVENT:
            #print('Lora packet sent')
