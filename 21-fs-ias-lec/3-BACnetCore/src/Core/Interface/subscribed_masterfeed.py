from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class SubscribedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController):
        super().__init__(feed_id, feed_meta, storage_controller)

    def get_owner_id(self):
        self.strg_ctrl.get_owner_id(self.feed_id)

    def receive(self):
        self.strg_ctrl.receive(self.feed_id)

