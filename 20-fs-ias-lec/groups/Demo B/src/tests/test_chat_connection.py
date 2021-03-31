from testfixtures import LogCapture
import os
from ..logStore.appconn.chat_connection import ChatFunction
from ..logStore.funcs.EventCreationTool import EventFactory


def test_get_chat_event():
    try:
        with LogCapture() as log_cap:
            ecf = EventFactory()

            cf = ChatFunction()

            new_event = ecf.next_event('MASTER/MASTER', {})
            cf.insert_event(new_event)

            feed = EventFactory()
            feed2 = EventFactory()
            feed3 = EventFactory()

            new_event = feed.next_event('chat/MASTER', {'master_feed': ecf.get_feed_id()})
            cf.insert_event(new_event)

            new_event = feed2.next_event('chat/MASTER', {'master_feed': ecf.get_feed_id()})
            cf.insert_event(new_event)

            new_event = feed3.next_event('chat/MASTER', {'master_feed': ecf.get_feed_id()})
            cf.insert_event(new_event)

            new_event = feed.next_event('chat/whateveraction',
                                        {'messagekey': 'hallo zusammen', 'chat_id': '1', 'timestampkey': 10})
            cf.insert_event(new_event)

            new_event = feed.next_event('chat/whateveraction',
                                        {'messagekey': 'wie gehts?', 'chat_id': '1', 'timestampkey': 20})
            cf.insert_event(new_event)

            new_event = feed.next_event('chat/whateveraction',
                                        {'messagekey': 'schönes Wetter heute', 'chat_id': '1', 'timestampkey': 30})
            cf.insert_event(new_event)

            print(log_cap)
            q = cf.get_chat_since(15, '1')
            assert q[0][0] == 'wie gehts?'
            assert q[1][0] == 'schönes Wetter heute'
            t = cf.get_full_chat('1')
            assert t[0][0] == 'hallo zusammen'
            assert t[1][0] == 'wie gehts?'
            assert t[2][0] == 'schönes Wetter heute'
        assert True
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
