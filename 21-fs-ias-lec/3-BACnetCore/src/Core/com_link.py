from enum import Enum
from queue import Queue

from storage_controller import StorageController
from ..Replication.channel import Channel
from ..Replication.message_container import MessageContainer


class OperationModes(Enum):
    AUTOSYNC = 1
    MANUAL = 2

class ComLinkProtocol(Enum):
    REQ_META = 1
    REQ_DATA = 2
    DATA = 3
    META = 4

class ComLink:

    def __init__(self, channel, operation_mode: OperationModes, storage_controller: StorageController):
        self.channel = channel
        self.operation_mode = operation_mode
        self.storage_controller = storage_controller
        # create queues to communicate with channel and configure channel accordingly
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.channel.set_output_queue(self.output_queue)
        self.channel.set_input_queue(self.input_queue)

        if operation_mode == OperationModes.AUTOSYNC:
            self.__autosync(1000)

    def sync(self):
        """
        This method reads all messages from the input_queue and processes them using __parse_next_input
        :return:
        """
        while self.input_queue.qsize() != 0:
            self.__parse_next_input(self.input_queue.get_nowait())

    def request_sync(self):
        self.channel.request_meta()

    def __parse_next_input(self, message_container):
        if message_container == ComLinkProtocol.REQ_META:
            self.channel.send_meta(self.storage_controller.get_database_status())
        elif message_container == ComLinkProtocol.REQ_DATA:
            self.channel.send_data(MessageContainer(ComLinkProtocol.DATA, ))
        elif message_container == ComLinkProtocol.DATA:
            self.storage_controller.import_event()
        elif message_container == ComLinkProtocol.META:
            self.storage_controller.ge
        else:
            raise UnknownMessageException(message_container.protocol_instrution)

    def set_channel(self, channel: Channel):
        self.channel = channel

    def __compare_database_status(self, status_dict):
        """
        This method takes a dictionary of (feed_id, current seq number) pairs and compares this status to the status
        of the own node.
        Used when receive Meta, to send right Fata requests.
        :param status_dict:
        :return: dict that contains feed_id, seq_num pairs with feed_ids from
        """
        pass

    def __autosync(self, interval):
        pass


class UnknownMessageException(Exception):
    def __init__(self, message):
        super().__init__(f"The given Message Protocol Instruction {message} is unknown!")