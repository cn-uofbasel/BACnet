#!/usr/bin/env python3

# Sneakernet/import-from.py

"""
  given: dir

  check if dir exists
  new_db = {}
  new_cnt = 0
  for each file in dir:
    for each block:
      feed,seq,transfer <- block
      new_db[feed] = {} if not already existing
      if not seq in new_db[feed]:
        new_db[feed][seq].append(transfer)
        new_cnt += 1

  have_db = {}
  have_max = {}
  for each file in dir:
    for each block:
      feed,seq,transfer <- block
      have_db[feed] = {} if not already existing
      have_db[feed]['file'] = dir+file
      # have_db[feed][seq] = transfer
      update have_max[[feed] <seq:hash>

  for feed in new_db:
    if not feed in have_db:
      create_pcap(feed)

  update_cnt = 0
  for feed in have_db:
     open pcap have_db[feed]['file'] in append mode
     while have_max[feed]+1 in new_db[feed]:
       check for prev, if OK:
         append to pcap
         have_max[feed] += 1
         update_cnt += 1
     close pcap
"""

import base64
import json
import os
import sys
import time

import lib.crypto as crypto
import lib.gg     as gg
import lib.pcap   as log

LOGS_DIR = 'logs'
MY_LOG_FILE = '1.pcap' # inside logs dir

# ----------------------------------------------------------------------
if __name__ == '__main__':

    # one optional parameter: -new_name
    import_dir = sys.argv[1]
    
    print("Welcome to SneakerNet\n")
    print(f"** importing new events from '{import_dir}'")
    print()

    if not os.path.isdir(import_dir):
        print(f"** directory not found, aborting")
        sys.exit()

    new_db = {}
    new_cnt = 0
    lg = log.PCAP()
    t = gg.TRANSFER()
    for fn in os.listdir(import_dir):
        fn = os.path.join(import_dir, fn)
        lg.open(fn, 'r')
        for block in lg:
            t.from_cbor(block)
            feed = t.event.feed
            seq = t.event.seq
            if not feed in new_db:
                new_db[feed] = {}
            if not seq in new_db[feed]:
                new_db[feed][seq] = []
            new_db[feed][seq].append(block)
            new_cnt += 1
        lg.close()
    print(f"** found {new_cnt} event(s) in '{import_dir}'")

    have_fn = {}
    have_max = {}
    have_cnt = 0
    max_fn_number = 1
    for fn in os.listdir(LOGS_DIR):
        # remember highest file number, if we have to create a new file
        i = int(fn.split('.')[0])
        if max_fn_number < i:
            max_fn_number = i

        lg.open(os.path.join(LOGS_DIR, fn), 'r')
        for block in lg:
            have_cnt += 1
            t.from_cbor(block)
            feed = t.event.feed
            if not feed in have_fn:
                have_fn[feed] = fn
            seq = t.event.seq
            if not feed in have_max:
                have_max[feed] = -1
            if seq > have_max[feed]:
                have_max[feed] = seq
        lg.close()
    print(f"** found {have_cnt} event(s) in '{LOGS_DIR}'")

    update_cnt = 0
    for feed in new_db:
        if not feed in have_fn:
            max_fn_number += 1
            have_fn[feed] = os.path.join(LOGS_DIR, str(max_fn_number)+'.pcap')
            have_max[feed] = 0
            if update_cnt == 0:
                print()
            print(f"** creating {have_fn[feed]} for {base64.b64encode(feed).decode('utf8')}")
            lg.open(have_fn[feed], 'w')
            lg.close()
            max_fn_number += 1
            update_cnt += 1

    update_cnt = 0
    for feed in have_fn:
        if not feed in new_db:
            continue
        lg.open(have_fn[feed], 'a')
        # print(f"** testing {have_fn[feed]}, seq={have_max[feed]}")
        while have_max[feed]+1 in new_db[feed]:
            have_max[feed] += 1
            if update_cnt == 0:
                print()
            print(f"** import {base64.b64encode(feed).decode('utf8')}/{have_max[feed]}")
            lg.write(new_db[feed][have_max[feed]][0])
            update_cnt += 1
        lg.close()

    print()
    print(f"** imported {update_cnt} event(s) to the '{LOGS_DIR}' directory")

# eof
