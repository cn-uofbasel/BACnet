from struct import *


testpayload = b'\x01\xbb\x82\x8c\xcd\x21\xbf\x2d\x52\xf3\xd0\xf6\xb0\x10\x00\x84\x1e\xb5\x00\x00\x01\x01\x08\x0a\xc2\x12\x8b\x52\x0e\x08\xaf\x35\x00\x20\x01\x01\x05\x0a\x52\xf3\xd1\x15\x52\xf3\xd1\x16'


def isset(k):
    if k == "1":
        return "Set"
    elif k == "0":
        return "Not Set"
    return "N/A"


class TCPPacket():

    def __init__(self, payload):
        self.payload = payload

    def unpack_tcp(self):
        (self.src_port, self.dst_port) = unpack('!HH', self.payload[0:4])
        (self.seq_no, self.ack_no) = unpack('!II', self.payload[4:12])
        (self.flags, self.window_size_value, self.check_sum, self.urgent_pointer) = unpack('!HHHH', self.payload[12:20])
        print("Source Port: " + str(self.src_port))
        print("Destionation Port: " + str(self.dst_port))
        print("Sequence number (raw): " + str(self.seq_no))
        print("Acknowledgment number (raw): " + str(self.ack_no))
        self.print_flags()
        print("Window size value: " + str(self.window_size_value))
        print("Checksum: " + ''.join('0x%01x' % i for i in [self.check_sum]))
        print("Urgent pointer: " + str(self.urgent_pointer))

    def print_flags(self):
        header_len = int(bin(self.flags)[2:6], 2) * 4
        int_flags = bin(self.flags)[6:22]
        nonce = int_flags[3]
        cog_win_red = int_flags[4]
        ecn_echo = int_flags[5]
        urgent = int_flags[6]
        acknowledgment = int_flags[7]
        push = int_flags[8]
        reset = int_flags[9]
        syn = int_flags[10]
        fin = int_flags[11]
        print(str(bin(self.flags)[2:6]) + " .... = Header Length: " + str(header_len) + " bytes (" + str(
            header_len // 4) + ")")
        print("Flags: " + ''.join('0x%03x' % i for i in [int(int_flags, 2)]))
        print(str(int_flags[0:3]) + ". .... .... = Reserved: Not set")
        print("..." + str(nonce) + " .... .... = Nonce: " + isset(nonce))
        print(".... " + str(cog_win_red) + "... .... = Congestion Window Reduced (CWR): " + isset(cog_win_red))
        print(".... ." + str(ecn_echo) + ".. .... = ECN-Echo: " + isset(ecn_echo))
        print(".... .." + str(urgent) + ". .... = Urgent: " + isset(urgent))
        print(".... ..." + str(acknowledgment) + " .... = Acknowledgment: " + isset(acknowledgment))
        print(".... .... " + str(push) + "... = Push: " + isset(push))
        print(".... .... ." + str(reset) + ".. = Reset: " + isset(reset))
        print(".... .... .." + str(syn) + ". = Syn: " + isset(syn))
        print(".... .... ..." + str(fin) + " = Fin: " + isset(fin))

        # print(reserverd)


toto = TCPPacket(testpayload)
toto.unpack_tcp()
