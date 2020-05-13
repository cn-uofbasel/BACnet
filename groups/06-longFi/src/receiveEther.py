'''
receiveEther.py
Faris Ahmetasevic, Marco Banholzer, Nderim Shatri
This code receives raw ethernet packets, which were sent to a network using the scapy library.
'''

from scapy.all import conf
import sys
import struct


'''
This function returns the converted information of the packets. 
'''
def ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('!6s6s2s', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), get_protocol(proto), data[14:]


'''
This function returns the converted MAC-addresses.  
'''
def get_mac_addr(bytes_addr):
    bytes_str = map('{:02x}'.format, bytes_addr)
    mac_address = ':'.join(bytes_str).upper()
    return mac_address


'''
This function returns the converted protocol.
'''
def get_protocol(bytes_proto):
    bytes_str = map('{:02x}'.format, bytes_proto)
    protocol = ''.join(bytes_str).upper()
    return protocol


'''
Within the loop the program filters every packet with the protocol "0x7000" and prints the information.
'''
while True:

    sock = conf.L2socket(iface=sys.argv[1])  # scapy socket which connects to a network e.g "en0", "en1"
    pkt = bytes(sock.recv())  # the packets get read and converted to bytes
    if pkt[12:14] != b'\x70\x00':  # only the packets with protocol "0x7000" get filtered
        continue

    dest_mac, src_mac, eth_proto, data = ethernet_frame(pkt)  # calls the function to convert the information of the packets

    print('\nEthernet Frame:')
    print("Destination MAC: {}".format(dest_mac))  # prints the converted destination MAC-address
    print("Source MAC: {}".format(src_mac))  # prints the converted source MAC-address
    print("Protocol: {}".format(eth_proto))  # prints the converted protocol
    print("Packet: ", data)  # prints the payout
