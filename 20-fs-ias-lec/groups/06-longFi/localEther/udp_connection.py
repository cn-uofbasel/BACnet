import socket
import cbor2
import time
import connect
from logSync import database_transport as transport # for databases
# from logSync import transport as transport # for pcap files

class hasPackets:
    def __init__(self, interface):

        connect.sender(transport.get_i_have_list(), interface)  # 4

        print("Request accepted, list of files sent.")
        print('Waiting for request...')

        data = connect.receiver(interface)
        connect.sender(transport.get_event_list(data), interface)  # 11
        print("\"I WANT\"-list received...")
        print("Sending event list...")

    """
    This is a list of the needed extensions of log files that have to be sent (already serialized)! 
    This method can be used by the other groups to transfer the information as they have to (QR code, etc...)
    """

    def get_packet_to_send_as_bytes(self):
        return self.__event_list_to_send


class needsPackets:
    def __init__(self, interface):

        broadcasting = True
        #while broadcasting
        #broadcasting = False

        self.__received_package_as_events = []
        data = connect.receiver(interface)
        packet, self.__list_of_needed_extensions = transport.get_i_want_list(data)
        print("\"I HAVE\"-list received...")

        connect.sender(packet, interface)  # 8
        print("Sending \"I WANT\"-list...")

        event_list = connect.receiver(interface)  # 11
        print("Event list received...")

        if not cbor2.dumps(event_list):
            print("You are already up-to-date!")

        self.__received_package_as_events = event_list

    """
    This is a list of the received log extensions that can be appended to the files.
    """
    def get_packet_to_receive_as_bytes(self):
        return self.__received_package_as_events

    def get_list_of_needed_extensions(self):
        return self.__list_of_needed_extensions
