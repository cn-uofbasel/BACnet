from eventbus_message import EventbusMessage
from protocols import InterfaceProtocol

"""
Interface messages
"""


class InterfaceMessage(EventbusMessage):

    def __init__(self, protocol: InterfaceProtocol, message, sender_id):
        super().__init__(protocol, message)
        self.sender_id = sender_id

    def get_protocol(self):
        return super().protocol

    def get_message(self):
        return super().message

    def get_sender_id(self):
        return self.sender_id
