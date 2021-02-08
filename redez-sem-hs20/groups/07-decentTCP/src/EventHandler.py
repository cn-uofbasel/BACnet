from eventCreationTool.EventCreationTool import EventFactory
from eventCreationTool.Event import Event

class EventHandler:
    eventfactory = None

    def __init__(self, eventFactory):
        self.eventfactory = eventFactory

    def addEvent(self, type, content):
        return self.eventfactory.next_event(type, content)

    def getEventContent(self, event):
        return Event.from_cbor(Event.get_as_cbor(event)).content()

    def read_pcap(self, path_to_file):
        packets_list = []
        swap_byte_order = False
        file = open(path_to_file, "rb")
        magic_number = file.read(4)
        if magic_number == bytes.fromhex("4d3cb2a1") or magic_number == bytes.fromhex("d4c3b2a1"):
            swap_byte_order = True
        file.read(20)
        timestamp = file.read(8)
        while timestamp is not b'':
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