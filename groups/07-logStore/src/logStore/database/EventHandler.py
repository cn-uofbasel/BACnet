from functions.Singleton import Singleton
from .SqlAlchemyConnector import SqLiteDatabase
from functions.Constants import SQLITE
from functions.Event import Event


class EventHandler(metaclass=Singleton):

    def __init__(self):
        self.__sqlAlchemyConnector = SqLiteDatabase(SQLITE, dbname='eventDatabase.sqlite')
        self.__sqlAlchemyConnector.create_event_table()

    def init_event_table(self):
        return False

    def add_event(self, event_as_cbor):
        event = Event.from_cbor(event_as_cbor)
        seq_no = event.meta.seq_no
        feed_id = event.meta.feed_id.decode()
        # TODO: fix problem with the timestamp in content
        application, timestamp, content = Event.Content.from_cbor(event)

        self.__sqlAlchemyConnector.insert_event(feed_id=feed_id, seq_no=seq_no, application=application,
                                                timestamp=timestamp, data=content)

    def get_event_since(self, application, timestamp):
        return self.__sqlAlchemyConnector.get_all_events_since(self, application, timestamp)

    def get_all_events(self, application):
        return self.__sqlAlchemyConnector.get_all_event_from_application(application)

    def create_table_for_feed(self, feedId):
        pass

    def read_data_from_event(self, byteArray):
        pass
