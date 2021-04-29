import sys

# add the lib to the module folder
sys.path.append("./lib")

import os
import crypto
import feed
import time


class Feed:

    def __init__(self, name):
        self.name = name
        self.myFeed = None

    # generates a new Feed
    def generate(self):
        if not os.path.isdir("data"):
            os.mkdir("data")

        if not os.path.isdir("data/" + self.name):
            os.mkdir("data/" + self.name)

        # Generate a key pair

        # generate a feed
        digestmod = "sha256"
        h, signer = None, None

        # Generate a Key if non exists
        if not os.path.isfile("data/" + self.name + "/" + self.name + "-secret.key"):
            print("Create " + self.name + "'s key pair at data/" + self.name + "/" + self.name + "-secret.key")
            h = crypto.HMAC(digestmod)
            h.create()
            with open("data/" + self.name + "/" + self.name + "-secret.key", "w") as f:
                f.write('{\n  ' + (',\n '.join(h.as_string().split(','))[1:-1]) + '\n}')
                signer = crypto.HMAC(digestmod, h.get_private_key())

        print("Read " + self.name + "'s secret key.")
        with open("data/" + self.name + "/" + self.name + "-secret.key", 'r') as f:
            key = eval(f.read())
            h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
            signer = crypto.HMAC(digestmod, bytes.fromhex(h.get_private_key()))

        print("Create or load " + self.name + "'s feed at data/" + self.name + "/" + self.name + "-feed.pcap")
        self.myFeed = feed.FEED(fname="data/" + self.name + "/" + self.name + "-feed.pcap", fid=h.get_feed_id(),
                                signer=signer, create_if_notexisting=True, digestmod=digestmod)

    # adds new Follow to the Feed
    def writeFollowToFeed(self, newFriend):
        self.myFeed.write(["bacnet/following", time.time(), newFriend])

    # reads the followList from the Feed
    def readFollowFromFeed(self):
        followList = []
        for event in self.myFeed:
            if event.content()[0] == "bacnet/following":
                followList.append({"Root": self.name, "time": event.content()[1], "Friend": event.content()[2]})

        followList.sort(key=lambda msg: msg["time"])

        for msg in followList:
            print(msg["Root"] + " follows " + msg["Friend"])
