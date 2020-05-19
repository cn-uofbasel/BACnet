from ..database.database_handler import DatabaseHandler


class Function:

    def __init__(self):
        self.__handler = DatabaseHandler()

    def get_feed_ids(self):
        pass

    def insert_event(self, cbor):
        self.__handler.add_to_db(event_as_cbor=cbor, app=True)

    def get_event(self, feedId, Hash):
        pass

    def get_all_events_since(self, feedId, Hash):
        pass

    def get_full_feed(self, feedId):
        pass

    def get_last_event(self, feed_id):
        return self.__handler.get_current_event_as_cbor(feed_id)
