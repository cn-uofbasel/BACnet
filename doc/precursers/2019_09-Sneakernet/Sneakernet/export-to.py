#!/usr/bin/env python3

# Sneakernet/export-to.py

"""
  given: dir

  check if export dir exists

  have_db = {}
  have_max = {}
  for each file in dir:
    for each block:
      feed,seq,transfer <- block
      have_db[feed] = {} if not already existing
      # have_db[feed]['file'] = dir+file
      have_db[feed][seq] = transfer
      update have_max[[feed] <seq:hash>

  target_db = {}
  target_cnt = 0
  for each file in dir:
    for each block:
      feed,seq,transfer <- block
      target_db[feed] = {} if not already existing
      if not seq in target_db[feed]:
        target_db[feed][seq].append(transfer)
        target_cnt += 1

  create dir/pcap file, open it
  update_cnt = 0
  for feed in have_db:
     if not feed in target_db:
        target_db[feed] = {}
     for i in range(have_max[feed]):
        if not i+1 in target_db[feed]:
          append_to_pcap(have_db[feed][i+1])
          update_cnt += 1
  close pcap
  if update_cnt == 0:
    unlink pcap

"""

import base64
import os
import random
import sys

import lib.gg     as gg
import lib.pcap   as log

def export():
    LOGS_DIR = 'logs'
    MY_LOG_FILE = '1.pcap' # inside logs dir

    # ----------------------------------------------------------------------
    if __name__ == '__main__':

        # one optional parameter: -new_name
        export_dir = sys.argv[1]

        print("Welcome to SneakerNet\n")
        print(f"** exporting new events to '{export_dir}'")
        print()

        if not os.path.isdir(export_dir):
            print(f"** directory not found, aborting")
            sys.exit()

        lg = log.PCAP()
        t = gg.TRANSFER()

        have_db = {}
        have_max = {}
        have_cnt = 0
        for fn in os.listdir(LOGS_DIR):
            lg.open(os.path.join(LOGS_DIR, fn), 'r')
            for block in lg:
                t.from_cbor(block)
                feed = t.event.feed
                seq = t.event.seq
                if not feed in have_db:
                    have_db[feed] = {}
                    have_max[feed] = 0
                have_db[feed][seq] = block
                if seq > have_max[feed]:
                    have_max[feed] = seq
                have_cnt += 1
            lg.close()
        print(f"** found {have_cnt} event(s) in directory '{LOGS_DIR}'")

        target_db = {}
        target_cnt = 0
        for fn in os.listdir(export_dir):
            fn = os.path.join(export_dir, fn)
            lg.open(fn, 'r')
            for block in lg:
                t.from_cbor(block)
                feed = t.event.feed
                seq = t.event.seq
                if not feed in target_db:
                    target_db[feed] = {}
                if not seq in target_db[feed]:
                    target_db[feed][seq] = []
                # target_db[feed][seq].append(block)
                target_cnt += 1
            lg.close()
        print(f"** found {target_cnt} event(s) in target directory '{export_dir}'")

        # create file with unique file name
        log_fn = None
        while True:
            log_fn = 'x' + str(random.randint(10000000, 19999999))[1:] + '.pcap'
            log_fn = os.path.join(export_dir, log_fn)
            if not os.path.isfile(log_fn):
                break

        lg.open(log_fn, 'w')
        update_cnt = 0
        for feed in have_db:
            for i in range(0, have_max[feed]):
                if not feed in target_db or not i+1 in target_db[feed]:
                    if update_cnt == 0:
                        print()
                    print(f"** exporting {base64.b64encode(feed).decode('utf8')}/{i+1}")
                    lg.write(have_db[feed][i+1])
                    update_cnt += 1
        lg.close()

        print()
        if update_cnt == 0:
            os.unlink(log_fn)
            print("** no events exported")
        else:
            print(f"** exported {update_cnt} event(s) to '{log_fn}'")

    # eof
