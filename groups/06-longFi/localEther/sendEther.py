'''
sendEther.py
Faris Ahmetasevic, Marco Banholzer, Nderim Shatri
This code sends raw ethernet packets to a network by using the scapy library.
'''

from scapy.all import sendp, Raw
from scapy.layers.l2 import Ether
from scapy.all import hexdump
import sys
import time

def send_len(packet, interface):

    length = len(packet)
    length = length * 1000
    length = hex(length)
    print("LENGTH", length)
    ether_len = Ether(type=0x7000)/Raw(load=length)
    sendp(ether_len, iface=interface)

def send_packet(packet, interface):

    for i in range(len(packet)):

        ether = Ether(type=0x7000)/Raw(load=packet[i])
        time.sleep(3)
        sendp(ether, iface=interface)
