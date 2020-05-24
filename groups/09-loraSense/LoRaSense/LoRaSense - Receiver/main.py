import socket
import time
import os
import _thread
import binascii
import network
import select
import _thread
from network import LoRa


lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
lora_s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_s.setblocking(False)


wlan = network.WLAN(mode=network.WLAN.STA)
nets = wlan.scan()
for net in nets:
    print(str(net))

wlan.connect('CasaSalsi', auth=(network.WLAN.WPA2, 'S@lsi1968'), timeout=5000)

print(wlan.mac())

while not wlan.isconnected():
    time.sleep(1)
print("WLAN CONNECTED")

wlan_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
wlan_s.bind(["192.168.1.141", 5200])
print(wlan.ifconfig())

inputs = [wlan_s]

def wifi_send(msg):
    print("Wifi Sending data: " + str(msg))
    wlan_s.sendto (msg , ( "192.168.1.123" , 5200 ))

def wifi_listen():
    while True:
        time.sleep(1)
        readable, writable, exceptional = select.select(inputs, [], [])
        for sock in readable:
            if sock == wlan_s:
                buf = wlan_s.recv(250)
                print("Wifi: Data received. Sending via LoRA.")
                print(buf)
                lora_send_csma(buf)

def lora_cb(lora):
    events = lora.events()
    if events & LoRa.RX_PACKET_EVENT:
        msg = lora_s.recv(250)
        print('LoRa: Data received. Sending via Wifi.')
        print(msg)
        wifi_send(msg)

lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=lora_cb)

def lora_send_csma(msg):
        #Semtech LoRa: High sensitivity  -111 to -148dBm (Datasheet: https://semtech.my.salesforce.com/sfc/p/#E0000000JelG/a/2R0000001OKs/Bs97dmPXeatnbdoJNVMIDaKDlQz8q1N_gxDcgqi7g2o)
        while not lora.ischannel_free(-100,100):
            #max rep.
            print("LoRa CSMA: channel not free")

        print("LoRa CSMA: channel free (CSMA). Sending data...")
        lora_send(msg)

def lora_send(msg):
    #frame = self.pack_frame("c", msg)
    frame = msg
    print("LoRa Sending data: " + str(frame))
    lora_s.send(frame)

_thread.start_new_thread(wifi_listen, ())
