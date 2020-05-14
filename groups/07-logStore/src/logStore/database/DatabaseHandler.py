from .ByteArrayHandler import ByteArrayHandler, InvalidSequenceNumber
from .EventHandler import EventHandler, InvalidApplicationError
from functions.log import create_logger

logger = create_logger('DatabaseHandler')
"""The database handler allows both the application as well as the network layer to access database functionality.

It is strictly meant for internal purposes and should not be directly accesses or called by any module importing this
module.
"""


class DatabaseHandler:
    """Database handler gets each created by the database connector as well as the function connector.

    It has the private fields of an byte array handler as well as an event handler to access the two databases
    accordingly.
    """

    def __init__(self):
        self.__byteArrayHandler = ByteArrayHandler()
        self.__eventHandler = EventHandler()

    def add_to_db(self, event_as_cbor):
        """"Add a cbor event to the two databases.

        Calls each the byte array handler as well as the event handler to insert the event in both databases
        accordingly. Gets called both by database connector as well as the function connector. Returns 1 if successful,
        otherwise -1 if any error occurred.
        """
        try:
            self.__byteArrayHandler.insert_byte_array(event_as_cbor)
        except InvalidSequenceNumber as e:
            logger.error(e)
            return -1
        try:
            self.__eventHandler.add_event(event_as_cbor)
        except InvalidApplicationError as e:
            logger.error(e)
            return -1
        return 1

    def get_current_seq_no(self, feed_id):
        """"Return the current sequence number of a given feed_id, returns an integer with the currently largest
                sequence number for the given feed. Returns -1 if there is no such feed_id in the database."""
        return self.__byteArrayHandler.get_current_seq_no(feed_id)

    def get_event(self, feed_id, seq_no):
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
                there is no such entry."""
        return self.__byteArrayHandler.get_event(feed_id, seq_no)

    def get_current_event_as_cbor(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
                there is no such feed_id in the database."""
        return self.__byteArrayHandler.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids(self):
        """"Return all current feed ids in the database."""
        return self.__byteArrayHandler.get_all_feed_ids()

    def get_event_since(self, application, timestamp, feed_id, chat_id):
        return self.__eventHandler.get_event_since(application, timestamp, feed_id, chat_id)

    def get_all_chat_msgs(self, application, chat_id):
        return self.__eventHandler.get_all_events(application, chat_id)

    def get_usernames_and_publickey(self):
        return self.__eventHandler.get_Kotlin_usernames()

    def get_all_entries_by_publickey(self, publicKey):
        return self.__eventHandler.get_all_entries_by_publickey(publicKey)
