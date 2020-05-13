#

# sn/lib/local_db.py

import base64
import os

import lib.gg   as gg
import lib.pcap as pcap

class LOCAL_DB:

    def __init__(self):
        self.dirname = None
        self.db = {} # feed : seq : transfer
        self.fn = {} # feed : fname
        self.max = {} # feed : maxs
        self.cnt = 0
        self.max_fn_number = 1

    def load(self, dirname):
        if not os.path.isdir(dirname):
            return 0
        self.dirname = dirname

        lg = pcap.PCAP()
        t = gg.TRANSFER()
        for fn in os.listdir(dirname):
            # remember highest file number, if we have to create a new file
            i = int(fn.split('.')[0])
            if self.max_fn_number < i:
                self.max_fn_number = i

            fn = os.path.join(dirname, fn)
            lg.open(fn, 'r')
            for block in lg:
                self.cnt += 1
                t.from_cbor(block)
                feed = t.event.feed
                if not feed in self.fn:
                    self.fn[feed] = fn
                    self.max[feed] = -1
                    self.db[feed] = {}
                seq = t.event.seq
                if seq > self.max[feed]:
                    self.max[feed] = seq
                self.db[feed][seq] = block
            lg.close()
        return self.cnt

    def ingest(self, data):
        t = gg.TRANSFER()
        t.from_cbor(data)
        feed = t.event.feed
        seq = t.event.seq
        lg = pcap.PCAP()
        if not feed in self.db:
            self.max_fn_number += 1
            self.fn[feed] = os.path.join(self.dirname,
                                         str(self.max_fn_number) + '.pcap')
            lg.open(self.fn[feed], 'w')
            lg.close()
            self.db[feed] = {}
            self.max[feed] = 0
        # print(f"-- ingesting {seq} into {self.fn[feed]}")
        if seq != self.max[feed]+1: # TODO: should also check prev field
            print("-- mismatch:", seq, self.max[feed]+1, ", ignored")
            return
        self.db[feed][seq] = data
        self.max[feed] += 1
        lg.open(self.fn[feed], 'a')
        lg.write(data)
        lg.close()
        print(f"-- ingested event {base64.b64encode(feed).decode('utf8')}:{seq}")

# eof
