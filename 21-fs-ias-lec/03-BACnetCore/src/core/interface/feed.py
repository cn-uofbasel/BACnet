from .event import Event


class FeedMeta:
    """
    This class represents the Metadata for every feed.
    """
    def __init__(self, feed_name, public_key, signature_info):
        self.feed_name = feed_name
        self.public_key = public_key
        self.signature_info = signature_info

    def get_feed_name(self):
        return self.feed_name

    def get_public_key(self):
        return self.public_key

    def get_signature_info(self):
        return self.signature_info

    def __str__(self):
        return f"--feed-name: {self.feed_name}\n--feed_id: {self.public_key}\n--signature-info: {self.signature_info}"


class Feed:
    """
    This class is the base Interface class for every Feed.
    """
    def __init__(self, feed_id, storage_controller):
        self.feed_id = feed_id
        self.strg_ctrl = storage_controller
        # this is separated due to self.meta reference in get_feed_meta()
        self.meta = None
        self.meta = self.get_feed_meta()

    def get_event(self, seq_num: int) -> Event:
        """
        This method tries to get a certain event. UnknownFeedError or EventNotfoundError can raise.
        """
        return self.strg_ctrl.get_event(seq_num, self.feed_id)

    def get_current_seq_num(self):
        """
        This method tries to get the current sequence number of this feed. -1 is returned when feed not known or no
        event in database.
        """
        return self.strg_ctrl.get_current_seq_num(self.feed_id)

    def get_last_event(self):
        """
        This method tries to get the latest event of this feed. Since it uses get_content(), UnknownFeedError
        or EventNotfoundError can raise.
        """
        return self.get_event(self.get_current_seq_num())

    def get_feed_id(self):
        """
        Returns the feed_id of this feed
        """
        return self.feed_id

    def get_feed_meta(self):
        """
        Getter for the metadata of this feed. If the metadata is currently None(= not able to load it yet). Then try
        to load it again. Anyway return self.meta.
        """
        if self.meta is None:
            self._reload_meta()
        return self.meta

    def _reload_meta(self):
        """
        This method tries to extract the metadata of a feed from the last event of this feed. if this fails (ex when no
        events of this feed are in the database) then return None
        """
        try:
            first_event = self.get_event(0)
            name = self.strg_ctrl.get_name_by_feed_id(self.feed_id)
            self.meta = FeedMeta(name, first_event.meta.feed_id, first_event.meta.signature_info)
        except Exception:
            self.meta = None

    def __str__(self):
        return f"\n****Feed****\n{str(self.meta)}"
