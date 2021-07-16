from feed import Feed
from ..storage_controller import StorageController


class SubscribedMasterFeed(Feed):
    """
    This Interface-Class is used to work with foreign Master Feeds. Additional to normal Feed functionality one can
    get information about owned/trusted feeds by this master. Furthermore
    """
    def __init__(self, feed_id, storage_controller: StorageController):
        super().__init__(feed_id, storage_controller)

    def get_username(self):
        self.strg_ctrl.get_database_handler().get_username(self.feed_id)

    def get_trusted_feeds(self):
        self.strg_ctrl.get_database_handler().get_trusted(self.feed_id)

    def get_subfeeds(self):
        self.strg_ctrl.get_database_handler().get_all_master_ids_feed_ids(self.feed_id)


