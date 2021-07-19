from .feed import Feed
from .event import Content


class OwnedSubFeed(Feed):
    """
     Instances of this class represent feeds that are owned by this node and are not the masterfeed.
     Additional to the normal feed-functionality (Feed class), this class adds the functionality to insert Events into
     the feed.
     """
    def __init__(self, feed_id, storage_controller):
        super().__init__(feed_id, storage_controller)

    def insert_event(self, content: Content):
        """
        This Method takes a Content-Instance as argument and uses the StorageController to insert this Event into the
        Feed. Never use MASTER as first part of the Content identifier since it is reserved for Masters only and can
        cause Errors and corrupted Data!
        """
        self.strg_ctrl.insert_event(self.feed_id, content)

    @classmethod
    def owned_subfeed_from_feed(cls, feed: Feed):
        """
        Utility to Downcast a given Feed-Instance to an OwnedSubfeed Instance.
        """
        return OwnedSubFeed(feed.feed_id, feed.strg_ctrl)
