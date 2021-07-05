from abc import ABC, abstractmethod


class Channel(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def request_meta(self):
        pass

    @abstractmethod
    def send_meta(self):
        pass

    @abstractmethod
    def request_data(self):
        pass

    @abstractmethod
    def send_data(self):
        pass
