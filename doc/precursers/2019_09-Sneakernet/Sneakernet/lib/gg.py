# sn/lib/gg.py
# GabbyGrove binary encoding

import cbor2
import hashlib
import lib.crypto as crypto

GG_TAG_CIPHERLINK = 1050
GG_CIPHERLINK_FEED_V1         = b'\x01' # ed25519
GG_CIPHERLINK_EVENT_V1        = b'\x02' # sha256
GG_CIPHERLINK_CONTENT_v1      = b'\x03' # sha256
GG_CIPHERLINK_FEED_SSB_V1     = b'\x04'
GG_CIPHERLINK_EVENT_SSB_V1    = b'\x05'
GG_CIPHERLINK_CONTENT_SSB_V1  = b'\x06'
GG_SIGNINGALGO_SHA256_ED25519 = 1
GG_CONTENT_ENCODING_OPAQUE    = 0
GG_CONTENT_ENCODING_JSON      = 1
GG_CONTENT_ENCODING_CBOR      = 2


def mk_cipherlink(t,val):
    if not val:
        return None
    return cbor2.CBORTag(GG_TAG_CIPHERLINK, t+val)


class EVENT:
    def __init__(self, prev=None, feed=None, seq=0, time=0,
                 content = None, content_enc = GG_CONTENT_ENCODING_OPAQUE,
                 signing_algo = GG_SIGNINGALGO_SHA256_ED25519):
        self.prev = prev
        self.feed = feed
        self.seq  = seq
        self.time = time
        self.content = content
        self.content_len = 0 if not content else len(content)
        self.content_hash = None
        self.content_enc = content_enc
        self.signing_algo = signing_algo
        #
        self.signed_bytes = None
        self.event_bytes = None
        self.signature = None
        self.cipherlink = None

    def from_cbor(self, c):
        # input must be CBOR of a signed event
        e = cbor2.loads(c)
        if type(e) != list and len(e) != 2:
            return False # raise()
        self.signed_bytes = c
        self.event_bytes = e[0]
        self.signature = e[1]
        self.cipherlink = None
        e = cbor2.loads(self.event_bytes)
        # we should do more sanity checks ...
        self.prev = None if not e[0] else e[0].value[1:]
        self.feed = None if not e[1] else e[1].value[1:]
        self.seq = e[2]
        self.time = e[3]
        self.content = None
        self.content_len = e[4][1]
        self.content_enc = e[4][0]
        self.content_hash = e[4][2].value[1:]
        self.signing_algo = e[5]
        return True

    def event_to_cbor(self):
        if self.content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.content).digest()
        self.event_bytes = cbor2.dumps([
            mk_cipherlink(GG_CIPHERLINK_EVENT_V1, self.prev),
            mk_cipherlink(GG_CIPHERLINK_FEED_V1, self.feed),
            self.seq,
            self.time,
            [self.content_enc, len(self.content) if self.content else 0,
             mk_cipherlink(GG_CIPHERLINK_EVENT_V1, self.content_hash)],
            GG_SIGNINGALGO_SHA256_ED25519
        ])
        return self.event_bytes

    def signed_event_to_cbor(self):
        # this assumes that self.event_bytes was already generated and
        # that self.signature received its respective value
        self.signed_bytes = cbor2.dumps([ self.event_bytes, self.signature ])
        return self.signed_bytes

    def get_sha256(self):
        if not self.signed_bytes:
            self.signed_event_to_cbor()
        return hashlib.sha256(self.signed_bytes).digest()

    def get_cipherlink(self):
        if not self.cipherlink:
            self.cipherlink = mk_cipherlink(GG_CIPHERLINK_EVENT_V1,
                                            self.get_sha256())
        return self.cipherlink

    def pretty_print(self):
        s = 'event {\n'
        for i in ['prev', 'feed', 'seq', 'time']:
            s += f'  {i}: {getattr(self, i)}\n'
        if self.content:
            s += f'  content: {len(self.content)} bytes ({self.content})' + '\n'
        else:
            s += '  content: None\n'
        s += f'  hash: {self.get_sha256()}' + '\n'
        return s + '}'


class TRANSFER:

    def __init__(self, event = None):
        self.event = event # class EVENT

    def to_cbor(self):
        if self.event.content:
            c = [ self.event.content, self.event.content_len,
                  self.event.content_enc ]
        else:
            c = None
        return cbor2.dumps([ self.event.signed_event_to_cbor(), c ])

    def from_cbor(self, c):
        t = cbor2.loads(c)
        if type(t) != list or len(t) != 2 or type(t[0]) != bytes:
            return False # raise()
        e = EVENT()
        if not e.from_cbor(t[0]) or (type(t[1]) != list and t[1] != None):
            return False # raise()
        if not crypto.ED25519.validate(e.feed, e.event_bytes, e.signature):
            # print("** WARNING: Failed to validate event.")
            # return False
            pass
        self.event = e
        if t[1] == None:
            self.event.content = None
        else:
            self.event.content = t[1][0]
            self.event.content_len = t[1][1]
            self.event.content_enc = t[1][2]
            self.event.content_hash = hashlib.sha256(t[1][0]).digest()
            # TODO: validate content hash and length
        return True

# eof
