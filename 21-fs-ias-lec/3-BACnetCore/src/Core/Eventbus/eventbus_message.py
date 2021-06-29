from abc import ABC

"""
Abstract class for the two types of messages on the eventbus (sync and interface messages).
"""


class EventbusMessage(ABC):

    def __init__(self, protocol, message):
        self.protocol = protocol
        self.message = message
