from abc import ABC, abstractmethod
from queue import Queue


class Channel(ABC):
    """
    The Channel class is abstract and specifies what must be implemented in an actual channel variant.
    Different channel implementations can be developed, according to the needs and circumstances of
    the project, that has to be connected to the BACnet core.
    We refer to the udp_channel for a specification using the UDP protocol, other variants have to be
    developed separately.
    """

    def __init__(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def set_input_queue(self, queue: Queue):
        pass

    @abstractmethod
    def set_output_queue(self, queue: Queue):
        pass
