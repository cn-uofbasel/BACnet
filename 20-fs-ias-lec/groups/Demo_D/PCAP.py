# Simple PCAP reading/writing tool
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import time


class PCAP:

    @classmethod
    def __save_file(cls, path, bytes):
        file = open(path + ".pcap", "wb")
        file.write(bytes)
        file.close()

    @classmethod
    def write_pcap(cls, path_to_file, list_of_events):
        file_bytes = 0xa1b23c4d.to_bytes(4, 'big') + \
                     (2).to_bytes(2, 'big') + \
                     (4).to_bytes(2, 'big') + \
                     (0).to_bytes(4, 'big') + \
                     (0).to_bytes(4, 'big') + \
                     (131071).to_bytes(4, 'big') + \
                     (147).to_bytes(4, 'big')
        maximum_bytes = 131071
        current_payload = 0
        list_of_processed_events = []
        for event in list_of_events:
            event_byte_length = len(event)
            while event_byte_length % 4 != 0:
                event += (0).to_bytes(1, 'big')
                event_byte_length += 1
            if event_byte_length > maximum_bytes:
                continue
            if current_payload + event_byte_length > maximum_bytes:
                PCAP.write_pcap(path_to_file + '0', list(set(list_of_events) - set(list_of_processed_events)))
                PCAP.__save_file(path_to_file, file_bytes)
                return
            current_payload += event_byte_length
            list_of_processed_events.append(event)
            timestamp = time.time_ns()
            time_sec = int(timestamp / 1000000000)
            time_nano = timestamp - time_sec * 1000000000
            event_header = time_sec.to_bytes(4, 'big') + \
                           time_nano.to_bytes(4, 'big') + \
                           len(event).to_bytes(4, 'big') + \
                           len(event).to_bytes(4, 'big')
            file_bytes += event_header + event
        PCAP.__save_file(path_to_file, file_bytes)

    @classmethod
    def read_pcap(cls, path_to_file):
        packets_list = []
        swap_byte_order = False
        file = open(path_to_file, "rb")
        magic_number = file.read(4)
        if magic_number == bytes.fromhex("4d3cb2a1") or magic_number == bytes.fromhex("d4c3b2a1"):
            swap_byte_order = True
        file.read(20)
        timestamp = file.read(8)
        while timestamp != b'':
            packet_length = bytearray(file.read(4))
            if swap_byte_order:
                packet_length.reverse()
            packet_length = int.from_bytes(bytes(packet_length), 'big')
            file.read(4)
            next_event = file.read(packet_length)
            if swap_byte_order:
                tmp_arr = bytearray(next_event)
                for i in range(len(tmp_arr), step=4):
                    tmp_arr[i], tmp_arr[i+1], tmp_arr[i+2], tmp_arr[i+3] = tmp_arr[i+3], tmp_arr[i+2], tmp_arr[i+1], tmp_arr[i]
                next_event = bytes(tmp_arr)
            packets_list.append(next_event)
            timestamp = file.read(8)
        file.close()
        return packets_list
