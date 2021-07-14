import cbor2
from ..Core.com_link import ComLinkProtocol


class MessageContainer:

    def __init__(self, protocol_instruction: ComLinkProtocol, data):
        self.protocol_instruction = protocol_instruction
        self.data = data

    @classmethod
    def from_cbor(cls, message_container: bytes):
        protocol_instruction, data = cbor2.loads(message_container)
        return MessageContainer(protocol_instruction, data)

    def get_as_cbor(self):
        return cbor2.dumps([self.protocol_instruction, self.data])
