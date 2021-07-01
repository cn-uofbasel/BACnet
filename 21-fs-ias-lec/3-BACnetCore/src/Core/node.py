from Interface.owned_masterfeed import OwnedMasterFeed
from Storage.event_factory import EventFactory
from storage_controller import StorageController
from com_link import ComLink


class Node:

    def __init__(self, operation_mode, channels, storage=None):
        self.operation_mode = operation_mode
        self.channels = channels
        self.storage = storage

        self.com_link = ComLink()
        self.storage_controller = StorageController()
        self.event_factory = EventFactory(self.storage_controller)

        self.owned_master_feed = OwnedMasterFeed(self.event_factory.create_new_feed(self.event_factory), self.storage_controller)

    def get_master(self):
        return self.owned_master_feed

    def get_storage(self):
        return self.storage_controller

    def get_com_link(self):
        return self.com_link

    def get_channels(self):
        pass

    def add_channel(self):
        pass

    def remove_channel(self):
        pass

    def shutdown(self):
        pass
