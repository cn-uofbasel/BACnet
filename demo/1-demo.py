# Demo 1

# This demo is a simple demo to introduce you how ...
#    to crete a user (-> generate a key pair + a feed/log)
#    to write data to the users log
#    to read data from multiple users
# with the basic bacnet libraries.


import sys
# add the lib to the module folder
sys.path.append("./lib") 


import os
import crypto 
import feed 



## Dependencies: 
# - [cbort2](https://pypi.org/project/cbor2/) 
# Run pip3 install cbor2

if not os.path.isdir("data"): 
    os.mkdir("data")
    os.mkdir("data/alice")
    os.mkdir("data/bob")

# Generate a key pair 

## Alice

alice_digestmod = "sha256"
alcie_h, alice_signer = None, None

if not os.path.isfile("data/alice/alice-secret.key"):
    print("Create Alice's key pair at data/alice/alice-secret.key") 
    alice_h = crypto.HMAC(alice_digestmod)
    alice_h.create()
    with open("data/alice/alice-secret.key", "w") as f: 
        f.write('{\n  '+(',\n '.join(alice_h.as_string().split(','))[1:-1])+'\n}')
        alice_signer = crypto.HMAC(alice_digestmod, alice_h.get_private_key())


print("Read Alice's secret key.") 
with open("data/alice/alice-secret.key", 'r') as f:
        print("Create Alice's key pair at data/alice/alice-secret.key")
        key = eval(f.read())
        alice_h = crypto.HMAC(alice_digestmod, key["private"], key["feed_id"])
        alice_signer = crypto.HMAC(alice_digestmod, bytes.fromhex(alice_h.get_private_key()))

print("Create or load Alice's feed at data/alice/alice-feed.pcap") 
alice_feed = feed.FEED(fname="data/alice/alice-feed.pcap", fid=alice_h.get_feed_id(), signer=alice_signer, create_if_notexisting=True, digestmod=alice_digestmod)

## Bob
bob_digestmod = "sha256"
bob_h, bob_signer = None, None

if not os.path.isfile("data/bob/bob-secret.key"):
    print("Create Bob's key pair at data/bob/bob-secret.key") 
    bob_h = crypto.HMAC(bob_digestmod)
    bob_h.create()
    with open("data/bob/bob-secret.key", "w") as f:
        f.write('{\n  '+(',\n '.join(bob_h.as_string().split(','))[1:-1])+'\n}')
        
print("Read Bob's secret key.") 
with open("data/bob/bob-secret.key", 'r') as f:
        key = eval(f.read())
        bob_h = crypto.HMAC(bob_digestmod, key["private"], key["feed_id"])
        bob_signer = crypto.HMAC(bob_digestmod, bytes.fromhex(bob_h.get_private_key()))


print("Create or load Boby's feed at data/bob/bob-feed.pcap") 
bob_feed = feed.FEED(fname="data/bob/bob-feed.pcap", fid=bob_h.get_feed_id(), signer=bob_signer, create_if_notexisting=True, digestmod=bob_digestmod)



import time

print("Alice and Bob write to their log.") 
alice_feed.write(["bacnet/chat", time.time(), "Hey, it is me Alice!"])
bob_feed.write(["bacnet/chat",  time.time(), "Hey, it is me Bob!"])


print("We now pretend that Alice and Bob already synced their logs and therefore have access of the others log.")

print("\n Chat:\n") 
chat = []
for event in alice_feed: 
    if event.content()[0] == "bacnet/chat":
        chat.append({"sender": "alice", "time": event.content()[1], "text": event.content()[2]})

for event in bob_feed: 
    if event.content()[0] == "bacnet/chat":
        chat.append({"sender": "bob", "time": event.content()[1], "text": event.content()[2]})

chat.sort(key=lambda msg: msg["time"])

for msg in chat: 
    print(msg["sender"] + ":" + msg["text"])
