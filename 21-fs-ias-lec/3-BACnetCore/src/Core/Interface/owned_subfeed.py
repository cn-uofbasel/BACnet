from feed import Feed, FeedMeta
from event import Content
from ..storage_controller import StorageController


class OwnedSubFeed(Feed):

    def __init__(self, feed_id, storage_controller: StorageController):
        super().__init__(feed_id, storage_controller)

    def insert_event(self, content: Content):
        self.strg_ctrl.insert_event(self.feed_id, content)

    @classmethod
    def owned_subfeed_from_feed(cls, feed: Feed):
        return OwnedSubFeed(feed.feed_id, feed.strg_ctrl)
