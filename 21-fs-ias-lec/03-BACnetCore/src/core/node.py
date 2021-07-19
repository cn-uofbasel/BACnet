from .storage_controller import StorageController
from .com_link import ComLink, OperationModes
from .interface.owned_masterfeed import OwnedMasterFeed
from ..constants import SQLITE


class Node:
    """
    This class is the main class for every Node in the BACnet. It creates all components such as the com-link and
    Storage-controller and serves basic functionality to retrieve the components and shut down the Node.
    """

    def __init__(self, operation_mode: OperationModes, channel, path="NodeBase.sqlite"):
        """
        :param operation_mode: (MANUAL or AUTOSYNC)
        :param channel: Communication channel to use
        :param: path: the path to the database to create or load
        """
        self.operation_mode = operation_mode
        self.channel = channel
        self.path_to_db = path
        self.db_type = SQLITE
        # initialize all main components
        self.storage_controller = StorageController(self.path_to_db, self.db_type)
        self.com_link = ComLink(channel, operation_mode, self.storage_controller)
        self.storage_controller.set_com_link(self.com_link)
        self.owned_master_feed = self.storage_controller.get_owned_master()
        # automatically start the channel when initialization is finished
        self.channel.start()

    def get_master(self) -> OwnedMasterFeed:
        """
        This method returns an Interface Instance of the Owned MasterFeed of this Node.
        (The Masterfeed is automatically created when creating a Database for the first time)
        """
        return self.owned_master_feed

    def get_storage(self):
        """
        Returns the Node's Storage-Controller so that the user can have better manual access to the functionality
        if needed. (Ex another application need in_depth access to internals or to functionality not yet served
        by the Interface.)
        """
        return self.storage_controller

    def get_com_link(self):
        """
        Returns the Node's Com-Link Instance so that the user can have better manual control/access if needed.
        """
        return self.com_link

    def manual_synchronize(self):
        """
        No matter which operation mode the com link is in, you can trigger the synchronization manually.
        This method HAVE TO be used when using the MANUAL OperationMode.
        """
        self.storage_controller.sync()

    def shutdown(self):
        """
        When shutting down a node, all threads need to be terminated. All other instances are automatically closed.
        Should ALWAYS be called at the end of a program that uses this package
        """
        self.com_link.stop_autosync()
        self.channel.stop()
