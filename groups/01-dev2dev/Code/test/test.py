#!/usr/bin/python 
import lib.pcap as pcap
import cbor2
import hashlib


inventory_file = open("inventory.txt")
inventory = inventory_file.read().splitlines()
log = pcap.PCAP('test.pcap')
log.open('r')
for w in log: 
    e = cbor2.loads(w)
    href = hashlib.sha256(e[0]).digest()
    e[0] = cbor2.loads(e[0])
    e[0] = pcap.base64ify(e[0])
    fid = e[0][0]
    seq = e[0][1]
    e[2] = cbor2.loads(e[2])
    print(fid)
    print(seq)
    print(e[2])

    print(e[0])
    print(href.hex())

