from Interface.owned_masterfeed import OwnedMasterFeed
from Storage.EventFactory import EventFactory
from storage_controller import StorageController
from pyeventbus3.pyeventbus3 import *
from .Eventbus.interface_message import InterfaceMessage
from .Eventbus.snyc_message import SyncMessage


class Node:

    def __init__(self, operation_mode, channels, storage=None):
        PyBus.Instance().register(self, self.__class__.__name__)
        self.operation_mode = operation_mode
        self.channels = channels
        self.storage = storage

        self.dbase_conn = StorageController()
        self.event_factory = EventFactory(self.dbase_conn)

        self.owned_master_feed = OwnedMasterFeed(self.event_factory.create_new_feed(self.event_factory), )
        # TODO FeedMeta?
        self.owned_master_feed.register(self.owned_master_feed)

    def get_master(self):
        pass

    def get_channels(self):
        pass

    def add_channel(self):
        pass

    def get_storage(self):
        pass

    def get_com_link(self):
        pass

    def remove_channel(self):
        pass

    def shutdown(self):
        pass
