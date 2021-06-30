from ..event import Event
from abc import ABC, abstractmethod


class FeedMeta:

    def __init__(self, feed_name, public_key, signature_info):  # eventually flags(subscribed, owned, secret, blocked)
        self.feed_name = feed_name
        self.public_key = public_key
        self.signature_info = signature_info

    def get_feed_name(self):
        return self.feed_name

    def get_public_key(self):
        return self.public_key

    def get_signature_info(self):
        return self.signature_info


class Feed(ABC):

    def __init__(self, feed_id, feed_meta: FeedMeta):
        self.feed_id = feed_id
        self.feed_meta = feed_meta

    @abstractmethod
    def get_content(self, seq_num, feed_id):
        pass

    @abstractmethod
    def get_current_seq_num(self, feed_id):
        pass

    @abstractmethod
    def get_last_event(self, feed_id):
        pass

    def get_feed_id(self):
        return self.feed_id
