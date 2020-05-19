import hashlib  # Comes with python
import secrets  # Comes with python
from nacl.signing import SigningKey
from testfixtures import LogCapture
import os
from ..logStore.funcs.event import Content, Event, Meta
from ..logStore.transconn.database_connector import DatabaseConnector
from ..logStore.database.event_handler import EventHandler
from ..logStore.funcs.EventCreationTool import EventFactory
from ..logStore.appconn.chat_connection import ChatFunction
from ..logStore.appconn.kotlin_connection import KotlinFunction

def test_event_factory():
    ecf = EventFactory()
    new_event = ecf.next_event('whateverapp/whateveraction', {'oneKey': 'somevalue', 'someotherkey': 1})
    connector = DatabaseConnector()
    connector.add_event(new_event)
    result = connector.get_current_event(ecf.get_feed_id())
    result = Event.from_cbor(result)
    assert result.content.content[0] == 'whateverapp/whateveraction'


def test_get_current_event():
    try:
        with LogCapture():
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            content = Content('whateverapp/whateveraction', {'oneKey': 'somevalue', 'someotherkey': 1})
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
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
                if os.path.exists('eventDatabase.sqlite'):
                    os.remove('eventDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_current_seq_no():
    try:
        with LogCapture() as log_cap:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            content = Content('whateverapp/whateveraction', {'somekey': 'somevalue', 'someotherkey': 2})
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
        print(log_cap)
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
                if os.path.exists('eventDatabase.sqlite'):
                    os.remove('eventDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_event():
    try:
        with LogCapture() as log_cap:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            content0 = Content('whateverapp/whateveraction', {'firstkey': 'somevalue', 'someotherkey': 3})
            hash_of_content = hashlib.sha256(content0.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content0).get_as_cbor()

            connector = DatabaseConnector()
            connector.add_event(event)
            meta = Meta(public_key_feed_id, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content1 = Content('whateverapp/whateveraction', {'secondkey': 'somevalue', 'someotherkey': 4})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content1).get_as_cbor()
            connector.add_event(event)
            content2 = Content('whateverapp/whateveraction', {'thirdkey': 'somevalue', 'someotherkey': 5})
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
        print(log_cap)
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
                if os.path.exists('eventDatabase.sqlite'):
                    os.remove('eventDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_chat_event():
    try:
        with LogCapture() as log_cap:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            content0 = Content('chat/whateveraction',
                               {'messagekey': 'hallo zusammen', 'chat_id': '1', 'timestampkey': 10})
            hash_of_content = hashlib.sha256(content0.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content0).get_as_cbor()

            connector = ChatFunction()
            connector.insert_chat_msg(event)
            meta = Meta(public_key_feed_id, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content1 = Content('chat/whateveraction',
                               {'messagekey': 'wie gehts?', 'chat_id': '1', 'timestampkey': 20})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content1).get_as_cbor()
            connector.insert_chat_msg(event)
            content2 = Content('chat/whateveraction',
                               {'messagekey': 'schönes Wetter heute', 'chat_id': '1', 'timestampkey': 30})
            meta = Meta(public_key_feed_id, 2, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content2).get_as_cbor()
            connector.insert_chat_msg(event)
            print(log_cap)
            print('\n#######################################')
            # TODO: there seem to be some errors concerning the chat_id, I would watch out in what form it is (binary or string?)
            q = EventHandler().get_event_since('chat', 15, '1')
            print(q)
            print('\n#######################################')
            t = EventHandler().get_all_events(application='chat', chat_id='1')
            print(t)
        assert True
    finally:
        try:
            if os.path.exists('eventDatabase.sqlite'):
                os.remove('eventDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_kotlin_event():
    try:
        with LogCapture() as log_cap:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            private_key2 = secrets.token_bytes(32)
            signing_key2 = SigningKey(private_key2)
            public_key_feed_id2 = signing_key2.verify_key.encode()

            private_key3 = secrets.token_bytes(32)
            signing_key3 = SigningKey(private_key3)
            public_key_feed_id3 = signing_key3.verify_key.encode()

            content00 = Content('KotlinUI/username',
                                {'newUsername': 'Bob', 'oldUsername': '',
                                 'timestamp': 1})
            hash_of_content = hashlib.sha256(content00.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content00).get_as_cbor()

            connector = KotlinFunction()
            connector.insert_data(event)

            meta = Meta(public_key_feed_id2, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content01 = Content('KotlinUI/username',
                                {'newUsername': 'Alice', 'oldUsername': '', 'timestamp': 2})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content01).get_as_cbor()
            connector.insert_data(event)

            meta = Meta(public_key_feed_id3, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content02 = Content('KotlinUI/username',
                                {'newUsername': 'Max', 'oldUsername': '', 'timestamp': 3})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content02).get_as_cbor()
            connector.insert_data(event)

            meta = Meta(public_key_feed_id, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content = Content('KotlinUI/post',
                              {'text': 'Hi Alice, nice to hear from you', 'username': 'Bob',
                               'timestamp': 11})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content).get_as_cbor()
            connector.insert_data(event)

            meta = Meta(public_key_feed_id2, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content1 = Content('KotlinUI/post',
                               {'text': 'Hi Bob', 'username': 'Alice', 'timestamp': 15})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content1).get_as_cbor()
            connector.insert_data(event)

            content2 = Content('KotlinUI/post',
                               {'text': 'Hello everyone', 'username': 'Max',
                                'timestamp': 17})
            meta = Meta(public_key_feed_id3, 1, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content2).get_as_cbor()
            connector.insert_data(event)

            meta = Meta(public_key_feed_id2, 2, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            content01 = Content('KotlinUI/username',
                                {'newUsername': 'Alice2', 'oldUsername': 'Alice', 'timestamp': 20})
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content01).get_as_cbor()
            connector.insert_data(event)


            s = connector.get_all_kotlin_events()
            print(s)
            p = connector.get_usernames_and_feed_id()
            print(p)
            q = connector.get_all_entries_by_feed_id(public_key_feed_id)
            print(q)
            m = connector.get_last_kotlin_event()
            print(m)
            assert True
            print(log_cap)

    finally:
        assert True
        try:
            if os.path.exists('eventDatabase.sqlite'):
                os.remove('eventDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')


def test_get_all_feed_ids():
    try:
        with LogCapture() as log_cap:
            private_key = secrets.token_bytes(32)
            signing_key = SigningKey(private_key)
            public_key_feed_id = signing_key.verify_key.encode()

            content = Content('whateverapp/whateveraction', {'somekey': 'somevalue', 'someotherkey': 1})
            hash_of_content = hashlib.sha256(content.get_as_cbor()).hexdigest()
            hash_of_prev = None
            meta = Meta(public_key_feed_id, 0, hash_of_prev, 'ed25519', ('sha256', hash_of_content))
            signature = signing_key.sign(meta.get_as_cbor())._signature
            event = Event(meta, signature, content).get_as_cbor()

            connector = DatabaseConnector()
            connector.add_event(event)
            result = connector.get_all_feed_ids()
        print(result)
        print(log_cap)
        assert True
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
            else:
                assert False
        except PermissionError:
            print('Database is still in use')
