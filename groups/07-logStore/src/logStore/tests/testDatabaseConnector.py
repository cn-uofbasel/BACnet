from downConnection.DatabaseConnector import DatabaseConnector
from functions.Event import Event, Meta, Content
import hashlib  # Comes with python
import secrets  # Comes with python
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from testfixtures import LogCapture
import os


def test_insert_cbor_event():
    try:
        with LogCapture() as l:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode(encoder=HexEncoder)

            content = Content('whateverapp/whateveraction', {'somekey': 'somevalue', 'someotherkey': 753465734265})
            hash_of_content = hashlib.sha256(content.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content).get_as_cbor()

            connector = DatabaseConnector()
            connector.add_event(event)
            result = connector.get_current_event(public_key_feed_id)
            result = Event.from_cbor(result)
        assert result.meta.hash_of_content[1] == meta.hash_of_content[1]
        print(l)
    finally:
        if os.path.exists('byteArrayDatabase.db'):
            pass
            #os.remove('byteArrayDatabase.db')
