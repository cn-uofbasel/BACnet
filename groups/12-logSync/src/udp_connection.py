import socket
import cbor2
import main
import pcap
import sync

buffSize = 1024


class Server:
    def __init__(self):
        # TODO: change hardcoded host and port
        host = 'localhost'
        port = 8080

        # Create the socket and bind to host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))  # 1

        print("Server started: <" + host + ">:<" + str(port) + ">")
        print('Waiting for query...')

        # Server receives information about the request
        info_request, address = self.socket.recvfrom(buffSize)  # 4
        if info_request == str.encode('requesting_infos_of_all_pcap_files'):
            list_of_files = main.create_list_of_files('dir1/')  # 4
            self.socket.sendto(cbor2.dumps(list_of_files), address)  # 4
            print("Request accepted, list of files sent.")
        else:
            print("Request denied.")
            return
        # Server receives the list with the necessary log extensions
        list_with_necessary_files = cbor2.loads(self.socket.recv(buffSize))  # 9

        if not list_with_necessary_files:
            print("All up-to-date on client's side. Closing the socket.")
            self.socket.close()
            return

        # Server sends the log extensions one by one
        for file_info in list_with_necessary_files:
            packet = pcap.get_meta_and_cont_bits('dir1/' + file_info[0], file_info[2])  # 10
            self.socket.sendto(cbor2.dumps(packet), address)  # 11
            print("Sending extensions of " + file_info[0] + "...")

        self.socket.close()


class Client:
    def __init__(self):
        # TODO: change hardcoded host and port
        address = ('localhost', 8080)

        # Create the UDP socket and request the log extensions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 2
        self.socket.sendto(str.encode('requesting_infos_of_all_pcap_files'), address)  # 3

        # Contains a list of all files of the server side and their sequence number
        requested_list = cbor2.loads(self.socket.recv(buffSize))  # 5 & 6

        compared_files = sync.compare_files(requested_list)  # 7
        self.socket.sendto(cbor2.dumps(compared_files), address)  # 8

        # Client receives log extensions one by one and appends them
        for file_info in compared_files:
            event = cbor2.loads(self.socket.recv(buffSize))  # 11
            synchro = sync.Sync('dir2/' + file_info[0])

            # If the file has to be created, the key is needed
            if file_info[2] == 0:
                synchro.sync_files(key=file_info[1], new_files=True, event_list=event)  # 12
            else:
                synchro.sync_files(event_list=event)  # 12
            print("Synchronising " + file_info[0] + "...")

        print("Finished synchronising!")
        self.socket.close()
