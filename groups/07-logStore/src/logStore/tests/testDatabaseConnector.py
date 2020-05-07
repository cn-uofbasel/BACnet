from downConnection.DatabaseConnector import DatabaseConnector
from functions.Event import Event, Meta, Content
import hashlib  # Comes with python
import secrets  # Comes with python
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from testfixtures import LogCapture
import os


def test_add_event_get_current_event():
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
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_current_seq_no():
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
            meta = Meta(public_key_feed_id, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content).get_as_cbor()
            connector.add_event(event)
            meta = Meta(public_key_feed_id, 2, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content).get_as_cbor()
            connector.add_event(event)
            res = connector.get_current_seq_no(public_key_feed_id)
        assert res == 2
        print(l)
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_event():
    try:
        with LogCapture() as l:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode(encoder=HexEncoder)

            content0 = Content('whateverapp/whateveraction', {'firstkey': 'somevalue', 'someotherkey': 753465734265})
            hash_of_content = hashlib.sha256(content0.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content0).get_as_cbor()

            connector = DatabaseConnector()
            connector.add_event(event)
            meta = Meta(public_key_feed_id, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content1 = Content('whateverapp/whateveraction', {'secondkey': 'somevalue', 'someotherkey': 753465734265})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content1).get_as_cbor()
            connector.add_event(event)
            content2 = Content('whateverapp/whateveraction', {'thirdkey': 'somevalue', 'someotherkey': 753465734265})
            meta = Meta(public_key_feed_id, 2, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content2).get_as_cbor()
            connector.add_event(event)
            res0 = connector.get_event(public_key_feed_id, 0)
            res1 = connector.get_event(public_key_feed_id, 1)
            res2 = connector.get_event(public_key_feed_id, 2)
            result0 = Event.from_cbor(res0)
            result1 = Event.from_cbor(res1)
            result2 = Event.from_cbor(res2)
        assert result0.content.content == content0.content
        assert result1.content.content == content1.content
        assert result2.content.content == content2.content
        print(l)
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')
