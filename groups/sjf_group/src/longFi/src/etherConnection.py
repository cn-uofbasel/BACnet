import cbor2
import time
from logSync import database_transport as transport
from longFi.src import sendEther
from longFi.src import receiveEther

import threading
from logSync import database_sync as ds
"""
Class HasPackets() has all of the packets and creates an i_have_list with tem.
It receives the i_want_list of the other class NeedsPackets(), which says what packets have to be send to 
the other user.
It creates an event_list and sends it to the other user.  
"""
wait_time = 3

class EtherUpdater:

    """
    This function sends and receives the necessary packets to the other user.

    :param interface: name of the network interface, for instance 'en0', 'en1', ...
    :type: str
    """

    def __init__(self, interface):

        self.__event_list_to_send = []

        print("\nServer started broadcasting at interface " + str(interface))

        s_thread = SenderThread(case="message", interface=interface, packet="broadcasting_looking_for_other_device")
        info_request = None
        s_thread.run()
        while info_request is None \
                or info_request != b'requesting_infos_of_all_pcap_files\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            print("Broadcasting...")
            info_request = receiveEther.receive(interface)
        s_thread.set_ACK_True()

        # Server receives information about the request
        print(info_request)

        i_want_list = None
        s_thread = SenderThread(case="have", interface=interface)
        s_thread.run()
        while i_want_list is None:
            sendEther.i_have_sender(interface)
            print("\nRequest was accepted, sending \"I HAVE\"-list and waiting for\"I WANT\"-list...")
            i_want_list = receiveEther.receive(interface)
        print("\n\"I WANT\"-list received...")
        s_thread.set_ACK_True()

        count = 0
        while count < 5:
            sendEther.event_sender(i_want_list, interface)
            print("\nSending event list...")
            time.sleep(wait_time)
            count += 1


    """
    This is a list of the needed extensions of log files that have to be sent (already serialized)! 
    This method can be used by the other groups to transfer the information as they have to (QR code, etc...)
    """

    def get_packet_to_send_as_bytes(self):
        return self.__event_list_to_send


"""
Class NeedsPackets() wants the missing packets from the i_have_list of the other user.
It creates the i_want_list with the missing packets and sends it to the HasPackets() class.
It receives an event_list and and the missing packets.  
"""


class EtherRequester:

    """
    This function sends and receives the necessary packets to the other user.

    :param interface: name of the network interface, for instance 'en0', 'en1', ...
    :type: str
    """

    def __init__(self, interface):

        interface = str(interface)
        self.__received_package_as_events = []

        print("\nWaiting for broadcaster...")
        request_acceptation = None
        while request_acceptation is None \
                or request_acceptation != b'broadcasting_looking_for_other_device\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            request_acceptation = receiveEther.receive(interface)

        print("\nRequesting a list the information about the files and their sequence number...\n")

        received_data = None
        s_thread = SenderThread(case="message", interface=interface, packet="requesting_infos_of_all_pcap_files")
        s_thread.run()
        while received_data is None:
            received_data = receiveEther.receive(interface)
        s_thread.set_ACK_True()
        packet, self.__list_of_needed_extensions = transport.get_i_want_list(received_data)
        print("\n\"I HAVE\"-list received...")

        event_list = None
        s_thread = SenderThread(case="want", interface=interface, packet=packet)
        s_thread.run()
        print("\nSending \"I WANT\"-list...")

        while event_list is None:
            # TODO: maybe bug, when event list is empty
            event_list = receiveEther.receive(interface)
        s_thread.set_ACK_True()
        print("\nEvent list received...")

        if not cbor2.dumps(event_list):
            print("\nYou are already up-to-date!")

        self.__received_package_as_events = event_list

    """
    This is a list of the received log extensions that can be appended to the files.
    """

    def get_packet_to_receive_as_bytes(self):
        return self.__received_package_as_events

    def get_list_of_needed_extensions(self):
        return self.__list_of_needed_extensions


class myEtherThread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        if self.name == "EtherRequester":
           etherrequest = EtherRequester("Ethernet 4")
           ds.sync_database(etherrequest.get_list_of_needed_extensions(), etherrequest.get_packet_to_receive_as_bytes())
        elif self.name == "EtherUpdater":
            EtherUpdater("Ethernet 4")


class SenderThread(threading.Thread):
    def __init__(self, case, interface, packet):
        threading.Thread.__init__(self)
        self.case = case
        self.interface = interface
        self.packet = packet
        self.ACK = False

    def run(self):
        while not self.ACK:
            if self.case == "message":
                sendEther.send_message(self.packet, self.interface)
            elif self.case == "have":
                sendEther.i_have_sender(self.interface)
            elif self.case == "want":
                sendEther.i_want_sender(self.packet, self.interface)
            time.sleep(wait_time)

    def set_ACK_True(self):
        self.ACK = True