import hashlib
import secrets

import nacl.encoding
import nacl.exceptions
import nacl.signing

"""
Crypto to Secure the BACNet:
-----------------------------

In general the hash of the previous event is just the hash of its metadata. This allows for the Events to be imported 
in a database without its content (ex when the content is too large or on low bandwidth networks).

Since the Hash of the Content is saved in metadata, the content integrity can always be checked.
The metadata is signed and thus protected from changes.
"""

from ..interface.event import Event, Meta

HASH_TYPES = {0: 'sha256'}
SIGNATURE_TYPES = {0: 'ed25519'}


def check_signature(event: Event):
    """
    This method checks the signature of an event. Typically, the signature is the hash of the metadata encrypted
    with a private key to the corresponding public-key/feed_id.

    raises InvalidSignType() Exception if given signature type/method is not supported

    Parameters
    ----------
    event   The event the signature needs to be checked for

    Returns
    -------
    true/false if the signature is valid or not
    """
    sign_type = event.meta.signature_info
    if sign_type == 0:
        verification_key = nacl.signing.VerifyKey(event.meta.feed_id)
        try:
            verification_key.verify(event.meta.get_as_cbor(), event.signature)
            # if no error is raised, verification has been successful
            return True
        except nacl.exceptions.BadSignatureError:
            return False
    else:
        raise InvalidSignType(sign_type)


def check_in_order(to_insert: Event, last_event: Event = None):
    """
    This function checks whether events are inorder and from the same feed. Therefore also checks the hash dependency
    Parameters
    ----------
    to_insert   The event to be inserted into the feed
    last_event  The last event from to feed to insert in (may be non existent when to_insert is genesis event)

    Returns
    -------
    boolean whether to_insert is in_order and from same feed as last event (if existent)
    """
    if last_event is not None:
        # from same feed and in-order sequence numbers?
        if (to_insert.meta.seq_no == last_event.meta.seq_no + 1) and last_event.meta.feed_id == to_insert.meta.feed_id:
            print("feed-no and seq_no correct!")
            # hash of previous is right?
            return _check_previous_hash(to_insert, last_event)
        else:
            return False
    else:
        return to_insert.meta.seq_no == 0


def check_content_integrity(event: Event) -> bool:
    """
    Check the integrity of the content by comparing its hash against the hash_of_content in the Metadata.
    TODO: What if You want to send just meta without content? -> separate functionality?
    Parameters
    ----------
    event   Event to check content integrity for

    Returns
    -------
    bool or raise exception when Hash-type is unknown
    """
    print(event.meta.hash_of_content)
    return event.meta.hash_of_content == hashlib.sha256(event.content.get_as_cbor()).digest()


def calculate_signature(meta: Meta, sign_key: str):
    """
    Used to sign the metadata of an event with a given sign_key. Used when an event is created.

    Parameters
    ----------
    meta        Metadata to sign
    sign_key    key to sign with, often the private key

    Returns
    -------
    signature
    """
    sign_type = meta.signature_info
    if sign_type == 0:
        signing_key = nacl.signing.SigningKey(sign_key)
        return signing_key.sign(meta.get_as_cbor()).signature
    else:
        raise InvalidSignType(sign_type)


def create_keys(signature_type=0):
    """
    Used when new feeds are created, takes the wished signature type and calculates a key(pair), and returns it.

    Parameters
    ----------
    signature_type  type of signature to use for the key (pair)

    Returns
    -------
    The key (pair)
    """
    # Use 0 -> Nacl ed2551^9
    if signature_type == 0:
        private_key = secrets.token_bytes(32)
        signing_key = nacl.signing.SigningKey(private_key)
        public_key = signing_key.verify_key.encode()
        return public_key, private_key
    else:
        raise InvalidSignType(signature_type)


def calculate_hash(to_hash: bytes, hash_type=0):
    """
    This method calculates hashed for given bytes.

    Parameters
    ----------
    to_hash   bytes to be hashed
    hash_type Type of hash that is used

    Returns
    -------
    The hash
    """
    if hash_type == 0:
        return hashlib.sha256(to_hash).digest()
    else:
        raise InvalidHashType(hash_type)


def _check_previous_hash(to_insert: Event, last_event: Event) -> bool:
    prev_hash = to_insert.meta.hash_of_prev
    return prev_hash == hashlib.sha256(last_event.meta.get_as_cbor()).digest()


class InvalidHashType(Exception):
    def __init__(self, message):
        super().__init__(f"The given hash-type: {message} is not known nor implemented\n "
                         f"Supported: {HASH_TYPES.values()}")


class InvalidSignType(Exception):
    def __init__(self, message):
        super().__init__(f"The given signature-type: {message} is not known nor implemented\n "
                         f"Supported: {SIGNATURE_TYPES.values()}")
