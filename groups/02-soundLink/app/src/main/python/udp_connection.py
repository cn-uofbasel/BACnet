import socket
import cbor
import time
from logSync import database_transport as transport # for databases
# from logSync import transport as transport # for pcap files

buffSize = 8192


class Server:
    def __init__(self, port):
        port = int(port)

        # Create the socket and bind to host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setblocking(False)
        self.__event_list_to_send = []

        print("Server started broadcasting at port" + str(port))
        connected = True
        while connected:
            self.socket.sendto(b'broadcasting_looking_for_other_device', ('<broadcast>', port))
            time.sleep(3)
            try:
                # Server receives information about the request
                info_request, address = self.socket.recvfrom(buffSize)  # 4
                if info_request == str.encode('requesting_infos_of_all_pcap_files'):
                    self.socket.sendto(transport.get_i_have_list(), address)  # 4
                    print("Request accepted, list of files sent.")
                    connected = False
            except:
                print('Waiting for request...')

        self.socket.setblocking(True)
        self.socket.sendto(transport.get_event_list(self.socket.recv(buffSize)), address)  # 11
        print("\"I WANT\"-list received...")
        print("Sending event list...")
        self.socket.close()

    """
    This is a list of the needed extensions of log files that have to be sent (already serialized)! 
    This method can be used by the other groups to transfer the information as they have to (QR code, etc...)
    """

    def get_packet_to_send_as_bytes(self):
        return self.__event_list_to_send


class Client:
    def __init__(self, port):
        # Create the UDP socket and request the log extensions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 2
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(('', int(port)))

        broadcasting = True
        while broadcasting:
            print("Waiting for broadcaster...")
            msg, address = self.socket.recvfrom(buffSize)
            if msg == b'broadcasting_looking_for_other_device':
                print("Requesting a list the information about the files and their sequence number...")
                self.socket.sendto(str.encode('requesting_infos_of_all_pcap_files'), address)  # 3
                broadcasting = False

        self.__received_package_as_events = []
        packet, self.__list_of_needed_extensions = transport.get_i_want_list(self.socket.recv(buffSize))
        print("\"I HAVE\"-list received...")

        self.socket.sendto(packet, address)  # 8
        print("Sending \"I WANT\"-list...")

        event_list = self.socket.recv(buffSize)  # 11
        print("Event list received...")

        if not cbor.dumps(event_list):
            print("You are already up-to-date!")

        self.__received_package_as_events = event_list
        self.socket.close()

    """
    This is a list of the received log extensions that can be appended to the files.
    """
    def get_packet_to_receive_as_bytes(self):
        return self.__received_package_as_events

    def get_list_of_needed_extensions(self):
        return self.__list_of_needed_extensions
