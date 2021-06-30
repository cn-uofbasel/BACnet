import hashlib
import hashlib
import hmac
import secrets
import nacl.signing  # install with 'pip install pynacl'
import nacl.encoding


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

    def create_next_event(self, last_event, sig_type=0, hash_type=0):
        pub_key = last_event.meta.feed_id
        seq_num = last_event.meta.seq_no

    def generate_feed_and_create_first_event(self, content_identifier: str, content_parameter: dict):
        public_key = self.create_new_feed()
        return self.create_first_event(public_key, content_identifier, content_parameter)

    def create_new_feed(self, sig_type=0):
        private_key = secrets.token_bytes(32)
        if sig_type == 0:
            signing_key = nacl.signing.SigningKey(private_key)
            public_key = signing_key.verify_key.encode()
        elif sig_type == 1:
            public_key = secrets.token_bytes(32)
        else:
            raise SigningAlgorithmNotFoundException
        # TODO: Create Feed in Dbase
        return public_key

    def create_first_event(self, feed_id: bytes, content_identifier: str, content_parameter: dict, sig_type=0):
        content = Content(content_identifier, content_parameter)
        meta = Meta(feed_id, 0, None, sig_type, self._calculate_hash(content.get_as_cbor()))
        signature = self._calculate_signature(self.load_private_key(feed_id), meta.get_as_cbor())
        return Event(meta, signature, content).get_as_cbor()

    def create_event(self, feed_id: bytes, last_sequence_number: int, hash_of_previous_meta,
                     content_identifier: str, content_parameter: dict, sig_type=0):
        private_key = self.load_private_key(feed_id)
        content = Content(content_identifier, content_parameter)
        meta = Meta(feed_id, last_sequence_number + 1,
                    hash_of_previous_meta, sig_type, self._calculate_hash(content.get_as_cbor()))
        signature = self._calculate_signature(private_key, meta.get_as_cbor())
        return Event(meta, signature, content).get_as_cbor()

    def create_event_from_previous(self, previous_event, content_identifier, content_parameter):
        previous_event = Event.from_cbor(previous_event)
        feed_id = previous_event.meta.feed_id
        last_sequence_number = previous_event.meta.seq_no + 1
        hash_of_previous_meta = self._calculate_hash(previous_event.meta.get_as_cbor())
        return self.create_event(feed_id, last_sequence_number, hash_of_previous_meta,
                                 content_identifier, content_parameter)


    def load_private_key(self, feed_id):
        if isinstance(feed_id, bytes):
            feed_id = feed_id
        elif isinstance(feed_id, str):
            feed_id = bytes.fromhex(feed_id)
        else:
            raise IllegalArgumentTypeException(['bytes', 'str'])
        # TODO: Query Dbase connector for private key

    @staticmethod
    def _calculate_hash(cbor_bytes, hash_type=0):
        if hash_type == 0:
            return [0, hashlib.sha256(cbor_bytes).digest()]
        else:
            raise HashingAlgorithmNotFoundException

    @staticmethod
    def _calculate_signature(private_key, cbor_bytes, sig_type=0):
        if sig_type == 0:
            signing_key = nacl.signing.SigningKey(private_key)
            return signing_key.sign(cbor_bytes).signature
        elif sig_type == 1:
            return hmac.new(private_key, cbor_bytes, hashlib.sha256).digest()
        else:
            raise SigningAlgorithmNotFoundException