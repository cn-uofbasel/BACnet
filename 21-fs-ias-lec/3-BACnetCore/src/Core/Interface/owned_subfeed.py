from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class OwnedSubFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController):
        super().__init__(feed_id, feed_meta, storage_controller)

    def push(self, datatype, data):
        self.strg_ctrl.push(self.feed_id, datatype, data)

    def send(self):
        self.strg_ctrl.send(self.feed_id)

