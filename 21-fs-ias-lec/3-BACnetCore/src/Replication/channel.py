from abc import ABC, abstractmethod


class Channel(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def set_input_queue(self):
        pass

    @abstractmethod
    def set_output_queue(self):
        pass
