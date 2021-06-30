from feed import Feed, FeedMeta
from pyeventbus3.pyeventbus3 import *
from ..Eventbus.interface_message import InterfaceMessage
from ..Eventbus.protocols import InterfaceProtocol


class SubscribedSubFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta):
        super().__init__(feed_id, feed_meta)

    def register(self, owned_master_feed):
        PyBus.Instance().register(owned_master_feed, self.__class__.__name__)

    def posting_an_event(self, interface_protocol: InterfaceProtocol, message=None):
        PyBus.Instance().post(InterfaceMessage(interface_protocol, message, id(self)))

    def get_owner_id(self):
        self.posting_an_event(InterfaceProtocol.get_owner_id)

    def receive(self):
        self.posting_an_event(InterfaceProtocol.receive)

    def get_content(self, seq_num, feed_id):
        self.posting_an_event(InterfaceProtocol.get_content, feed_id)

    def get_current_seq_num(self, feed_id):
        self.posting_an_event(InterfaceProtocol.get_current_seq_number, feed_id)

    def get_last_event(self, feed_id):
        self.posting_an_event(InterfaceProtocol.get_last_event, feed_id)
