#!/usr/bin/env python3

# lib/feed.py
# Jan 2020 <christian.tschudin@unibas.ch>

''' event data structure (="log entry")

  +-event------------------------------------------------------------------+
  | +-meta---------------------------------------+                         |
  | | feed_id, seq_no, h_prev, sign_info, h_cont |, signature, opt_content |
  | +--------------------------------------------+                         |
  +------------------------------------------------------------------------+

  event :== cbor( [ meta, signature, opt_content ] )

  meta  :== cbor( [ feed_id, seq_no, h_prev, sign_info, h_cont ] )

  h_prev         :== [hash_info, "hash value of prev event's meta field"]
  signature      :== "signature of meta"
  h_cont         :== [hash_info, "hash value of opt_content"]

  sign_info:     enum (0=ed25519)
  hash_info:     enum (0=sha256)

  opt_content    :== cbor( data )  # must be bytes so we can compute a hash)



# how to start Wireshark with BACnet event parsing:

wireshark -X lua_script:bacnet.lua PCAPFILE
  
'''

import hashlib
import cbor2

import crypto

# hash info
HASHINFO_SHA256      = 0
HASHINFO_SHA512      = 1
HASHINFO_MD5         = 2
HASHINFO_SHA1        = 3


# ---------------------------------------------------------------------------

def serialize(ds):
    return cbor2.dumps(ds)

def deserialize(s):
    return cbor2.loads(s)

# ---------------------------------------------------------------------------

class EVENT:

    def __init__(self, fid=None, seq=1, hprev=None, content=None,
                 digestmod='sha256'):
        self.wire, self.metabits, self.sinfo  = None, None, -1
        self.fid, self.seq, self.hprev        = fid, seq, hprev
        self.contbits = serialize(content)
        self.set_digestmod(digestmod)

    def set_digestmod(self, digestmod):
        self.digestmod = digestmod
        self.get_hash = lambda buf: getattr(hashlib,digestmod)(buf).digest()
        self.hinfo = {
            'md5'    : HASHINFO_MD5,
            'sha1'   : HASHINFO_SHA1,
            'sha256' : HASHINFO_SHA256,
            'sha512' : HASHINFO_SHA512
        }[digestmod]
        
    def from_wire(self, w):
        self.wire = w
        e = deserialize(w)
        self.metabits, self.signature = e[:2]
        self.contbits = None if len(e) < 2 else e[2]
        self.fid, self.seq, self.hprev, self.sinfo, self.hcont = \
                                                  deserialize(self.metabits)[:5]
        hval = self.hprev[1] if self.hprev != None else self.hcont[1]
        dm = 'sha256'
        if len(hval) == 16:
            dm = 'md5'
        elif  len(hval) == 20:
            dm = 'sha1'
        self.set_digestmod(dm)

    def get_ref(self):
        return [self.hinfo, self.get_hash(self.metabits)]

    def mk_metabits(self, sign_info):
        self.sinfo = sign_info
        meta = [self.fid, self.seq, self.hprev, self.sinfo,
                [self.hinfo, self.get_hash(self.contbits)]]
        self.metabits = serialize(meta)
        return self.metabits

    def to_wire(self, signature):
        # must be called after having called mk_metabits()
        if self.wire != None:
            return self.wire
        self.signature = signature
        self.wire = serialize([ self.metabits, signature, self.contbits ])
        return self.wire

    def chk_content(self):
        return self.hcont == self.get_hash(self.contbits)

    def content(self):
        return None if self.contbits == None \
                    else deserialize(self.contbits)

    def __str__(self):
        e = deserialize(self.wire)
        e[0] = deserialize(e[0])
        e[2] = deserialize(e[2])
        return "e - " + str(e)

    pass

# ----------------------------------------------------------------------
        
# eof
