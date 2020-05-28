from .connection import Function


class KotlinFunction(Function):
    """Connection to the group kotlin to insert and output the chat elements"""

    def __init__(self):
        super(KotlinFunction, self).__init__()

    def insert_data(self, cbor):
        """adds a new chat element as cbor

        @:parameter event: The new cbor event to be added
        @:returns 1 if successful, -1 if any error occurred
        """
        self.insert_event(cbor)

    def get_usernames_and_feed_id(self):
        """Get all current usernames with the corresponding feed id

        @:returns a list with all Kotlin usernames and the corresponding feed id
        """
        return self._handler.get_usernames_and_feed_id()

    def get_all_entries_by_feed_id(self, feed_id):
        """Get all elements with the corresponding feed id, thus all events of a user

        @:parameter feed_id: the feed id of a user
        @:returns a list of all Kotlin entries with the correct feed id
        """
        return self._handler.get_all_entries_by_feed_id(feed_id)

    def get_all_kotlin_events(self):
        """Get all existing kotlin elements that are in the database

        @:returns a list of all Kotlin entries
        """
        return self._handler.get_all_kotlin_events()

    def get_last_kotlin_event(self):
        """Get only the last added kotlin element

        @:returns a only the last Kotlin entry as cbor
        """
        return self._handler.get_last_kotlin_event()
