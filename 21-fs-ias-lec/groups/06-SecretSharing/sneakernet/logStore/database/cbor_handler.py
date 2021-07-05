from .sql_alchemy_connector import SqLiteDatabase
from ..funcs.log import create_logger
from ..funcs.constants import SQLITE
from ..funcs.singleton import Singleton
from ..funcs.event import Event

logger = create_logger('ByteArrayHandler')
"""The byte array handler allows the database handler to insert a new event into the cbor database.

It is strictly meant for internal purposes and should not be directly accesses or called by any module importing this
module.
"""


class ByteArrayHandler(metaclass=Singleton):
    """Byte Array Handler gets created once by the database handler.

    It has the metaclass singleton to be allowed to be created only once as there should not be more than one handler
    created by each callee. The init function initiates the database variable and creates the needed tables in
    the database.
    """

    def __init__(self):
        self.__sqlAlchemyConnector = SqLiteDatabase(SQLITE, dbname='cborDatabase.sqlite')
        self.__sqlAlchemyConnector.create_cbor_db_tables()

    def insert_byte_array(self, event_as_cbor):
        """"Insert a new event into the database. For this we extract the sequence number and feed_id and store the
        exact cbor event with those values as keys."""
        event = Event.from_cbor(event_as_cbor)
        seq_no = event.meta.seq_no
        feed_id = event.meta.feed_id
        self.__sqlAlchemyConnector.insert_byte_array(feed_id, seq_no, event_as_cbor)

    def get_current_seq_no(self, feed_id):
        """"Return the current sequence number of a given feed_id, returns an integer with the currently largest
        sequence number for the given feed. Returns -1 if there is no such feed_id in the database."""
        return self.__sqlAlchemyConnector.get_current_seq_no(feed_id)

    def get_event(self, feed_id, seq_no):
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
        there is no such entry."""
        return self.__sqlAlchemyConnector.get_event(feed_id, seq_no)

    def get_current_event_as_cbor(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
        there is no such feed_id in the database."""
        return self.__sqlAlchemyConnector.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids(self):
        """"Return all current feed ids in the database."""
        return self.__sqlAlchemyConnector.get_all_feed_ids()


class InvalidSequenceNumber(Exception):
    def __init__(self, message):
        super(InvalidSequenceNumber, self).__init__(message)
