from .storage_controller import StorageController
from .com_link import ComLink, OperationModes
from .interface.owned_masterfeed import OwnedMasterFeed
from ..constants import SQLITE


class Node:

    def __init__(self, operation_mode: OperationModes, channel):
        """
        :param operation_mode: (MANUAL or AUTOSYNC)
        :param channel: Communication channel to use
        """
        self.operation_mode = operation_mode
        self.channels = channel
        self.path_to_db = "NodeBase.sqlite"
        self.db_type = SQLITE

        self.com_link = None
        self.storage_controller = StorageController(self.path_to_db, self.db_type, self)
        self.com_link = ComLink(channel, OperationModes.MANUAL, self)

        self.owned_master_feed = self.storage_controller.get_owned_master()

    def get_master(self) -> OwnedMasterFeed:
        return self.owned_master_feed

    def get_storage(self):
        return self.storage_controller

    def get_com_link(self):
        return self.com_link

    def shutdown(self):
        pass
