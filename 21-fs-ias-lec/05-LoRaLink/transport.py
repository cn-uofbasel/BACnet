import queue
import hashlib
import os
import json
from datetime import datetime

LOG = 'log.txt'

class TransportLayer():
    """
    This class is the interface between application layer and link layer.

    The transport layer is connected to the application layer via two queues and with two other queues to the link
    layer. Determines if the input is handed over to the application layer or to the link layer. It also creates and
    maintains the append only log.

    Attributes:
        msg_rx_queue (Queue): Queue that contains received messages from the application layer.
        msg_tx_queue (Queue): Queue that contains messages that are handed over to application layer.
        rx_queue (Queue): Queue that contains received messages from link layer.
        tx_queue (Queue): Queue that contains messages that are handed over to link layer.
        identity (str): Hardcoded identity of each device.
        duplicates (dict): Contains hash values of received and transmitted messages, if hash is contained message is
                           neither transmitted nor handed to application layer.
        sequence_number (int): Current sequence number of the personal log.
    """

    msg_rx_counter = 0
    msg_tx_counter = 0
    rx_counter = 0
    tx_counter = 0
    msg_rx_queue: queue.Queue = None
    msg_tx_queue: queue.Queue = None
    rx_queue: queue.Queue = None
    tx_queue: queue.Queue = None

    def __init__(self):
        self.identity = 'C'  # oder B oder C oder D oder E oder F
        print("ID = " + self.identity)
        self.duplicates = {}
        self.initialize_append_only_log()
        self.sequence_number = self.get_sequence_number()

    def register_msg_Rx(self, msg_qRx: queue.Queue):
        self.msg_rx_queue = msg_qRx

    def register_msg_Tx(self, msg_qTx: queue.Queue):
        self.msg_tx_queue = msg_qTx

    def register_qRx(self, qRx: queue.Queue):
        self.rx_queue = qRx

    def register_qTx(self, qTx: queue.Queue):
        self.tx_queue = qTx

    def get_sequence_number(self) -> int:
        """
        Returns the last sequence number occurring in own log.

        Returns:
            int: last sequence number in own log.
        """

        with open(LOG) as json_log:
            log_file = json.load(json_log)
            return int(log_file[str(self.identity)][-1]['sequence'])

    def initialize_append_only_log(self):
        """
        If the log file is not existing it is created and initialized with it's own log containing an initialization
        entry.

        Returns:
            None
        """

        if not os.path.isfile("/home/pi/tmp/loralink_test/bacnet-lora-sms/log.txt"):
            log = {str(self.identity): []}
            log[str(self.identity)].append({
                'sequence': int(0),
                'receiver': str(self.identity),
                'timestamp': '',
                'data': 'Initialise log of {ident}'.format(ident=self.identity)
            })

            with open(LOG, 'w') as outfile:
                json.dump(log, outfile, indent=4)

    def append_to_linklayer(self):
        """
        Receives message from application layer, packs it for the link layer, adds the hash value of the message to the
        duplicates dictionary, appends the message to the own log and transmits it to the link layer.

        Returns:
            None

        """

        segment = self.msg_tx_queue.get()
        try:
            if self.check_destination_segment(segment):
                # When message is to yourself print it don't use unnecessary bandwidth and directly give back to
                # application layer.
                msg = self.unpack_segment(segment)
                msg_done = str(msg[0] + ";" + msg[1])
                self.msg_rx_queue.put(msg_done)
            else:
                packed_segment = self.pack_segment(segment)
                hash_value = self.calculate_md5(packed_segment)
                self.duplicates[str(hash_value)] = 'true'
                self.append_to_root_log(packed_segment)
                self.tx_queue.put(packed_segment)
        except Exception:
            print("Error while transmitting msg (wrong formatius maximus)")
            return

    def append_to_root_log(self, msg: str) -> None:
        """
        Appends message to the personal log after it was received from application layer before it gets transmitted to
        the link layer.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            None
        """

        unpacked = self.unpack(msg)
        with open(LOG) as json_log:
            log_file = json.load(json_log)
            log_file[str(self.identity)].append({
                'sequence': unpacked[1],
                'receiver': unpacked[4],
                'timestamp': unpacked[3],
                'data': unpacked[5]
            })
            with open(LOG, 'w') as outfile:
                json.dump(log_file, outfile, indent=4)

    # if flag 0 = normal message
    def append_to_log(self, unpacked_msg: tuple) -> None:
        """
        Appends a message that is received to the general log. If the message is from an unknown sender a new dictionary
        key is created for the sender with an initialization entry. If the sequence numbers are consecutive the message
        is added to the log.

        Args:
            unpacked_msg (tuple): Tuple containing all components of a transport layer packet.

        Returns:
            None
        """

        with open(LOG) as json_log:
            log_file = json.load(json_log)
            if not str(unpacked_msg[0]) in log_file:
                log_file[str(unpacked_msg[0])] = []
                log_file[str(unpacked_msg[0])].append({
                    'sequence': int(0),
                    'receiver': str(unpacked_msg[0]),
                    'timestamp': '',
                    'data': 'Initialise log of {ident}'.format(ident=str(unpacked_msg[0]))
                })
                with open(LOG, 'w') as outfile:
                    json.dump(log_file, outfile, indent=4)
                if unpacked_msg[2] == "2":
                    entry = self.unpack_request_response(unpacked_msg)
                    if self.check_sequence_num_order_int(entry[0], unpacked_msg, log_file):
                        log_file[str(unpacked_msg[0])].append({
                            'sequence': entry[0],
                            'receiver': entry[1],
                            'timestamp': entry[2],
                            'data': entry[3]
                        })
                        with open(LOG, 'w') as outfile:
                            json.dump(log_file, outfile, indent=4)

                if self.check_sequence_num_order(unpacked_msg, log_file):
                    log_file[str(unpacked_msg[0])].append({
                        'sequence': unpacked_msg[1],
                        'receiver': unpacked_msg[4],
                        'timestamp': unpacked_msg[3],
                        'data': unpacked_msg[5]
                    })
                    with open(LOG, 'w') as outfile:
                        json.dump(log_file, outfile, indent=4)
                else:
                    log_request = self.create_log_request(unpacked_msg[0])
                    self.tx_queue.put(log_request)

            else:
                if unpacked_msg[2] == "2":
                    entry = self.unpack_request_response(unpacked_msg)
                    if self.check_sequence_num_order_int(entry[0], unpacked_msg, log_file):
                        log_file[str(unpacked_msg[0])].append({
                            'sequence': entry[0],
                            'receiver': entry[1],
                            'timestamp': entry[2],
                            'data': entry[3]
                        })
                        with open(LOG, 'w') as outfile:
                            json.dump(log_file, outfile, indent=4)

                if self.check_sequence_num_order(unpacked_msg, log_file):
                    log_file[str(unpacked_msg[0])].append({
                        'sequence': unpacked_msg[1],
                        'receiver': unpacked_msg[4],
                        'timestamp': unpacked_msg[3],
                        'data': unpacked_msg[5]
                    })
                    with open(LOG, 'w') as outfile:
                        json.dump(log_file, outfile, indent=4)
                else:
                    log_request = self.create_log_request(unpacked_msg[0])
                    self.tx_queue.put(log_request)

    @staticmethod
    def check_sequence_num_order(unpacked_msg: tuple, log_file: dict) -> bool:
        """
        Checks if the received message is consecutive to the last entry in the log of the sender.

        Args:
            unpacked_msg (tuple): Tuple containing all components of a transport layer packet.
            log_file (dict): Dictionary containing all logs of known sender.

        Returns:
            boolean
        """

        return int(log_file[str(unpacked_msg[0])][-1]['sequence']) == (int(unpacked_msg[1]) - 1)

    @staticmethod
    def check_sequence_num_order_int(sequence: int, unpacked_msg: tuple, log_file: dict) -> bool:
        """
        Checks if the received message is consecutive to the last entry of the log, used for Response Messages.

        Args:
            sequence (int): Sequence number of the response.
            unpacked_msg (tuple): Tuple containing all components of a transport layer packet.
            log_file (dict): Dictionary containing all logs of known sender.

        """

        return int(log_file[str(unpacked_msg[0])][-1]['sequence']) == (int(sequence) - 1)

    def append_to_application_layer(self):
        """
        Checks if message received from link layer is at it's destination and hasn't been received yet. If so it is
        unpacked and passed to the application layer. If not at the right destination and it hasn't been received yet it
        is sent back to the link layer.

        Returns:
            None
        """

        msg = self.rx_queue.get()
        try:
            unpacked = self.unpack(msg)
            hashval = self.calculate_md5(msg)
            if not self.already_received(hashval):
                if unpacked[2] == "2":
                    self.append_to_log(unpacked)
                if self.check_if_request(unpacked) and unpacked[4] == self.identity:
                    self.create_request_response(unpacked)
                else:
                    self.append_to_log(unpacked)
                    if self.check_destination(msg):
                        if not unpacked[2] == "2":
                            unpacked_msg = unpacked[0] + ";" + unpacked[5]
                            self.msg_rx_queue.put(unpacked_msg)
                    else:
                        self.tx_queue.put(msg)
        except Exception:
            print("Error while parsing message on transport layer")
            return

    # ???
    def get_identity(self):
        return self.identity

    def pack_segment(self, msg: str) -> str:
        """
        Finish implementation first
        """

        flag = 0
        self.sequence_number += 1
        segment = self.identity + ';' + str(self.sequence_number) + ";" + str(flag) + ";" + msg
        return segment

    @staticmethod
    def unpack(msg: str) -> tuple:
        """
        Unpacks a message into its components.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            tuple: Tuple containing all components of a transport layer packet.
        """

        sender = msg.split(";")[0]
        seq_num = msg.split(";")[1]
        flag = msg.split(";")[2]
        time = msg.split(";")[3]
        receiver = msg.split(";")[4]
        if flag == "2":
            message = msg.split(";")[5:]
        else:
            message = msg.split(";")[5]
        return sender, seq_num, flag, time, receiver, message

    # Checks if device is intended receiver
    def check_destination(self, msg: str) -> bool:
        """
        Checks if the packet has reached its destination.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            boolean
        """

        unpacked = self.unpack(msg)
        return unpacked[4] == self.identity

    def check_destination_segment(self, msg: str) -> bool:
        """
        Checks if the message was addressed to the sender itself.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            boolean
        """

        unpacked = self.unpack_segment(msg)
        return unpacked[0] == self.identity

    @staticmethod
    def unpack_segment(msg: str) -> tuple:
        """
        Unpack method for segment in case the message was addressed to the sender himself.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            tuple: Tuple containing all components of a application layer packet.
        """

        receiver = msg.split(";")[1]
        data = msg.split(";")[2]
        return receiver, data

    def already_received(self, hash_val: str) -> bool:
        """
        Checks if the message has already been received before (used to avoid echoes). If not received before it is
        added to the duplicates dictionary.

        Args:
            hash_val (str): Hash value of the message received.

        Returns:
            boolean
        """

        if str(hash_val) in self.duplicates:
            return True
        else:
            self.duplicates[str(hash_val)] = 'true'
            return False

    def calculate_md5(self, msg: str) -> str:
        """
        Calculates hash value with the timestamp and data of the message as input. Only used to determine if message has
        already been received.

        Args:
            msg (str): Message with full transport layer header.

        Returns:
            str: Hash value created wit timestamp and data of message
        """

        unpacked = self.unpack(msg)
        if unpacked[2] == "2":
            string_to_hash = str(unpacked[5][2] + unpacked[5][3] + unpacked[2])
        else:
            string_to_hash = str(unpacked[3] + unpacked[5])
        hashed = hashlib.md5(string_to_hash.encode())
        return hashed.hexdigest()

    def create_log_request(self, destination: str) -> str:
        now = str(datetime.now().time())
        with open(LOG) as json_log:
            log_file = json.load(json_log)
            last_sequence = log_file[str(destination)][-1]["sequence"]
            request_msg = self.identity + ";" + "-1" + ";" + "1" + ";" + now + ";" + str(destination) + ";" \
                          + str(last_sequence)
            return request_msg

    @staticmethod
    def check_if_request(unpacked_msg: tuple) -> bool:
        """
        Checks if the flag corresponds to a request flag.

        Args:
            unpacked_msg (tuple): Tuple containing all components of a transport layer packet.

        Returns:
            boolean

        """

        return unpacked_msg[2] == "1"

    def create_request_response(self, request_msg: tuple) -> None:
        """
        Creates a response message to the requested entry of the log. Calculates the negative of the difference of the
        requested sequence and the current sequence and uses this difference to address the right position in the log.
        From there the needed data is collected and packed into a response message.

        Args:
            request_msg (tuple): Tuple containing all components of a request message.

        Returns:
            None
        """

        now = str(datetime.now())
        with open(LOG) as json_log:
            log_file = json.load(json_log)
            last_sequence = int(log_file[str(self.identity)][-1]["sequence"])
            last_sequence_request = int(request_msg[5])
            difference = (-1) * abs(last_sequence - last_sequence_request)
            if difference == 0:
                return
            else:
                #for i in range(difference, 0):
                entry_data = str(log_file[str(self.identity)][difference]["sequence"]) + ";" + \
                            str(log_file[str(self.identity)][difference]["receiver"]) + ";" + \
                            str(log_file[str(self.identity)][difference]["timestamp"]) + ";" + \
                            str(log_file[str(self.identity)][difference]["data"])
                response = str(self.identity) + ";" + "-1" + ";" + "2" + ";" + str(now) + ";" + str(request_msg[0]) + \
                               ";" + str(entry_data)
                self.tx_queue.put(response)

    @staticmethod
    def unpack_request_response(entry: tuple) -> tuple:
        """
        Gathers the response data from the whole packet.

        Args:
            entry (tuple): Tuple containing all components of a response message.

        Returns:
            tuple: Tuple containing the relevant information needed for the log.
        """

        info = entry[5]
        return info

    def start(self):
        while True:
            if not self.msg_tx_queue.empty():
                self.append_to_linklayer()

            if not self.rx_queue.empty():
                self.append_to_application_layer()
