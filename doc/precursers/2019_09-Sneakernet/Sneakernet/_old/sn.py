#!/usr/bin/env python3

# sn/sn.py

import binascii
import json
import logging
import os

import lib.gg    as event
import lib.pcap   as log
import lib.crypto as crypto

# ----------------------------------------------------------------------

if __name__ == '__main__':

    # create feed ID
    keypair = crypto.ED25519()
    keypair.create()

    # create and sign two events
    e1 = event.EVENT(prev=None,
                     feed=keypair.public,
                     seq=1,
                     time=1564444800,
                     content = b'{\n  "name": "foo.box"\n}\n',
                     content_enc = event.GG_CONTENT_ENCODING_JSON)
    e1.signature = keypair.sign(e1.event_to_cbor())

    e2 = event.EVENT(prev=e1.get_sha256(),
                     feed=keypair.public,
                     seq=2,
                     time=1564444801,
                     content = b'{\n  "name": "foobar.box"\n}\n',
                     content_enc = event.GG_CONTENT_ENCODING_JSON)
    e2.signature = keypair.sign(e2.event_to_cbor())

    # --------------------------------------------------
    # write two events into a log
    
    lg = log.PCAP()
    lg.open('test.pcap', 'w')

    for e in [e1, e2]:
        t = event.TRANSFER(e)
        lg.write(t.to_cbor())
    lg.close()

    # --------------------------------------------------
    # read all events from the log, pretty-print them

    lg.open('test.pcap', 'r')
    n = 0
    while True:
        # print(f"offs={lg.offset}")
        block = lg.read()
        if block == None:
            break
        # print(f"pcap block {n}:\n", block, '\n')
        t = event.TRANSFER()
        t.from_cbor(block)
        print(t.event.pretty_print() + '\n')
        n += 1
    lg.close()

# eof
