from feed import Feed, FeedMeta


class SubscribedSubFeed(Feed):

    def __init__(self, feed_id, feed_meta: FeedMeta):
        super().__init__(feed_id, feed_meta)

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
