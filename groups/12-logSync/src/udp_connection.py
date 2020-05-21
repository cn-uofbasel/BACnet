import socket
import cbor2
import main
import pcap
import sync
import time

buffSize = 2048


class Server:
    def __init__(self, port):
        port = int(port)

        # Create the socket and bind to host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setblocking(False)
        self.__package_to_send_as_bytes = []

        print("Server started broadcasting at port" + str(port))
        connected = True
        while connected:
            self.socket.sendto(b'broadcasting_looking_for_other_device', ('<broadcast>', port))
            time.sleep(3)
            try:
                # Server receives information about the request
                info_request, address = self.socket.recvfrom(buffSize)  # 4
                if info_request == str.encode('requesting_infos_of_all_pcap_files'):
                    list_of_files = sync.create_list_of_files('udpDir/')  # 4
                    self.socket.sendto(cbor2.dumps(list_of_files), address)  # 4
                    print("Request accepted, list of files sent.")
                    connected = False
            except:
                print('Waiting for request...')
        self.socket.setblocking(True)

        # Server receives the list with the necessary log extensions
        list_with_necessary_files = cbor2.loads(self.socket.recv(buffSize))  # 9

        if not list_with_necessary_files:
            print("All up-to-date on client's side. Closing the socket.")
            self.socket.close()
            return

        # Server sends the log extensions one by one
        for file_info in list_with_necessary_files:
            packet = pcap.get_meta_and_cont_bits('udpDir/' + file_info[0], file_info[2])  # 10
            self.__package_to_send_as_bytes.append(cbor2.dumps(packet))
            #############################################################################################
            self.socket.sendto(cbor2.dumps(packet), address)  # 11
            print("Sending extensions from seq=" + str(file_info[2]) + " on of " + file_info[0] + "...")
            #############################################################################################

        self.socket.close()

    """
    This is a list of the needed extensions of log files that have to be sent (already serialized)! 
    This method can be used by the other groups to transfer the information as they have to (QR code, etc...)
    """

    def get_packet_to_send_as_bytes(self):
        return self.__package_to_send_as_bytes


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

        # Contains a list of all files of the server side and their sequence number
        requested_list = cbor2.loads(self.socket.recv(buffSize))  # 5 & 6
        print("List received...")

        self.__list_of_needed_extensions = sync.compare_files(requested_list)  # 7
        self.socket.sendto(cbor2.dumps(self.__list_of_needed_extensions), address)  # 8
        print("Files compared and sending information about the needed extensions...")
        #############################################################################################
        # Client receives log extensions one by one and appends them
        for file_info in self.__list_of_needed_extensions:
            event = self.socket.recv(buffSize)  # 11
            self.__received_package_as_events.append(event)

        print("Packets received!")
        #############################################################################################
        self.socket.close()

    """
    This is a list of the received log extensions that can be appended to the files.
    """
    def get_packet_to_receive_as_bytes(self):
        return self.__received_package_as_events

    def get_list_of_needed_extensions(self):
        return self.__list_of_needed_extensions
