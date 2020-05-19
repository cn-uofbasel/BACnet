from ..database.database_handler import DatabaseHandler


class Function:

    def __init__(self):
        self._handler = DatabaseHandler()

    def get_feed_ids(self):
        pass

    def insert_event(self, cbor):
        self._handler.add_to_db(event_as_cbor=cbor, app=True)

    def get_event(self, feed_id):
        pass

    def get_all_events_since(self, feed_id):
        pass

    def get_full_feed(self, feed_id):
        pass

    def get_last_event(self, feed_id):
        return self._handler.get_current_event_as_cbor(feed_id)
