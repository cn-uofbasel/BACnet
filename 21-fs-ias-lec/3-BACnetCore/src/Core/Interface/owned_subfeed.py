from feed import Feed, FeedMeta
from ..storage_controller import StorageController


class OwnedSubFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController):
        super().__init__(feed_id, feed_meta)
        self.storage_controller = storage_controller

    def push(self, datatype, data):
        self.storage_controller.push(self.feed_id, datatype, data)

    def send(self):
        self.storage_controller.send(self.feed_id)

    def get_content(self, seq_num, feed_id):
        return self.storage_controller.get_content(self.feed_id, seq_num, feed_id)

    def get_current_seq_num(self, feed_id):
        return self.storage_controller.get_current_seq_num(self.feed_id, feed_id)

    def get_last_event(self, feed_id):
        return self.storage_controller.get_last_event(self.feed_id, feed_id)
