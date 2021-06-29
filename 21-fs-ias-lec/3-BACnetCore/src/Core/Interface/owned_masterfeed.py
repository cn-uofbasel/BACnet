from feed import Feed, FeedMeta


class OwnedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, master_id):
        super().__init__(feed_id, feed_meta)
        self.master_id = master_id

    def create_feed(self):
        pass

    def get_feed(self):
        pass

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass

    def get_available_feeds(self):
        pass

    def set_radius(self):
        pass

    def get_master_id(self):
        pass

    def get_all_feeds(self):
        pass

    def get_owned_feeds(self):
        pass

    def block(self):
        pass

    def unblock(self):
        pass

    def get_content(self, seq_num):
        pass

    def get_current_seq_num(self):
        pass

    def get_last_event(self):
        pass