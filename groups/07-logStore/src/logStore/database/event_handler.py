from ..funcs.singleton import Singleton
from .sql_alchemy_connector import SqLiteDatabase
from ..funcs.constants import SQLITE
from ..funcs.event import Event
from ..funcs.log import create_logger

logger = create_logger('EventHandler')


class EventHandler(metaclass=Singleton):

    def __init__(self):
        self.__sqlAlchemyConnector = SqLiteDatabase(SQLITE, dbname='eventDatabase.sqlite')
        self.__sqlAlchemyConnector.create_chat_event_table()
        self.__sqlAlchemyConnector.create_kotlin_table()

    def add_event(self, event_as_cbor):
        event = Event.from_cbor(event_as_cbor)
        seq_no = event.meta.seq_no
        feed_id = event.meta.feed_id
        content = event.content.content

        cont_ident = content[0].split('/')
        application = cont_ident[0]

        if application == 'chat':
            chatMsg = content[1]['messagekey']
            chat_id = content[1]['chat_id']
            timestamp = content[1]['timestampkey']

            self.__sqlAlchemyConnector.insert_event(feed_id=feed_id, seq_no=seq_no, application=application,
                                                    chat_id=chat_id,
                                                    timestamp=timestamp, data=chatMsg)

        elif application == 'KotlinUI':
            username = content[1]['username']
            timestamp = content[1]['timestamp']
            text = content[1]['text']
            self.__sqlAlchemyConnector.insert_kotlin_event(feed_id=feed_id, seq_no=seq_no, application=application,
                                                           username=username,
                                                           timestamp=timestamp, text=text)

        elif application == 'MASTER':
            self.master_handler(seq_no, feed_id, content, cont_ident)

        else:
            raise InvalidApplicationError('Invalid application called %s' % application)

    def get_event_since(self, application, timestamp, chat_id):
        return self.__sqlAlchemyConnector.get_all_events_since(application, timestamp, chat_id)

    def get_all_events(self, application, chat_id):
        return self.__sqlAlchemyConnector.get_all_event_with_chat_id(application, chat_id)

    def get_Kotlin_usernames(self):
        return self.__sqlAlchemyConnector.get_all_usernames()

    def get_all_kotlin_events(self, feed_id):
        return self.__sqlAlchemyConnector.get_all_kotlin_events(feed_id=feed_id)

    def get_all_entries_by_feed_id(self, feed_id):
        return self.__sqlAlchemyConnector.get_all_entries_by_feed_id(feed_id)

    def get_last_kotlin_event(self):
        return self.__sqlAlchemyConnector.get_last_kotlin_event()

    def master_handler(self, seq_no, feed_id, content, cont_ident):
        event = cont_ident[1]
        if event == 'MASTER':
            self.__sqlAlchemyConnector.insert_master_event(True, feed_id, None, None, seq_no, None, None, None, 0)
        elif event == 'Trust':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, True,
                                                           False, None, None)
        elif event == 'Untrust':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, False,
                                                           True, None, None)
        elif event == 'Name':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no, None, None,
                                                           content[1]['name'], None)
        elif event == 'NewFeed':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, content[1]['feed_id'], None, seq_no, True,
                                                           False, None, None)
        elif event == 'Block':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, False,
                                                           True, None, None)
        elif event == 'Unblock':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, True,
                                                           False, None, None)
        elif event == 'Radius':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no, None,
                                                           None, None, content[1]['radius'])
        else:
            raise InvalidApplicationError('Invalid action called %s' % event)


class InvalidApplicationError(Exception):
    def __init__(self, message):
        super(InvalidApplicationError, self).__init__(message)
