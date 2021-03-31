"""
sendEther.py
Faris Ahmetasevic, Marco Banholzer, Nderim Shatri
This code sends raw ethernet packets to a network by using the scapy library.
"""

from scapy.all import sendp, Raw
from scapy.layers.l2 import Ether
import time
import transport

"""
Sends a message as ethernet packet to the network interface with an ether-type '0x7000'.

:param data: message as payload inside the ethernet packet
:type data: str, bytes, int, ...
:param interface: name of the network interface, for instance 'en0', 'en1', ...
:type: str
"""


def send_message(data, interface):

    ether = Ether(type=0x7000) / Raw(load=data)
    sendp(ether, iface=interface)


"""
Creates the i_have_list and saves it as data.
Sends the i_have_list as ethernet packet to the network interface with an ether-type '0x7000'.

:param interface: name of the network interface, for instance 'en0', 'en1', ...
:type: str
"""


def i_have_sender(interface):

    data = transport.get_i_have_list()
    ether = Ether(type=0x7000)/Raw(load=data)
    sendp(ether, iface=interface)


"""
Sends the created i_want_list as ethernet packet to the network interface with an ether-type '0x7000'.

:param want: the i_want_list which was created
:type: bytes
:param interface: name of the network interface, for instance 'en0', 'en1', ...
:type: str
"""


def i_want_sender(want, interface):

    ether = Ether(type=0x7000) / Raw(load=want)
    time.sleep(5)
    sendp(ether, iface=interface)


"""
Creates the event_list and saves it as data.
Sends the event_list as ethernet packet to the network interface with an ether-type '0x7000'.

:param want: the i_want_list with which the event_list gets created
:type: bytes
:param interface: name of the network interface, for instance 'en0', 'en1', ...
:type: str
"""


def event_sender(want, interface):

    data = transport.get_event_list(want)
    ether = Ether(type=0x7000) / Raw(load=data)
    sendp(ether, iface=interface)