from feed import Feed
from ..storage_controller import StorageController


class SubscribedSubFeed(Feed):
    """
    This class represents a Feed which is not owned by another Node and is not It's master_feed.
    Additional to the normal feed-functionality it has a method to determine the Owner/Master of this feed
    """

    def __init__(self, feed_id, storage_controller: StorageController):
        super().__init__(feed_id, storage_controller)

    def get_owner_id(self):
        """
        This method returns the master_id of the Masterfeed, that owns this Subfeed. If no Master is found or this feed
        is unknown(should never be the case in normal use of this library), None is returned
        """
        return self.strg_ctrl.get_database_handler().get_master_id_from_feed(self.feed_id)


