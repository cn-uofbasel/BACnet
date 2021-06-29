import cbor2


class Event:

    def __init__(self, meta, signature, content):
        """
        Create Event from scratch.
        NOTE!!!: meta and content parameters must be Meta() and Content() objects! (see below)
        """
        self.meta = meta
        self.signature = signature
        self.content = content

    @classmethod
    def from_cbor(cls, event):
        """Read in an Event from cbor format (parameter is bytes()), creates a new Event object"""

        meta, signature, content = cbor2.loads(event)
        meta = Meta.from_cbor(meta)
        content = Content.from_cbor(content)
        return Event(meta, signature, content)

    def get_as_cbor(self):
        """Return an event cbor encoded as bytes() python object"""

        return cbor2.dumps([self.meta.get_as_cbor(), self.signature, self.content.get_as_cbor()])


class Meta:

    def __init__(self, feed_id, seq_no, hash_of_prev, signature_info, content_hash):
        """Create the Meta() object from scratch (for example if you create a new event)"""

        self.feed_id = feed_id
        self.seq_no = seq_no
        self.hash_of_prev = hash_of_prev
        self.signature_info = signature_info
        self.hash_of_content = content_hash

    @classmethod
    def from_cbor(cls, cbor):
        """Read in a Meta() object from cbor format"""

        feed_id, seq_no, hash_of_prev, signature_info, hash_of_content = cbor2.loads(cbor)
        return Meta(feed_id, seq_no, hash_of_prev, signature_info, hash_of_content)

    def get_as_cbor(self):
        """Get the cbor encoded version of the meta object"""

        return cbor2.dumps([self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content])


class Content:

    def __init__(self, identifier, parameters):
        """Create content from scratch from identifier and parameter dictionary as specified in BACnet documentation"""

        self.content = [identifier, parameters]

    @classmethod
    def from_cbor(cls, cbor):
        """Read in a Content() object from cbor format"""

        identifier, parameters = cbor2.loads(cbor)
        return Content(identifier, parameters)

    def get_as_cbor(self):
        """Get the Content cbor encoded (as bytes() python object)"""

        return cbor2.dumps(self.content)
