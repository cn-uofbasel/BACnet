import sys
# add the lib to the module folder
sys.path.append("./lib")


import os
import generateFeed

## Dependencies:
# - [cbort2](https://pypi.org/project/cbor2/)
# Run pip3 install cbor2

if not os.path.isdir("data"):
    os.mkdir("data")
    os.mkdir("data/alice")
    os.mkdir("data/bob")


import time

print("Alice and Bob write to their log.")


generateFeed.myfeed.write(["bacnet/chat", time.time(), "Hey, it is me Alice!"])
generateFeed.bob_feed.write(["bacnet/chat",  time.time(), "Hey, it is me Bob!"])


print("We now pretend that Alice and Bob already synced their logs and therefore have access of the others log.")

print("\n Chat:\n")
chat = []
for event in generateFeed.myfeed:
    if event.content()[0] == "bacnet/chat":
        chat.append({"sender": "alice", "time": event.content()[1], "text": event.content()[2]})

for event in generateFeed.bob_feed:
    if event.content()[0] == "bacnet/chat":
        chat.append({"sender": "bob", "time": event.content()[1], "text": event.content()[2]})

chat.sort(key=lambda msg: msg["time"])

for msg in chat:
    print(msg["sender"] + ":" + msg["text"])