import cbor2


class MessageContainer:
    """
    The message container deals with the serialization and deserialization of data within the
    CBOR format.
    """

    def __init__(self, protocol_instruction, data):
        self.protocol_instruction = protocol_instruction
        self.data = data

    @classmethod
    def from_cbor(cls, message_container: bytes):
        protocol_instruction, data = cbor2.loads(message_container)
        return MessageContainer(protocol_instruction, data)

    def get_as_cbor(self):
        return cbor2.dumps([self.protocol_instruction, self.data])
