from feed import Feed, FeedMeta
from pyeventbus3.pyeventbus3 import *
from ..Eventbus.interface_message import InterfaceMessage
from ..Eventbus.protocols import InterfaceProtocol


class OwnedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, master_id=None):
        super().__init__(feed_id, feed_meta)
        self.master_id = master_id

    def register(self, owned_master_feed):
        PyBus.Instance().register(owned_master_feed, self.__class__.__name__)

    def posting_an_event(self, interface_protocol: InterfaceProtocol, message=None):
        PyBus.Instance().post(InterfaceMessage(interface_protocol, message, id(self)))

    def create_feed(self):
        self.posting_an_event(InterfaceProtocol.create_feed)

    def get_feed(self, feed_id):
        self.posting_an_event(InterfaceProtocol.get_feed, feed_id)

    def subscribe(self, feed_id):
        self.posting_an_event(InterfaceProtocol.subscribe, feed_id)

    def unsubscribe(self, feed_id):
        self.posting_an_event(InterfaceProtocol.unsubscribe, feed_id)

    def get_available_feeds(self):
        self.posting_an_event(InterfaceProtocol.get_available_feeds)

    def set_radius(self, radius: int):
        self.posting_an_event(InterfaceProtocol.set_radius, radius)

    def get_master_id(self):
        return self.master_id

    def get_all_feeds(self):
        self.posting_an_event(InterfaceProtocol.get_all_feeds)

    def get_owned_feeds(self):
        self.posting_an_event(InterfaceProtocol.get_owned_feeds)

    def block(self, feed_id):
        self.posting_an_event(InterfaceProtocol.block, feed_id)

    def unblock(self, feed_id):
        self.posting_an_event(InterfaceProtocol.unblock, feed_id)

    def get_content(self, seq_num, feed_id):
        self.posting_an_event(InterfaceProtocol.get_content, feed_id)

    def get_current_seq_num(self, feed_id):
        self.posting_an_event(InterfaceProtocol.get_current_seq_number, feed_id)

    def get_last_event(self, feed_id):
        self.posting_an_event(InterfaceProtocol.get_last_event, feed_id)
