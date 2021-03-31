import impexp
import lib.pcap as pcap
try:
    print("eigene DB")
    pcap.dump("test.pcap")
except Exception as e: 
    print(e)
try:
    print("eigener Payload")
    pcap.dump("payload.pcap")
except Exception as e: 
    print(e)
try:
    print("peer Payload")
    pcap.dump("peerPayload.pcap")
except Exception as e: 
    print(e)