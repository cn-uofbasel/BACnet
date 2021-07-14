from ..storage_controller import StorageController


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


class Feed:

    def __init__(self, feed_id, feed_meta: FeedMeta, storage_controller: StorageController):
        self.feed_id = feed_id
        self.feed_meta = feed_meta
        self.strg_ctrl = storage_controller

    def get_content(self, seq_num):
        return self.strg_ctrl.get_content(self.feed_id, seq_num)

    def get_current_seq_num(self):
        return self.strg_ctrl.get_current_seq_num(self.feed_id)

    def get_last_event(self, feed_id):
        return self.get_content(self.get_current_seq_num())

    def get_feed_id(self):
        return self.feed_id
