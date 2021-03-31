import secrets

from testfixtures import LogCapture
import os
from logStore.appconn.ratchet_chat_connection import RatchetChatFunction

from logStore.funcs.EventCreationTool import EventFactory
from logStore.funcs.log import create_logger

logger = create_logger('test_chat_connection')


def test_get_ratchet_chat_event():
    with LogCapture() as log_cap:
        ecf = EventFactory()

        cf = RatchetChatFunction()

        private_key1 = secrets.token_bytes(32)
        private_key2 = secrets.token_bytes(32)
        private_key3 = secrets.token_bytes(32)

        special_key1 = secrets.token_bytes(32)
        special_key2 = secrets.token_bytes(32)
        special_key3 = secrets.token_bytes(32)

        new_event = ecf.next_event('MASTER/MASTER', {})
        cf.insert_event(new_event)

        feed = EventFactory()
        feed2 = EventFactory()
        feed3 = EventFactory()

        new_event = feed.next_event('ratchet/MASTER', {'master_feed': ecf.get_feed_id()})
        cf.insert_event(new_event)

        new_event = feed2.next_event('ratchet/MASTER', {'master_feed': ecf.get_feed_id()})
        cf.insert_event(new_event)

        new_event = feed3.next_event('ratchet/MASTER', {'master_feed': ecf.get_feed_id()})
        cf.insert_event(new_event)

        new_event = feed.next_event('ratchet/whateveraction',
                                    {'messagekey': private_key1, 'chat_id': '1', 'timestampkey': 10,
                                     'special_key': special_key1})
        cf.insert_event(new_event)

        new_event = feed.next_event('ratchet/whateveraction',
                                    {'messagekey': private_key2, 'chat_id': '1', 'timestampkey': 20,
                                     'special_key': special_key2})
        cf.insert_event(new_event)

        new_event = feed.next_event('ratchet/whateveraction',
                                    {'messagekey': private_key3, 'chat_id': '1', 'timestampkey': 30,
                                     'special_key': special_key3})
        cf.insert_event(new_event)

        print(log_cap)
        q = cf.get_ratchet_chat_since(15, '1')
        assert q[0][0] == private_key2
        assert q[1][0] == private_key3
        t = cf.get_full_ratchet_chat('1')
        assert t[0][0] == private_key1
        assert t[1][0] == private_key2
        assert t[2][0] == private_key3
    assert True

    try:
        if os.path.exists('cborDatabase.sqlite'):
            os.remove('cborDatabase.sqlite')
            directory = "./"
            files_in_directory = os.listdir(directory)
            filtered_files = [file for file in files_in_directory if file.endswith(".key")]
            for file in filtered_files:
                path_to_file = os.path.join(directory, file)
                os.remove(path_to_file)
        else:
            assert False

    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    test_get_ratchet_chat_event()
