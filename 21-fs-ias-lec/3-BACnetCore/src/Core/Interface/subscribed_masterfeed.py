from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class SubscribedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController, master_id=None):
        super().__init__(feed_id, feed_meta)
        self.master_id = master_id
        self.storage_controller = storage_controller

    def get_owner_id(self):
        self.storage_controller.get_owner_id(self.feed_id)

    def receive(self):
        self.storage_controller.receive(self.feed_id)

    def get_content(self, seq_num, feed_id):
        return self.storage_controller.get_content(self.feed_id, seq_num, feed_id)

    def get_current_seq_num(self, feed_id):
        return self.storage_controller.get_current_seq_num(self.feed_id, feed_id)

    def get_last_event(self, feed_id):
        return self.storage_controller.get_last_event(self.feed_id, feed_id)
