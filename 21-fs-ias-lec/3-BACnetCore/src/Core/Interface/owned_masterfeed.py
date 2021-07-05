from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class OwnedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController, master_id=None):
        super().__init__(feed_id, feed_meta)
        self.feed_id = feed_id
        self.master_id = master_id
        self.storage_controller = storage_controller

    def create_feed(self):
        return self.storage_controller.create_feed()

    def get_feed(self, feed_id):
        return self.storage_controller.get_feed(feed_id)

    def subscribe(self, feed_id):
        self.storage_controller.subscribe(feed_id)

    def unsubscribe(self, feed_id):
        self.storage_controller.unsubscribe(feed_id)

    def get_available_feeds(self):
        return self.storage_controller.get_available_feeds()

    def set_radius(self, radius: int):
        self.storage_controller.set_radius(radius)

    def get_master_id(self):
        return self.master_id

    def get_all_feeds(self):
        return self.storage_controller.get_all_feeds()

    def get_owned_feeds(self):
        return self.storage_controller.get_owned_feeds()

    def block(self, feed_id):
        self.storage_controller.block(feed_id)

    def unblock(self, feed_id):
        self.storage_controller.unblock(feed_id)

    def get_content(self, seq_num, feed_id):
        return self.storage_controller.get_content(self.feed_id, seq_num, feed_id)

    def get_current_seq_num(self, feed_id):
        return self.storage_controller.get_current_seq_num(self.feed_id, feed_id)

    def get_last_event(self, feed_id):
        return self.storage_controller.get_last_event(self.feed_id, feed_id)
