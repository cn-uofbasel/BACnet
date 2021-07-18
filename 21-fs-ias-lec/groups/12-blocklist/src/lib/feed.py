#!/usr/bin/env python3

# lib/feed.py
# Jan-Mar 2020 <christian.tschudin@unibas.ch>

import cbor2
import os

import event
import pcap


class FEED:

    def __init__(self, fname, fid=None, signer=None,
                 create_if_notexisting=False,
                 digestmod = 'sha256'):
        self.fname = fname
        self.fid = fid
        self.signer = signer
        self.cine = create_if_notexisting
        self.digestmod = digestmod

        self.seq = 0
        self.pcap = pcap.PCAP(fname)
        self.hprev = None
        try:
            self.pcap.open('r')
            # find highest seq number:
            w = self.pcap.read_backwards(True)
            e = event.EVENT(digestmod=self.digestmod)
            e.from_wire(w)
            if fid != None and e.fid != fid:
                print("feed ID mismatch:", e.fid, "instead of", fid)
                self.pcap.close()
                self.pcap = None
                return
            self.fid, self.seq = e.fid, e.seq
            self.hprev = e.get_ref()
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
                        hprev=self.hprev, content=c,
                        digestmod=self.digestmod)
        metabits = e.mk_metabits(self.signer.get_sinfo())
        signature = self.signer.sign(metabits)
        w = e.to_wire(signature)
        self._append(w)
        self.hprev = e.get_ref()
        return w

    def is_valid_extension(self, e):
        if e.fid != self.fid or e.seq != self.seq+1:
            print(f"   out-of-seq (expected: {self.seq+1}, actual: {e.seq})")
            return False
        r = False
        if e.sinfo == crypto.SIGNINFO_ED25519:
            r = crypto.ED25519.verify(e.fid, e.metabits, e.signature)
        elif isinstance(self.signer, crypto.HMAC):
            if e.sinfo != self.signer.sinfo:
                print("   signature type mismatch")
            else:
                r = crypto.HMAC.verify(crypto.sinfo2mod[e.sinfo],
                                       self.signer.get_private_key(),
                                       e.metabits, e.signature)
        if not r:
            print("   invalid signature")
            return False
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
            self.hprev = e.get_ref()
            return True
        except Exception as x:
            print(x)
            pass
        print("   invalid packet")
        return False

    def __len__(self):
        return self.seq

    def __iter__(self):
        return FEED_ITER(self.fname, self.digestmod)

class FEED_ITER:
    def __init__(self, fn, digestmod='sha256'):
        self.pcap = pcap.PCAP(fn)
        self.pcap.open('r')
        self.digestmod = digestmod

    def __next__(self):
        pkt = self.pcap.read()
        if not pkt:
            self.pcap.close()
            raise StopIteration
        e = event.EVENT(digestmod=self.digestmod)
        e.from_wire(pkt)
        return e

# ----------------------------------------------------------------------

if __name__ == '__main__':

    import argparse
    import os
    import sys

    import crypto

    def load_keyfile(fn):
        with open(fn, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'ed25519':
            fid = bytes.fromhex(key['public'])
            signer = crypto.ED25519(bytes.fromhex(key['private']))
            digestmod = 'sha256'
        elif key['type'] in ['hmac_sha256', 'hmac_sha1', 'hmac_md5']:
            fid = bytes.fromhex(key['feed_id'])
            digestmod = key['type'][5:]
            signer = crypto.HMAC(digestmod, bytes.fromhex(key['private']))
        return fid, signer, digestmod

    parser = argparse.ArgumentParser(description='BACnet feed tool')
    parser.add_argument('--keyfile')
    parser.add_argument('pcapfile', metavar='PCAPFILE')
    parser.add_argument('CMD', choices=['create','dump','append','check'])
    
    args = parser.parse_args()

    if args.CMD == 'dump':
        pcap.dump(args.pcapfile)

    elif args.CMD in ['create','append']:
        if args.keyfile == None:
            print("missing keyfile parameter")
            sys.exit()
        fid, signer, digestmod = load_keyfile(args.keyfile)

        if args.CMD == 'create':
            try:
                os.remove(args.pcapfile)
            except:
                pass
            feed = FEED(args.pcapfile, fid, signer, True, digestmod=digestmod)
        else:
            feed = FEED(args.pcapfile, fid, signer, digestmod=digestmod)
        print("# enter payload of first event as a Python data structure, end with CTRL-D:")
        content = sys.stdin.read()
        feed.write(eval(content))

    elif args.CMD == 'check':
        if args.keyfile != None:
            fid, signer, digestmod = load_keyfile(args.keyfile)
        else:
            fid, signer, digestmod = None, None, None

        f = FEED(args.pcapfile, fid=fid, signer=signer, digestmod=digestmod)
        if f.pcap == None:
            sys.exit()
        f.seq = 0
        f.hprev = None
        print(f"Checking feed {f.fid.hex()}")
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq+1}: chaining or signature problem")
            else:
                print(f"-> event {e.seq}: ok, content={e.content().__repr__()}")
            f.seq += 1
            f.hprev = e.get_ref()

# eof
