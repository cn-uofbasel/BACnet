"""
The Storage Controller class is the main component in the BACNet Core it consists of methods that are triggered by feeds
They are therefore used to insert Events into the Database
"""


class StorageController:

    def __init__(self, database_connector):
        self.database_connector = database_connector

    def get_storage_connectors(self):
        pass

    def _insert_event(self):
        pass

    def _insert_and_verify_event(self):
        pass

    def _verify_event(self):
        pass

    def _get_masters_info(self):
        pass

    def _get_feed_info(self):
        pass

    def _get_config_info(self):
        pass

    def _set_config(self):
        pass

    def _import_event(self):
        pass

    def _export_event(self):
        pass

    def _verification(self):
        pass

    def _filter(self):
        pass

    def _get_information(self):
        pass

    def create_feed(self):
        pass

    def get_feed(self, feed_id):
        pass

    def subscribe(self, feed_id):
        pass

    def unsubscribe(self, feed_id):
        pass

    def get_available_feeds(self):
        pass

    def set_radius(self, radius: int):
        pass

    def get_all_feeds(self):
        pass

    def get_owned_feeds(self):
        pass

    def block(self, feed_id):
        pass

    def unblock(self, feed_id):
        pass

    def get_content(self, own_id, seq_num, feed_id):
        pass

    def get_current_seq_num(self, own_id, feed_id):
        pass

    def get_last_event(self, own_id, feed_id):
        pass

    def get_owner_id(self, own_id):
        pass

    def receive(self, own_id):
        pass

    def push(self, own_id, datatype, data):
        pass

    def send(self, own_id):
        pass
