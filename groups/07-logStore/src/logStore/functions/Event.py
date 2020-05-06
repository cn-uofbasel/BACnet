import cbor2
import hashlib


class Meta:

    def __init__(self, feed_id, seq_no, hash_of_prev, signature_info, hash_of_content):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.hash_of_prev = hash_of_prev
        self.signature_info = signature_info
        self.hash_of_content = hash_of_content

    @classmethod
    def from_cbor(cls, meta):
        feed_id, seq_no, hash_of_prev, signature_info, hash_of_content = cbor2.loads(meta)
        return Meta(feed_id, seq_no, hash_of_prev, signature_info, hash_of_content)

    def get_as_cbor(self):
        return cbor2.dumps([self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content])


class Content:

    def __init__(self, identifier, parameter):
        self.content = [identifier, parameter]

    @classmethod
    def from_cbor(cls, content):
        identifier, parameters = cbor2.loads(content)
        return Content(identifier, parameters)

    def get_as_cbor(self):
        return cbor2.dumps(self.content)


class Event:

    def __init__(self, meta, signature, content):
        self.meta = meta
        self.signature = signature
        self.content = content

    # parameter event: cbor encoded feed event
    @classmethod
    def from_cbor(self, event):
        meta, signature, content = cbor2.loads(event)
        meta = Meta.from_cbor(meta)
        content = Content.from_cbor(content)
        return Event(meta, signature, content)


    def get_as_cbor(self):
        return cbor2.dumps([self.meta.get_as_cbor(), self.signature, self.content.get_as_cbor()])


if __name__ == "__main__":
    pass
