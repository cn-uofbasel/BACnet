from feed import Feed, FeedMeta
from ..storage_controller import StorageController
from ..Storage.database_handler import UnknownFeedError
from owned_subfeed import OwnedSubFeed


class OwnedMasterFeed(Feed):
    """
    This class is the Interface to use the own master-feed of this Node. It has functionality that is related
    to import/export policies as well as to manage feeds.
    """

    def __init__(self, feed_id, storage_controller: StorageController):
        super().__init__(feed_id, storage_controller)

    def create_feed(self, name: str) -> OwnedSubFeed:
        """
        This Method tries to create a new feed with the given name. If the creation is successful, the New FeedInstance
        is returned. If not None is returned.
        """
        res = self.strg_ctrl.create_feed(name)
        if res:
            return OwnedSubFeed.owned_subfeed_from_feed(self.get_feed_by_id(res))
        else:
            raise FeedExistsError(name)

    def get_feed_by_id(self, feed_id):
        """
        This method tries to get generate an Interface Instance for the given feed_id.
        If the feed is unknown an UnknownFeedError is raised.
        """
        return self.strg_ctrl.get_feed(feed_id)

    def get_feed_by_name(self, name):
        """
        This Method takes a name and tries to generate an InterfaceInstance for a feed with the given name.
        If no feed is found, UnknownFeedError is raised.
        """
        self.get_feed_by_id(self.strg_ctrl.get_feed_id_for_name(name))

    def subscribe(self, feed_id):
        """
        This method tries to trust/subscribe to a feed with a given feed_id. Returns True if subscription was successful
        False if not.
        """
        self.strg_ctrl.subscribe(feed_id)

    def get_known_feeds(self, with_names=False):
        """
        Returns either a list of the feed_ids of all known feeds or a dict that contains all name-feed_id pairs that are
        known. If no name is determinable, None is a placeholder.
        """
        if with_names:
            return self.strg_ctrl.get_feed_name_list()
        else:
            return self.strg_ctrl.get_known_feeds()

    def set_radius(self, radius: int):
        """
        This Method sets the radius of the Node to a certain value.
        """
        self.strg_ctrl.get_database_handler().set_radius(radius)

    def get_radius(self):
        """
        This Method returns the current radius of this Node
        """
        return self.strg_ctrl.get_database_handler().get_radius()

    def get_stored_feeds(self):
        """
        This Method returns a list of feed_ids from all feeds that have events in the Database
        """
        return self.strg_ctrl.get_all_stored_feeds()

    def get_trusted_feeds(self):
        """
        This Method returns a list of feed_ids from all feeds, that are trusted on this node.
        """
        self.strg_ctrl.get_trusted_feeds()

    def get_owned_feeds(self):
        """
        This Method returns a list of feed_ids from all feeds, that are owned by this Node.
        """
        return self.strg_ctrl.get_owned_feeds()

    def block(self, feed_id):
        """
        This Method tries to block a feed with the given feed_id. The existence of a feed is not checked, so that
        every feed, even when unknown can be blocked.
        """
        self.strg_ctrl.block(feed_id)


class FeedExistsError(Exception):
    def __init__(self, message):
        super().__init__(f"The Feed: {message} is already in the database!")
