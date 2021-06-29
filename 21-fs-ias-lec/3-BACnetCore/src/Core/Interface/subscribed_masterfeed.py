from feed import Feed, FeedMeta


class SubscribedMasterFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta, master_id):
        super().__init__(feed_id, feed_meta)
        self.master_id = master_id

    def get_owner_id(self):
        pass

    def receive(self):
        pass

    def get_content(self, seq_num):
        pass

    def get_current_seq_num(self):
        pass

    def get_last_event(self):
        pass
