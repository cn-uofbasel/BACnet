import sys
import time
import os
# add the lib to the module folder
sys.path.append("lib")

import crypto
import feed
from blocklist import Blocklist
from blocksettings import Blocksettings


def demo():
    if not os.path.isdir("data"):
        os.mkdir("data")
        os.mkdir("data/alice")
        os.mkdir("data/bob")

    ## Alice
    alice_digestmod = "sha256"
    alcie_h, alice_signer = None, None

    # Create Alice's key pair at data/alice/alice-secret.key
    if not os.path.isfile("data/alice/alice-secret.key"):
        alice_h = crypto.HMAC(alice_digestmod)
        alice_h.create()
        with open("data/alice/alice-secret.key", "w") as f:
            f.write('{\n  ' + (',\n '.join(alice_h.as_string().split(','))[1:-1]) + '\n}')
            alice_signer = crypto.HMAC(alice_digestmod, alice_h.get_private_key())

    # Read Alice's secret key
    with open("data/alice/alice-secret.key", 'r') as f:
        key = eval(f.read())
        alice_h = crypto.HMAC(alice_digestmod, key["private"], key["feed_id"])
        alice_signer = crypto.HMAC(alice_digestmod, bytes.fromhex(alice_h.get_private_key()))

    # Create or load Alice's feed at data/alice/alice-feed.pcap
    alice_feed = feed.FEED(fname="data/alice/alice-feed.pcap", fid=alice_h.get_feed_id(), signer=alice_signer,
                           create_if_notexisting=True, digestmod=alice_digestmod)
    ## Bob
    bob_digestmod = "sha256"
    bob_h, bob_signer = None, None

    # Create Bob's key pair at data/bob/bob-secret.key
    if not os.path.isfile("data/bob/bob-secret.key"):
        bob_h = crypto.HMAC(bob_digestmod)
        bob_h.create()
        with open("data/bob/bob-secret.key", "w") as f:
            f.write('{\n  ' + (',\n '.join(bob_h.as_string().split(','))[1:-1]) + '\n}')

    # Read Bob's secret key
    with open("data/bob/bob-secret.key", 'r') as f:
        key = eval(f.read())
        bob_h = crypto.HMAC(bob_digestmod, key["private"], key["feed_id"])
        bob_signer = crypto.HMAC(bob_digestmod, bytes.fromhex(bob_h.get_private_key()))

    # Create or load Bob's feed at data/bob/bob-feed.pcap
    bob_feed = feed.FEED(fname="data/bob/bob-feed.pcap", fid=bob_h.get_feed_id(), signer=bob_signer,
                         create_if_notexisting=True, digestmod=bob_digestmod)

    # Create Blocklist and add words and authors to block

    # Blocklist alice
    blocklist_alice = Blocklist()
    blocklist_alice.loadFromFeed(alice_feed)
    blocklist_alice.blockAuthor(bob_feed.fid)  # alice blocks bob
    blocklist_alice.writeToFeed(alice_feed)

    # Blocklist bob

    blocklist_bob = Blocklist()
    blocklist_bob.loadFromFeed(bob_feed)
    blocklist_bob.blockWord("chicken")
    blocklist_bob.blockWord("house")
    blocklist_bob.writeToFeed(bob_feed)

    # Create BlocklistSettings
    settings_alice = Blocksettings()
    settings_alice.loadFromFeed(alice_feed)
    settings_alice.changeBlockLevel(Blocksettings.SOFTBLOCK)
    settings_alice.writeToFeed(alice_feed)

    settings_bob = Blocksettings()
    settings_bob.loadFromFeed(bob_feed)
    settings_bob.changeBlockLevel(Blocksettings.SOFTBLOCK)
    settings_bob.writeToFeed(bob_feed)

    # Demo Chat ( we pretend that Alice and Bob already synced their logs)
    alice_feed.write(["bacnet/chat", time.time(), "Chicken"])
    bob_feed.write(["bacnet/chat", time.time(), "Hello?"])

    alice_feed = Blocklist.filterFeed(blocklist_bob, settings_bob, alice_feed)  # bob filters alice's feed
    bob_feed = Blocklist.filterFeed(blocklist_alice, settings_alice, bob_feed)  # alice filters bob's feed

    chat = []
    for event in alice_feed:
        if event.content()[0] == "bacnet/chat":
            chat.append({"sender": "alice", "time": event.content()[1], "text": event.content()[2]})

    for event in bob_feed:
        if event.content()[0] == "bacnet/chat":
            chat.append({"sender": "bob", "time": event.content()[1], "text": event.content()[2]})

    chat.sort(key=lambda msg: msg["time"])

    for msg in chat:
        print(msg["sender"] + ": " + msg["text"])


if __name__ == "__main__":
    demo()
