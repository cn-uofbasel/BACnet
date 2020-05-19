from .connection import Function


class FeedCtrlConnection(Function):

    def __init__(self):
        super(FeedCtrlConnection, self).__init__()

    def add_event(self, event):
        return super().insert_event(event)

    def get_trusted(self, master_id):
        return self.__handler.get_trusted(master_id)

    def get_blocked(self, master_id):
        return self.__handler.get_blocked(master_id)

    def get_all_master_ids(self):
        return self.__handler.get_all_master_ids()

    def get_all_master_ids_feed_ids(self, master_id):
        return self.__handler.get_all_master_ids_feed_ids(master_id)

    def get_username(self, master_id):
        return self.__handler.get_username(master_id)

    def get_my_last_event(self):
        return self.__handler.get_my_last_event()

    def get_host_master_id(self):
        return self.__handler.get_host_master_id()

    def get_radius(self):
        return self.__handler.get_radius()

    def get_master_id_from_feed(self, feed_id):
        return self.__handler.get_master_id_from_feed(feed_id)

    def get_application_name(self, feed_id):
        return self.__handler.get_application_name(feed_id)

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        return self.__handler.get_feed_ids_from_application_in_master_id(master_id, application_name)

    def get_feed_ids_in_radius(self):
        return self.__handler.get_feed_ids_in_radius()

    def set_feed_ids_radius(self, feed_id, radius):
        return self.__handler.set_feed_ids_radius(feed_id, radius)