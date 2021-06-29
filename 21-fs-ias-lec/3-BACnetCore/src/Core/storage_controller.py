from pyeventbus3.pyeventbus3 import *
from .Eventbus.interface_message import InterfaceMessage
from .Eventbus.snyc_message import SyncMessage

from .Storage.database_handler import DatabaseHandler
from .event import Event

"""
The Storage Controller class is the main component in the BACNet Core it consists of methods that are triggered on certain
EventBus Messages. They are therefor used to insert Events into the Database
"""

class Storage_Controller:
    def __init__(self):
        PyBus.Instance().register(self, self.__class__.__name__)

    @subscribe(onEvent=InterfaceMessage)
    def dispatch_on_interface(self, event):
        pass

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

