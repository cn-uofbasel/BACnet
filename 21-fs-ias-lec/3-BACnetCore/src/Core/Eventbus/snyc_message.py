from eventbus_message import EventbusMessage
from protocols import SyncProtocol

"""
Interface messages
"""


class SyncMessage(EventbusMessage):

    def __init__(self, protocol: SyncProtocol, message):
        super().__init__(protocol, message)

    def get_protocol(self):
        return super().protocol

    def get_message(self):
        return super().message

