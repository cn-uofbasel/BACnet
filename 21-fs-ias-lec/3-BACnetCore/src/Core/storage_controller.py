from pyeventbus3.pyeventbus3 import *
from .Eventbus.interface_message import InterfaceMessage
from .Eventbus.snyc_message import SyncMessage

from .Storage.database_handler import DatabaseHandler
from .event import Event

"""
The Storage Controller class is the main component in the BACNet Core it consists of methods that are triggered on certain
EventBus Messages. They are therefore used to insert Events into the Database
"""


class StorageController:

    def __init__(self):
        PyBus.Instance().register(self, self.__class__.__name__)

    @subscribe(onEvent=SyncMessage)
    def dispatch_on_replication(self, event):
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

    def get_storage_connectors(self):
        pass

    def insert_event(self, event: Event):
        pass

    @subscribe(threadMode=Mode.PARALLEL, onEvent=InterfaceMessage)
    def dispatch_on_interface(self, interface_message: InterfaceMessage):
        method_name = 'interface_' + str(interface_message.protocol.name)
        method = getattr(self, method_name, lambda: "Invalid protocol")
        return method(interface_message.message, interface_message.sender_id)

    def __interface_create_feed(self, message, sender_id):
        pass

    def __interface_get_feed(self, message, sender_id):
        pass

    def __interface_subscribe(self, message, sender_id):
        pass

    def __interface_unsubscribe(self, message, sender_id):
        pass

    def __interface_get_available_feeds(self, message, sender_id):
        pass

    def __interface_set_radius(self, message, sender_id):
        pass

    def __interface_get_all_feeds(self, message, sender_id):
        pass

    def __interface_get_owned_feeds(self, message, sender_id):
        pass

    def __interface_block(self, message, sender_id):
        pass

    def __interface_unblock(self, message, sender_id):
        pass

    def __interface_push(self, message, sender_id):
        pass

    def __interface_send(self, message, sender_id):
        pass

    def __interface_get_owner_id(self, message, sender_id):
        pass

    def __interface_receive(self, message, sender_id):
        pass

    def __interface_get_content(self, message, sender_id):
        pass

    def __interface_get_current_seq_number(self, message, sender_id):
        pass

    def __interface_get_last_event(self, message, sender_id):
        pass


