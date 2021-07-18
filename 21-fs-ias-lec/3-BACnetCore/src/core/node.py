from .storage_controller import StorageController
from .com_link import ComLink, OperationModes
from .interface.owned_masterfeed import OwnedMasterFeed
from ..constants import SQLITE


class Node:

    def __init__(self, operation_mode: OperationModes, channel, path="NodeBase.sqlite"):
        """
        :param operation_mode: (MANUAL or AUTOSYNC)
        :param channel: Communication channel to use
        """
        self.operation_mode = operation_mode
        self.channel = channel
        self.path_to_db = path
        self.db_type = SQLITE

        self.storage_controller = StorageController(self.path_to_db, self.db_type)
        self.com_link = ComLink(channel, operation_mode, self.storage_controller)
        self.storage_controller.set_com_link(self.com_link)
        self.owned_master_feed = self.storage_controller.get_owned_master()

        self.channel.start()

    def get_master(self) -> OwnedMasterFeed:
        return self.owned_master_feed

    def get_storage(self):
        return self.storage_controller

    def get_com_link(self):
        return self.com_link

    def manual_synchronize(self):
        self.storage_controller.sync()

    def shutdown(self):
        self.channel.stop()
        self.com_link.stop_autosync()
