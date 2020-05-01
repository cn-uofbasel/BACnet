import cbor2
import hashlib


class Meta:

    def __init__(self, meta):
        self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content = cbor2.loads(meta)

    def __init__(self, feed_id, seq_no, hash_of_prev, signature_info, hash_of_content):
        self.feed_id = feed_id
        self.seq_no = seq_no
        self.hash_of_prev = hash_of_prev
        self.signature_info = signature_info
        self.hash_of_content = hash_of_content

    def get_as_cbor(self):
        return cbor2.dumps([self.feed_id, self.seq_no, self.hash_of_prev, self.signature_info, self.hash_of_content])


class Content:

    def __init__(self, content):
        self.content = cbor2.loads(content)

    def __init__(self, identifier, parameter):
        self.content = [identifier, parameter]

    def get_as_cbor(self):
        return cbor2.dumps(self.content)


class Event:

    # parameter event: cbor encoded feed event
    def __init__(self, event):
        meta, self.signature, content = cbor2.loads(event)
        self.meta = Meta(meta)
        self.content = Content(content)

    def __init__(self, meta, signature, content):
        self.meta = meta
        self.signature = signature
        self.content = content

    def get_as_cbor(self):
        return cbor2.dumps([self.meta.get_as_cbor(), self.signature, self.content.get_as_cbor()])


if __name__ == "__main__":
    content = Content('whateverapp/whateveraction', {'somekey': 'somevalue', 'someotherkey': 753465734265})
    hoc = hashlib.sha256(content.get_as_cbor()).hexdigest()
    signature = '832649741acddcf4382975ccd89d98af987ab9b90e908fff9ae89bac8bacbac1'
    meta = Meta('7326acd76a876adc89e78897d8778f78787c879234322acd789d12caffff5da2', 0, None, 'sha256', hoc)
    event = Event(meta, signature, content)
    file = open('dummyfeedentry.cbor', 'wb')
    file.write(event.get_as_cbor())
    file.close()
