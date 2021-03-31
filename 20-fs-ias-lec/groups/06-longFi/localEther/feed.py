#!/usr/bin/env python3

# lib/feed.py
# Jan-Mar 2020 <christian.tschudin@unibas.ch>

import event
import pcap
import os
import crypto


class FEED:

    def __init__(self, fname, fid=None, signer=None,
                 create_if_notexisting=False):
        self.fname = fname
        self.fid = fid
        self.signer = signer
        self.cine = create_if_notexisting

        self.seq = 0
        self.pcap = pcap.PCAP(fname)
        self.hprev = None
        try:
            self.pcap.open('r')
            # find highest seq number:
            w = self.pcap.read_backwards(True)
            e = event.EVENT()
            e.from_wire(w)
            if fid != None and e.fid != fid:
                print("feed ID mismatch:", e.fid, "instead of", fid)
                self.pcap.close()
                self.pcap = None
                return
            self.fid, self.seq = e.fid, e.seq
            self.hprev = event.get_hash(e.metabits)
            self.pcap.close()
        except Exception as e:
            if not self.cine:
                self.pcap = None
                print(f"error opening file {fname}")
            else:
                self.pcap.open('w')
                self.pcap.close()

    def _append(self, w): # blindly append the bytes in w to a log file
        p = self.pcap
        p.open('a')
        p.write(w)
        p.close()
        try:
            os.sync()
        except:
            pass
        self.seq += 1

    def write(self, c): # create new log extension with given content
        if self.seq == 0:
            self.hprev = None
        e = event.EVENT(fid=self.fid, seq=self.seq+1,
                        hprev=self.hprev, content=c)
        metabits = e.get_metabits(self.signer.get_sinfo())
        signature = self.signer.sign(metabits)
        w = e.to_wire(signature)
        self._append(w)
        self.hprev = event.get_hash(metabits)
        return w

    # Needs an event as input. Important to use the from_wire function if one have to check bytes
    def is_valid_extension(self, e):
        # Checks first if the feed IDs (public key) are the same and check the sequence number order
        if e.fid != self.fid or e.seq != self.seq+1:
            print(f"   out-of-seq (expected: {self.seq+1}, actual: {e.seq})")
            return False

        # Checks if instance of ED25519
        if isinstance(self.signer, crypto.ED25519):
            if e.sinfo != crypto.SIGNINFO_ED25519:
                print("   signature type mismatch")
                r = False
            else:
                r = crypto.ED25519.verify(e.fid, e.metabits, e.signature)

        # Checks if instance of HMAC
        elif isinstance(self.signer, crypto.HMAC256):
            if e.sinfo != crypto.SIGNINFO_HMAC_SHA256:
                print("   signature type mismatch")
                r = False
            else:
                r = crypto.HMAC256.verify(self.signer.get_private_key(),
                                          e.metabits, e.signature)
        else:
            r = False

        if not r:
            print("   invalid signature")
            return False

        # Check the hash chaining (hash pointer to previous hash pointers)
        if self.hprev != e.hprev:
            print(f"   invalid hash chaining: expected={self.hprev}, actual={e.hprev}")
            return False
        return True

    def ingest(self, e): # append event to log only if a valid extension
        # return False if failing
        try:
            if not self.is_valid_extension(e):
                print("   invalid extension")
                return False
            self._append(e.to_wire())
            self.hprev = event.get_hash(e.metabits)
            return True
        except Exception as x:
            print(x)
            pass
        print("   invalid packet")
        return False

    def __len__(self):
        return self.seq

    def __iter__(self):
        return FEED_ITER(self.fname)

class FEED_ITER:
    def __init__(self, fn):
        self.pcap = pcap.PCAP(fn)
        self.pcap.open('r')

    def __next__(self):
        pkt = self.pcap.read()
        if not pkt:
            self.pcap.close()
            raise StopIteration
        e = event.EVENT()
        e.from_wire(pkt)
        return e

# eof
