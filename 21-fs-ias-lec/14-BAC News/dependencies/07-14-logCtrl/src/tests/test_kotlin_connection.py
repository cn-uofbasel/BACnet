from testfixtures import LogCapture
import os
from contextlib import contextmanager
from logStore.funcs.event import Content, Event, Meta
from logStore.appconn.kotlin_connection import KotlinFunction
from logStore.funcs.EventCreationTool import EventFactory
from logStore.funcs.log import create_logger


logger = create_logger('test_get_kotlin_event')

def test_get_kotlin_event():
    with session_scope():
        with LogCapture() as log_cap:
            ecf = EventFactory()

            kf = KotlinFunction()

            new_event = ecf.next_event('MASTER/MASTER', {})
            kf.insert_event(new_event)

            feed = EventFactory()
            feed2 = EventFactory()
            feed3 = EventFactory()

            new_event = feed.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
            kf.insert_event(new_event)

            new_event = feed2.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
            kf.insert_event(new_event)

            new_event = feed3.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
            kf.insert_event(new_event)

            new_event = feed.next_event('KotlinUI/username',
                                        {'newUsername': 'Bob', 'oldUsername': '',
                                         'timestamp': 1})
            kf.insert_event(new_event)

            new_event = feed2.next_event('KotlinUI/username',
                                         {'newUsername': 'Alice', 'oldUsername': '', 'timestamp': 2})
            kf.insert_event(new_event)

            new_event = feed3.next_event('KotlinUI/username',
                                         {'newUsername': 'Max', 'oldUsername': '', 'timestamp': 3})
            kf.insert_event(new_event)

            new_event = feed.next_event('KotlinUI/post',
                                        {'text': 'Hi Alice, nice to hear from you', 'username': 'Bob',
                                         'timestamp': 11})
            kf.insert_event(new_event)

            new_event = feed2.next_event('KotlinUI/post',
                                         {'text': 'Hi Bob', 'username': 'Alice', 'timestamp': 15})
            kf.insert_event(new_event)

            new_event = feed3.next_event('KotlinUI/post',
                                         {'text': 'Hello everyone', 'username': 'Max',
                                          'timestamp': 17})
            kf.insert_event(new_event)

            new_event = feed2.next_event('KotlinUI/username',
                                         {'newUsername': 'Alice2', 'oldUsername': 'Alice', 'timestamp': 20})
            kf.insert_event(new_event)

            s = kf.get_all_kotlin_events()
            print(s)
            assert s[0][0] == 'username'
            assert s[1][0] == 'username'
            assert s[3][0] == 'post'
            p = kf.get_usernames_and_feed_id()
            print(p)
            assert p[0][0] == 'Bob'
            assert p[1][0] == 'Alice2'
            q = kf.get_all_entries_by_feed_id(feed.get_feed_id())
            print(q)
            assert q[0][3] == 1
            assert q[1][2] == 11
            m = kf.get_last_kotlin_event()
            t = Event.from_cbor(m)
            assert t.content.content[0] == 'KotlinUI/username'
            assert True
            print(log_cap)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield
    except Exception as e:
        logger.error(e)
        raise
    finally:
        try:
            if os.path.exists('cborDatabase.sqlite'):
                os.remove('cborDatabase.sqlite')
                if os.path.exists('eventDatabase.sqlite'):
                    os.remove('eventDatabase.sqlite')
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
