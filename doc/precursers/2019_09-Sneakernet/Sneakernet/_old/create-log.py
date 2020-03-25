#!/usr/bin/env python3

# Sneakernet/create-log.py

"""
write the log
    #create identity                        | True
    #input loop (interruptable)             |
        #create event                       |
            #seq counter +1                 |
            #timestamp                      |
            #content                        |
            #feed (public_key)              |
            #previous (previous hash)
            #signature
        #save to pcap
    #finish
"""

import lib.crypto as crypto
import lib.gg     as gg
import lib.pcap   as log
import time

LOG_FILE_NAME = 'log.pcap'

# ----------------------------------------------------------------------

def create_event(content, seq, prev, public_key):
    return gg.EVENT(
        prev=prev,
        feed=public_key,
        seq=seq,
        time=int(time.time()),
        content=bytes("{\n  \"message\": \"%s\"\n}\n" % content, 'utf-8'),
        content_enc=gg.GG_CONTENT_ENCODING_JSON
    )


if __name__ == '__main__':

    print("Welcome to SneakerNet\n")

    keypair = crypto.ED25519()
    keypair.create()
    seq = 1
    prev = None
    lg = log.PCAP()

    lg.open(LOG_FILE_NAME, 'w')

    print(f"creating new log '{LOG_FILE_NAME}'")
    while True:
        content = input("\n** type in your message (or RETURN to leave): ")
        if content == "":
            end = input(">> do you really want to leave? (y/N) ")
            if end == "y":
                break
            continue
        event = create_event(content, seq, prev, keypair.public)
        event.signature = keypair.sign(event.event_to_cbor())
        t = gg.TRANSFER(event)
        lg.write(t.to_cbor())
        print('>> wrote', event.pretty_print())
        seq += 1
        prev = event.get_sha256()

    print('\n' + f"** wrote {seq-1} messages to {LOG_FILE_NAME}")

    lg.close()

# eof
