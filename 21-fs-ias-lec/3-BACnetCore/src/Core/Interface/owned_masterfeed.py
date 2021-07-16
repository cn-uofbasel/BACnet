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
        """
        names = self.strg_ctrl.get_feed_name_list()
        if name in names.keys():
            return self.get_feed_by_id(names[name])
        else:
            raise UnknownFeedError(name)

    def subscribe(self, feed_id):
        self.strg_ctrl.subscribe(feed_id)

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


class FeedExistsError(Exception):
    def __init__(self, message):
        super().__init__(f"The Feed: {message} is already in the database!")
