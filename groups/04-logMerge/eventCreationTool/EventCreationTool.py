# This is a wrapper for simple BACnet event handling provided by group 4 logMerge
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

# For documentation how to use this tool, please refer to README.md

import Event  # Our representation of an feed event, please refer to Event.py
import hashlib
import hmac
import secrets
import nacl.signing  # install with 'pip install pynacl'
import nacl.encoding
import os

# !!! For the code to work your also need to install cbor2 (This is used inside Event.py) !!!
# Install with: 'pip install cbor2'


class HashingAlgorithmNotFoundException(Exception):
    def __init__(self):
        super().__init__("The hashing algorithm you specified is unknown to this version of the EventCreationTool")


class SigningAlgorithmNotFoundException(Exception):
    def __init__(self):
        super().__init__("The signing algorithm you specified is unknown to this version of the EventCreationTool")


class KeyFileNotFoundException(Exception):
    def __init__(self):
        super().__init__("Sorry, it seems that you are not the owner of the specified feed. "
                         + "The private key was not found at the specified path.")


class IllegalArgumentTypeException(Exception):
    def __init__(self, list_of_supported_types):
        if not list_of_supported_types or not isinstance(list_of_supported_types, set):
            super().__init__("You called the method with an argument of wrong type!")
        else:
            super().__init__("You called the method with an argument of wrong type! Supported types are:"
                             + ' '.join(list_of_supported_types))


class EventCreationTool:

    # These are the currently supported signing/hashing algorithms. Contact us if you need another one!
    _SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
    _HASH_INFO = {'sha256': 0}

    def __init__(self):
        self._hashing_algorithm = 0
        self._signing_algorithm = 0
        self._path_to_keys = os.getcwd()

    def set_path_to_keys(self, directory_path, relative=True):
        if relative:
            self._path_to_keys = os.path.join(os.getcwd(), directory_path)
        else:
            self._path_to_keys = directory_path

    def get_own_feed_ids(self):
        (_, _, filenames) = next(os.walk(self._path_to_keys))
        return [filename[:len(filename) - 4] for filename in filenames if filename.endswith('.key')]

    def set_hashing_algorithm(self, hashing_algorithm):
        if hashing_algorithm in self._HASH_INFO:
            self._hashing_algorithm = self._HASH_INFO[hashing_algorithm]
        else:
            raise HashingAlgorithmNotFoundException

    def set_signing_algorithm(self, signing_algorithm):
        if signing_algorithm in self._SIGN_INFO:
            self._signing_algorithm = self._SIGN_INFO[signing_algorithm]
        else:
            raise SigningAlgorithmNotFoundException

    def get_supported_hashing_algorithms(self):
        return self._HASH_INFO.keys()

    def get_supported_signing_algorithms(self):
        return self._SIGN_INFO.keys()

    def create_feed_and_generate_first_event(self, content_identifier, content_parameter):
        public_key = self.create_feed()
        return self.generate_first_event(public_key, content_identifier, content_parameter)

    def create_feed(self):
        private_key = secrets.token_bytes(32)
        if self._signing_algorithm == 0:
            signing_key = nacl.signing.SigningKey(private_key)
            public_key = signing_key.verify_key.encode()
        elif self._signing_algorithm == 1:
            public_key = secrets.token_bytes(32)
        else:
            raise SigningAlgorithmNotFoundException
        with open(os.path.join(self._path_to_keys, public_key.hex() + '.key'), 'wb') as file:
            file.write(private_key)
        return public_key

    def generate_first_event(self, feed_id, content_identifier, content_parameter):
        if isinstance(feed_id, str):
            feed_id = bytes.fromhex(feed_id)
        elif not isinstance(feed_id, bytes):
            raise IllegalArgumentTypeException
        content = Event.Content(content_identifier, content_parameter)
        meta = Event.Meta(feed_id, 0, None, self._signing_algorithm, self._generate_hash(content.get_as_cbor()))
        signature = self._generate_signature(self._load_private_key(feed_id), meta.get_as_cbor())
        return Event.Event(meta, signature, content).get_as_cbor()

    def generate_event(self, feed_id, last_sequence_number, hash_of_previous_meta,
                       content_identifier, content_parameter):
        if isinstance(feed_id, str):
            feed_id = bytes.fromhex(feed_id)
        elif not isinstance(feed_id, bytes):
            raise IllegalArgumentTypeException
        private_key = self._load_private_key(feed_id)
        content = Event.Content(content_identifier, content_parameter)
        meta = Event.Meta(feed_id, last_sequence_number + 1,
                          hash_of_previous_meta, self._signing_algorithm, self._generate_hash(content.get_as_cbor()))
        signature = self._generate_signature(private_key, meta.get_as_cbor())
        return Event.Event(meta, signature, content).get_as_cbor()

    def generate_event_from_previous(self, previous_event, content_identifier, content_parameter):
        previous_event = Event.Event.from_cbor(previous_event)
        feed_id = previous_event.meta.feed_id
        last_sequence_number = previous_event.meta.seq_no + 1
        hash_of_previous_meta = self._generate_hash(previous_event.meta.get_as_cbor())
        return self.generate_event(feed_id, last_sequence_number, hash_of_previous_meta,
                                   content_identifier, content_parameter)

    def get_private_key_from_feed_id(self, feed_id):
        if isinstance(feed_id, bytes):
            feed_id = feed_id
        elif isinstance(feed_id, str):
            feed_id = bytes.fromhex(feed_id)
        else:
            raise IllegalArgumentTypeException(['bytes', 'str'])
        return self._load_private_key(feed_id)

    def get_private_key_from_event(self, event):
        if not isinstance(event, bytes):
            raise IllegalArgumentTypeException(['bytes'])
        feed_id = Event.Event.from_cbor(event).meta.feed_id
        return self._load_private_key(feed_id)

    def _load_private_key(self, feed_id):
        try:
            file = open(os.path.join(self._path_to_keys, feed_id.hex() + '.key'), 'rb')
        except FileNotFoundError:
            raise KeyFileNotFoundException
        else:
            private_key = file.read(32)
            file.close()
            return private_key

    def _generate_hash(self, cbor_bytes):
        if self._hashing_algorithm == 0:
            return [self._hashing_algorithm, hashlib.sha256(cbor_bytes).digest()]
        else:
            raise HashingAlgorithmNotFoundException

    def _generate_signature(self, private_key, cbor_bytes):
        if self._signing_algorithm == 0:
            signing_key = nacl.signing.SigningKey(private_key)
            return signing_key.sign(cbor_bytes).signature
        elif self._signing_algorithm == 1:
            return hmac.new(private_key, cbor_bytes, hashlib.sha256).digest()
        else:
            raise SigningAlgorithmNotFoundException
