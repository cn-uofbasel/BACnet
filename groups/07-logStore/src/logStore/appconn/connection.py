from ..database.database_handler import DatabaseHandler


class Function:

    def __init__(self):
        self._handler = DatabaseHandler()

    def insert_event(self, cbor):
        self._handler.add_to_db(event_as_cbor=cbor, app=True)

    def get_last_event(self, feed_id):
        return self._handler.get_current_event_as_cbor(feed_id)
