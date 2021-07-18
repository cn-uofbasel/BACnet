from enum import Enum
from queue import Queue
from .security.verification import Verification
from ..replication.channel import Channel
from ..replication.message_container import MessageContainer
from .interface.event import Event


class OperationModes(Enum):
    AUTOSYNC = 1
    MANUAL = 2


class ComLinkProtocol(Enum):
    """
    The protocol that the Com-Link uses to process and label the messages. Messages are encapsulated
    in MessageContainers
    """
    REQ_META = 1
    REQ_DATA = 2
    DATA = 3
    META = 4


class ComLink:
    """
    This class manages the communication between nodes. It is created by the Node class and is connected to channels
    via 2 queues for input and output. The Channels can have arbitrary form, as long as they give MessageContainers into
    the Input-queue and can handle MessageContainers in the Output-queue. (Both following the protocol)

    It uses the StorageController to check the Database-status and to get Events.

    It is Used by the StorageController
    to sync -> request new meta data from peers and process all elements in the Input queue.
    """

    def __init__(self, channel, operation_mode: OperationModes, node):
        self.operation_mode = operation_mode
        self.storage_controller = node.get_storage()
        self.verification = Verification(self.storage_controller.get_database_handler())
        # create queues to communicate with channel and configure channel accordingly
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.channel = None
        self.set_channel(channel)

        self.set_operation_mode(operation_mode)

    def set_operation_mode(self, op_mode: OperationModes):
        """
        This Method is used to set the operationMode according to the parameter. When mode is manual, nothing needs
        to be done. When mode is AUTOSYNC, a Thread is started, that will call sync() in a fixed time Interval

        Parameters
        ----------
        operation_mode  the mode you want to set the comLink to operate in!
        """
        if op_mode == OperationModes.MANUAL:
            self.operation_mode = OperationModes.MANUAL
        elif op_mode == OperationModes.AUTOSYNC:
            raise UnknownOperationModeException(OperationModes.AUTOSYNC.name)
        else:
            raise UnknownOperationModeException(op_mode)

    def parse_all_inputs(self):
        """
        This method reads all messages from the input_queue and processes them using __parse_next_input
        """
        print("In Parse all inputs...")
        while self.input_queue.qsize() != 0:
            self.__handle_message(self.input_queue.get_nowait())
        print("Finished parsing inputs...")

    def request_sync(self):
        """
        This method puts a message in the output queue, that contains a request for the metadata of the peer Node.
        """
        self.output_queue.put(MessageContainer(ComLinkProtocol.REQ_META, None))

    def __handle_message(self, message_container: MessageContainer):
        """
        This method takes a messageContainer, extracts its content and performs different operations depending on
        the Protocol-Instruction it finds in the MessageContainer.
        Parameters
        ----------
        message_container Container that should be operated on
        """
        # When incoming message is requesting metadata, then get the metadata of feeds that should be exported and send
        # this list(put an according MessageContainer in the output_queue)
        if message_container.protocol_instruction == ComLinkProtocol.REQ_META:
            to_promote = message_container.data
            self.output_queue.put(MessageContainer(ComLinkProtocol.META, to_promote))

        # Incoming message is requesting data(events) from this node. Loop through the requested data and put created
        # Data-MessageContainers in the output_queue
        elif message_container.protocol_instruction == ComLinkProtocol.REQ_DATA:
            requested = message_container.data  # is a dict containing feed_id and
            for feed_id, last_seq_num in requested.items():
                if self.verification.should_export_feed(feed_id):
                    events = self.storage_controller.get_events_since(feed_id, last_seq_num)
                    for event in events:
                        self.output_queue.put(MessageContainer(ComLinkProtocol.DATA, event.get_as_cbor()))

        # Incoming message contains data(events) that may be imported. Unpack event from MessageContainer and parse it
        # from cbor. Then try to import using the appropriate method from storage_controller
        elif message_container.protocol_instruction == ComLinkProtocol.DATA:
            self.storage_controller.import_event(Event.from_cbor(message_container.data))

        # Incoming message contains metadata from peer Node(we might have requested it). Check if our database is
        # missing events the other node has and request them.
        elif message_container.protocol_instruction == ComLinkProtocol.META:
            to_request = self.__compare_database_status(message_container.data)
            self.output_queue.put(MessageContainer(ComLinkProtocol.REQ_DATA, to_request))
        else:
            raise UnknownMessageException(message_container.protocol_instruction)

    def set_channel(self, channel: Channel):
        self.channel = channel
        self.channel.set_output_queue(self.output_queue)
        self.channel.set_input_queue(self.input_queue)

    def __compare_database_status(self, peer_status: dict) -> dict:
        """
        This method takes a dictionary of (feed_id, current seq number) pairs and compares this status to the status
        of the own node.
        Here we return everything we don't have no matter if some feeds are blocked or not or trusted
        :param peer_status: dict that contains the information about the peers status of feeds
        :return: dict that contains feed_id, seq_num pairs with feed_ids from all feeds we need to request
        """
        my_status = self.storage_controller.get_database_status()  # contains all known feeds
        to_request = dict()  # dict that will hold feed_id and current_seq_no of own node we need to request
        for feed_id, curr_seq_no in peer_status.items():
            if feed_id not in my_status.keys():
                to_request[feed_id] = -1
            elif my_status[feed_id] < curr_seq_no:
                to_request[feed_id] = my_status[feed_id]
        return to_request


class UnknownMessageException(Exception):
    def __init__(self, message):
        super().__init__(f"The given Message Protocol Instruction {message} is unknown\n Please check the enumeration"
                         f"{ComLinkProtocol.__class__.__name__} for available Instructions!")


class UnknownOperationModeException(Exception):
    def __init__(self, mode):
        super().__init__(f"{mode} is no mode the Com-Link can operate in! It is not implemented or unknown\n"
                         f"Please check the enumeration {OperationModes.__class__.__name__} for available Modes!")
