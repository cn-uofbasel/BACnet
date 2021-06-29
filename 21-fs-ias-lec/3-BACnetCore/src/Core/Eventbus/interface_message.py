from eventbus_message import EventbusMessage
from protocols import InterfaceProtocol

"""
Interface messages
"""


class InterfaceMessage(EventbusMessage):

    def __init__(self, protocol: InterfaceProtocol, message):
        super().__init__(protocol, message)

    def get_protocol(self):
        return super().protocol

    def get_message(self):
        return super().message
