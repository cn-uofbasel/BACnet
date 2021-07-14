from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class OwnedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController):
        super().__init__(feed_id, feed_meta, storage_controller)

    def create_feed(self):
        return self.strg_ctrl.create_feed()

    def get_feed(self, feed_id):
        return self.strg_ctrl.get_feed(feed_id)

    def subscribe(self, feed_id):
        self.strg_ctrl.subscribe(feed_id)

    def unsubscribe(self, feed_id):
        self.strg_ctrl.unsubscribe(feed_id)

    def get_available_feeds(self):
        return self.strg_ctrl.get_available_feeds()

    def set_radius(self, radius: int):
        self.strg_ctrl.set_radius(radius)

    def get_all_feeds(self):
        return self.strg_ctrl.get_all_feeds()

    def get_owned_feeds(self):
        return self.strg_ctrl.get_owned_feeds()

    def block(self, feed_id):
        self.strg_ctrl.block(feed_id)

    def unblock(self, feed_id):
        self.strg_ctrl.unblock(feed_id)

