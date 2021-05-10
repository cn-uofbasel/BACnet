# Demo 2 - Dumb log sync demo

# This demo builds on the first demo,
# make sure to run 1-1-demo.py before you run this script.

# In demo 1 we assumed that Alice and Bob synchronized their logs.
# In this demo each user can only access his/her data folder.
# Therefore we have to implement the sync procedure.

# This demo introduces a dumb way how logs could be
# synchronized by copying and overwriting the users log on a USB stick.
#
# Assumptions:
#   1) Alice and Bob are following each others and want to sync their logs
#   2) The USB folder is a USB stick which they exchange.





import sys
# add the lib to the module folder
sys.path.append("./lib")


import os
import shutil
import crypto
import feed

## Dependencies:
# - [cbort2](https://pypi.org/project/cbor2/)
# Run pip3 install cbor2


if not os.path.isdir("data"):
    print("Data folder ./data not found! Did you run demo 1?")

if not os.path.isdir("data/usb-stick"):
    os.mkdir("data/usb-stick")


digestmod = "sha256"

alcie_h, alice_signer = None, None
bob_h, bob_signer = None, None

print("Read Alice's secret key.")
with open("data/alice/alice-secret.key", 'r') as f:
    print("Create Alice's key pair at data/alice/alice-secret.key")
    key = eval(f.read())
    alice_h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
    alice_signer = crypto.HMAC(digestmod, bytes.fromhex(alice_h.get_private_key()))

print("Load Alice's feed at data/alice/alice-feed.pcap")
alice_feed = feed.FEED(fname="data/alice/alice-feed.pcap", fid=alice_h.get_feed_id(), signer=alice_signer, create_if_notexisting=True, digestmod=digestmod)


print("Read Bob's secret key.")
with open("data/bob/bob-secret.key", 'r') as f:
    key = eval(f.read())
    bob_h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
    bob_signer = crypto.HMAC(digestmod, bytes.fromhex(bob_h.get_private_key()))


print("Create or load Boby's feed at data/bob/bob-feed.pcap")
bob_feed = feed.FEED(fname="data/bob/bob-feed.pcap", fid=bob_h.get_feed_id(), signer=bob_signer, create_if_notexisting=True, digestmod=digestmod)


import time

print("Alice writes a chat message to her feed.")
alice_feed.write(["bacnet/chat", time.time(), "Hey, it is me Alice! Do you get my messages over the USB stick?"])


print("Alice: She syncs her log.")
shutil.copy("data/alice/alice-feed.pcap", "data/usb-stick/alice-feed.pcap")

print("Alice: Unmounts the USB stick and hands it over to Bob.")

print("Bob: Mounts the USB stick...")
print("Bob: ... and syncs Alice's log to his his folder.")

shutil.copy("data/usb-stick/alice-feed.pcap", "data/bob/alice-feed.pcap")


def print_chat(alice_feed, bob_feed):

    print("\n Chat:\n")
    chat = []
    for event in alice_feed:
        if event.content()[0] == "bacnet/chat":
            chat.append({"sender": "alice", "time": event.content()[1], "text": event.content()[2]})

    for event in bob_feed:
        if event.content()[0] == "bacnet/chat":
            chat.append({"sender": "bob", "time": event.content()[1], "text": event.content()[2]})

    chat.sort(key=lambda msg: msg["time"])

    print("################# CHAT #################")
    for msg in chat:
        print(msg["sender"] + ":" + msg["text"])
    print("############### CHAT END ###############")


print("Bob: Read the chat.")

bob_feed = feed.FEED(fname="data/bob/bob-feed.pcap", fid=bob_h.get_feed_id(), signer=bob_signer, digestmod=digestmod)
alice_feed = feed.FEED(fname="data/bob/alice-feed.pcap", digestmod=digestmod)
# Note:
# We do not pass a signer to Alice's feed
# since Bob has no access to her private key
# and is only allowed to read her feed.

print_chat(alice_feed, bob_feed)

print("Bob: Writes a chat message to his feed.")
bob_feed.write(["bacnet/chat", time.time(), "Hey, it is me Bob!"])
bob_feed.write(["bacnet/chat", time.time(), "Yeah, I got your message :)."])
bob_feed.write(["bacnet/chat", time.time(), "How are you?"])


print("Bob: He syncs his log.")
shutil.copy("data/bob/bob-feed.pcap", "data/usb-stick/bob-feed.pcap")

print("Bob: Unmounts the USB stick and hands it over to Alice.")

print("Alice: Mounts the USB stick...")
print("Alice: ... and syncs Bob's log to her his folder.")

shutil.copy("data/usb-stick/bob-feed.pcap", "data/alice/bob-feed.pcap")

print("Alice: Reads the chat.")

alice_feed = feed.FEED(fname="data/bob/alice-feed.pcap", fid=alice_h.get_feed_id(),signer=alice_signer, digestmod=digestmod)
bob_feed = feed.FEED(fname="data/bob/bob-feed.pcap", digestmod=digestmod)

print_chat(alice_feed, bob_feed)


