from blocklist import Blocklist
from blocksettings import Blocksettings
### for testing ###
import lib.crypto as crypto
import lib.feed as feed
import os
import time
import shutil
import cbor2


def testEventFilter():
    if not os.path.isdir("testdata"):
        os.mkdir("testdata")
        os.mkdir("testdata/alice")

    # Generate a key pair

    alice_digestmod = "sha256"
    alcie_h, alice_signer = None, None

    if not os.path.isfile("testdata/alice/alice-secret.key"):
        # print("Create Alice's key pair at data/alice/alice-secret.key")
        alice_h = crypto.HMAC(alice_digestmod)
        alice_h.create()
        with open("testdata/alice/alice-secret.key", "w") as f:
            f.write('{\n  ' + (',\n '.join(alice_h.as_string().split(','))[1:-1]) + '\n}')
            alice_signer = crypto.HMAC(alice_digestmod, alice_h.get_private_key())

    # print("Read Alice's secret key.")
    with open("testdata/alice/alice-secret.key", 'r') as f:
        # print("Create Bob's key pair at data/bob/bob-secret.key")
        key = eval(f.read())
        alice_h = crypto.HMAC(alice_digestmod, key["private"], key["feed_id"])
        alice_signer = crypto.HMAC(alice_digestmod, bytes.fromhex(alice_h.get_private_key()))

    # print("Create or load Alice's feed at data/alice/alice-feed.pcap")
    alice_feed = feed.FEED(fname="testdata/alice/alice-feed.pcap", fid=alice_h.get_feed_id(), signer=alice_signer,
                           create_if_notexisting=True, digestmod=alice_digestmod)

    # print("Alice and Bob write to their log.")
    alice_feed.write(["bacnet/chat", time.time(), "Where is the duck ?"])

    bl = Blocklist('myblocklist.json')
    print(bl.blocklist["words"])
    bs = Blocksettings('myblocklistsettings.json')
    print("Blocklevel: " + str(bs.blocklevel))
    chat = []

    for event in alice_feed:
        event = bl.filterEvent(bl, bs, event)
        if event.content()[0] == "bacnet/chat":
            chat.append({"sender": "alice", "time": event.content()[1], "text": event.content()[2]})

    chat.sort(key=lambda msg: msg["time"])

    for msg in chat:
        print(msg["sender"] + ":" + msg["text"])
    shutil.rmtree('testdata')


def testJson(blocklistpath):
    b = Blocklist(blocklistpath)
    print(b.getBlocklist())
    b.blockWord("test")
    print(b.getBlocklist())
    b.unblockWord("test")
    b.writeToFile("./myblocklist.json")
    print(b.getBlocklist())

    bs = Blocksettings.getStandartSettings()
    bs.valuesToJson()
    bs.writeToFile("./myblocklistsettings.json")


if __name__ == '__main__':
    print("------------Test Json------------")
    testJson("./myblocklist.json")
    print("------------Test Eventfilter------------")
    testEventFilter()
