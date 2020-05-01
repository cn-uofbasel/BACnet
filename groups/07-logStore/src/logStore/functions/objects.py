import cbor2

if __name__ == "__main__":
    pass


class Meta:

    def __init__(self, meta):
        self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content = cbor2.loads(meta)

    def get_as_cbor(self):
        return cbor2.dumps([self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content])


class Content:

    def __init__(self, content):
        self.content = cbor2.loads(content)

    def get_as_cbor(self):
        return cbor2.dumps(self.content)


class Event:

    # parameter event: cbor encoded feed event
    def __init__(self, event):
        meta, self.signature, content = cbor2.loads(event)
        self.meta = Meta(meta)
        self.content = Content(content)

    def get_as_cbor(self):
        return cbor2.dumps([self.meta, self.signature, self.content])
