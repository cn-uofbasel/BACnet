from socket import *
import uuid
#import numpy as np
import socket as testsock

class SendEthernet:
    def __init__(self, src, dest, data):
        self.src = src
        self.dest = dest
        # PPPoE Discovery Stage
        self.ether_type = [0x88, 0x63]
        self.payload = data

    def convert_to_hex(self, address):
        addr_arr = []
        add = address.split(":")
        for i in add:
            addr_arr.append(int('0x'+ i, 0))
        return addr_arr

    def make_ethernet_packet(self):
        src_hex = self.convert_to_hex(self.src)
        dst_hex = self.convert_to_hex(self.dest)
        eth_type = self.ether_type
        list_of_lists = [dst_hex, src_hex, eth_type]
        ether_packet = [val for sub_list in list_of_lists for val in sub_list]
        return ether_packet

    def pack(self, byte_sequence):
        return bytes(byte_sequence)


    def send_eth(self, interface="enp9s0"):
    # interface = get your own ethernet interface... linux: ip
        s = socket(AF_PACKET, SOCK_RAW)
        s.bind((interface, 0))
        ether_packet = self.make_ethernet_packet()

        print(self.pack(ether_packet))
        return s.send(self.pack(ether_packet) + self.pack(self.payload))

def get_src_mac():
    # formatiert
    src = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
    return src

if __name__ == '__main__':

    # source device is always the own source, if you send packets
    src = get_src_mac()
    dst = src
    """
    TODO:
    getting information of what kind of data we will send. 
    Defining the kind of destination address
    """
    # print(src)
    data = [0]
    test_connect = SendEthernet(src, dst, data)
    testhex = test_connect.convert_to_hex(src)
    s = test_connect.send_eth()

    print("Sent Ethernet")