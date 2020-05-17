#!/usr/bin/python 
import cbor2
import hashlib
import impexp 
import lib.pcap as pcap

impexp.createPayload('test.pcap','logtextfile2.txt','logtextfile.txt')
impexp.handlePayload('test2.pcap','payload.pcap','logtextfile2.txt')

