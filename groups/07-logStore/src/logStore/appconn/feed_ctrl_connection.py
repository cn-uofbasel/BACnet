from .connection import Function


class FeedCtrlConnection(Function):

    def __init__(self):
        super(FeedCtrlConnection, self).__init__()

    def add_event(self, event):
        return self.__handler.add_to_db(event)

    def get_trusted(self, master_id):
        pass

    def get_blocked(self, master_id):
        pass

    def get_all_master_ids(self):
        pass

    def get_all_master_ids_feed_ids(self, master_id):
        pass

    def get_username(self, master_id):
        pass

    def get_my_last_event(self):
        pass

    def get_host_master_id(self):
        pass

    def get_radius(self):
        pass

    def get_master_id_from_feed(self, feed_id):
        pass

    def get_application_name(self, feed_id):
        pass

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        pass

    def get_feed_ids_in_radius(self):
        pass

    def set_feed_ids_radius(self, feed_id, radius):
        pass