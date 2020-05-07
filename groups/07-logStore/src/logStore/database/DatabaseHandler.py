from .ByteArrayHandler import ByteArrayHandler
from .EventHandler import EventHandler
from functions.log import create_logger
from functions.Event import Event

logger = create_logger('DatabaseHandler')


class DatabaseHandler:

    def __init__(self):
        self.__byteArrayHandler = ByteArrayHandler()
        self.__eventHandler = EventHandler()

# Mixed operations

    def add_to_db(self, event_as_cbor):
        self.__byteArrayHandler.insert_byte_array(event_as_cbor)
        event = Event.from_cbor(event_as_cbor)
        # TODO: Handle event from here to event database

#  byte array operations:

    def get_current_seq_no(self, feed_id):
        res = self.__byteArrayHandler.get_current_seq_no(feed_id)
        return res

    def get_event(self, feed_id, seq_no):
        res = self.__byteArrayHandler.get_event(feed_id, seq_no)
        return res

    def get_current_event_as_cbor(self, feed_id):
        res = self.__byteArrayHandler.get_current_event_as_cbor(feed_id)
        return res

# TODO: Event operations:
