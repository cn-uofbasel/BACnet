import cbor2


class Event:
    """
    This class represents an Event. An Event is a part of a Feed, which itself is an append only log used to communicate
    and send data. It consists of three parts:
    meta: Metadata of an Event is essential for the BACNET to work, it lets the Nodes categorize and validate events
    signature: Each Event is signed by the owner of the feed, the event is part of (Ensure Authenticity)
    content: The data transferred with an event. Consists of an Identifier(String) as well as the data
    """

    def __init__(self, meta, signature, content):
        """
        Create Event from scratch.
        NOTE!!!: meta and content parameters must be Meta() and Content() objects! (see below)
        """
        self.meta = meta
        self.signature = signature
        self.content = content

    @classmethod
    def from_cbor(cls, event: bytes):
        """Read in an Event from cbor format (parameter is bytes()), creates a new Event object"""

        meta, signature, content = cbor2.loads(event)
        meta = Meta.from_cbor(meta)
        content = Content.from_cbor(content)
        return Event(meta, signature, content)

    def get_as_cbor(self):
        """Return an event cbor encoded as bytes() python object"""
        return cbor2.dumps([self.meta.get_as_cbor(), self.signature, self.content.get_as_cbor()])

    def __str__(self):
        """
        Method to represent the Event as a String.
        """
        return str(self.meta) + str(self.content)


class Meta:
    """
    This class represents the metadata of an Event in a feed, it bundles parameters that are essential for the
    functionality of BACNet:

    feed_id:    The ID of the feed the event belongs to(= a pubkey)
    seq_no:     The Sequence number of the event (counting up from 0)
    hash_of_prev: Hash value of the previous Event in this feed, ensures that feeds cant be modified (append only)
    signature_info: defines which type the signature of an event has (which crypto-Algorithm)
    hash_of_content: Contains the hash value of the content(ensures integrity)
    """

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

    def __str__(self):
        """
        Useful helper to represent the Metadata as a string
        """
        return f"********\nMeta:\n--feed_id: {self.feed_id}\n--seq_no: {self.seq_no}\n"


class Content:
    """
    This class represents the content and thus the main part of an event, It consists of two parts:
    identifier: Is a field that can and should be used to identify the Event later (On application level or in queries)
    data: Here you can store arbitrary data
    """

    def __init__(self, identifier, data):
        """Create content from scratch from identifier and parameter dictionary as specified in BACnet documentation"""
        self.identifier = identifier
        self.data = data

    @classmethod
    def from_cbor(cls, cbor):
        """Read in a Content() object from cbor format"""
        identifier, data = cbor2.loads(cbor)
        return Content(identifier, data)

    def get_as_cbor(self):
        """Get the Content cbor encoded (as bytes() python object)"""
        return cbor2.dumps([self.identifier, self.data])

    def __str__(self):
        """
        Utility Method to represent the Content as a String.
        """
        return f"\nContent:\n--identifier: {self.identifier}\n--data: {self.data}\n********"
