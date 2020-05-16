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

ether = Ether(type=0x7000)/Raw(load="Faris")  # creates an ethernet packet with raw data
hexdump(ether)  # prints out a hexdump

'''
Sends every ten seconds a packet to the network.
The interface can be returned as an argument e.g "en0", "en1"
'''
while True:

    time.sleep(10)
    sendp(ether, iface=sys.argv[1])
