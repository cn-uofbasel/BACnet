from .Function import Function


class KotlinFunktion(Function):

    def insert_data(self, data):
        return False

    def set_data_structure(self, data_type):
        pass

    def retrieve_data_since(self, hash):
        pass

    def get_usernames_and_feed_id(self):
        return self.__handler.get_usernames_and_feed_id()

    def get_all_entries_by_feed_id(self, feed_id):
        return self.__handler.get_all_entries_by_feed_id(feed_id)

    def get_all_kotlin_event(self):
        return self.__handler.get_all_kotlin_events()

    def get_last_kotlin_event(self):
        return self.__handler.get_last_kotlin_event()
