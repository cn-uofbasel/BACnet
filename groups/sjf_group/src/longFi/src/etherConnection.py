import cbor2
import time
from logSync import database_transport as transport
from longFi.src import sendEther
from longFi.src import receiveEther


"""
Class HasPackets() has all of the packets and creates an i_have_list with tem.
It receives the i_want_list of the other class NeedsPackets(), which says what packets have to be send to 
the other user.
It creates an event_list and sends it to the other user.  
"""


class HasPackets:

    """
    This function sends and receives the necessary packets to the other user.

    :param interface: name of the network interface, for instance 'en0', 'en1', ...
    :type: str
    """

    def __init__(self, interface):

        self.__event_list_to_send = []

        print("\nServer started broadcasting at interface " + str(interface))

        time.sleep(5)
        sendEther.send_message("broadcasting_looking_for_other_device", interface)

        # Server receives information about the request
        info_request = receiveEther.receive(interface)
        print(info_request)
        if info_request == b'requesting_infos_of_all_pcap_files\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':

            time.sleep(5)  # delay to have an asynchronous conversation between the users
            sendEther.i_have_sender(interface)

            print("\nRequest accepted, list of files sent.")

        print('\nWaiting for request...')

        msg = receiveEther.receive(interface)

        time.sleep(5)
        sendEther.event_sender(msg, interface)

        print("\n\"I WANT\"-list received...")
        print("\nSending event list...")

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


class NeedsPackets:

    """
    This function sends and receives the necessary packets to the other user.

    :param interface: name of the network interface, for instance 'en0', 'en1', ...
    :type: str
    """

    def __init__(self, interface):

        interface = str(interface)

        print("\nWaiting for broadcaster...")
        msg = receiveEther.receive(interface)

        if msg == b'broadcasting_looking_for_other_device\x00\x00\x00\x00\x00\x00\x00\x00\x00':

            print("\nRequesting a list the information about the files and their sequence number...\n")
            time.sleep(5)
            sendEther.send_message("requesting_infos_of_all_pcap_files", interface)

        self.__received_package_as_events = []
        data = receiveEther.receive(interface)

        packet, self.__list_of_needed_extensions = transport.get_i_want_list(data)
        print("\n\"I HAVE\"-list received...")

        time.sleep(5)
        sendEther.i_want_sender(packet, interface)

        time.sleep(2)
        print("\nSending \"I WANT\"-list...")

        event_list = receiveEther.receive(interface)
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