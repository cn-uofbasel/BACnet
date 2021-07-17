from ..security.crypto import calculate_hash, calculate_signature
from ..interface.event import Event, Meta, Content


class HashingAlgorithmNotFoundException(Exception):
    def __init__(self):
        super().__init__("The hashing algorithm you specified is unknown to this version of the EventCreationTool")


class SigningAlgorithmNotFoundException(Exception):
    def __init__(self):
        super().__init__("The signing algorithm you specified is unknown to this version of the EventCreationTool")


class IllegalArgumentTypeException(Exception):
    def __init__(self, list_of_supported_types):
        if not list_of_supported_types or not isinstance(list_of_supported_types, set):
            super().__init__("You called the method with an argument of wrong type!")
        else:
            super().__init__("You called the method with an argument of wrong type! Supported types are:"
                             + ' '.join(list_of_supported_types))


class EventFactory:
    # These are the currently supported signing/hashing algorithms. Contact us if you need another one!
    _SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
    _HASH_INFO = {'sha256': 0}

    def __init__(self, dbase_conn):
        self.dbase_conn = dbase_conn

    def create_first_event(self, feed_id: bytes, content_identifier: str, content_parameter: dict, sig_type=0):
        content = Content(content_identifier, content_parameter)
        meta = Meta(feed_id, 0, None, sig_type, calculate_hash(content.get_as_cbor()))
        signature = calculate_signature(self.dbase_conn.load_private_key(feed_id), meta.get_as_cbor())
        return Event(meta, signature, content).get_as_cbor()

    def create_event(self, feed_id: bytes, last_sequence_number: int, hash_of_previous_meta,
                     content_identifier: str, content_parameter: dict, sig_type=0):
        private_key = self.dbase_conn.load_private_key(feed_id)
        content = Content(content_identifier, content_parameter)
        meta = Meta(feed_id, last_sequence_number + 1,
                    hash_of_previous_meta, sig_type, calculate_hash(content.get_as_cbor()))
        signature = calculate_signature(private_key, meta.get_as_cbor())
        return Event(meta, signature, content).get_as_cbor()

    def create_event_from_previous(self, previous_event, content_identifier, content_parameter):
        previous_event = Event.from_cbor(previous_event)
        feed_id = previous_event.meta.feed_id
        last_sequence_number = previous_event.meta.seq_no + 1
        hash_of_previous_meta = calculate_hash(previous_event.meta.get_as_cbor())
        return self.create_event(feed_id, last_sequence_number, hash_of_previous_meta,
                                 content_identifier, content_parameter)

