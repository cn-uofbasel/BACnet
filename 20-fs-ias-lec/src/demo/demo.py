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
    # Alice did not create a key pair yet, lets create it!
    alice_h = crypto.HMAC(alice_digestmod)
    alice_h.create()
    with open("data/alice/alice-secret.key", "w") as f: 
        f.write('{\n  '+(',\n '.join(alice_h.as_string().split(','))[1:-1])+'\n}')
        alice_signer = crypto.HMAC(alice_digestmod, alice_h.get_private_key())

else:
    with open("data/alice/alice-secret.key", 'r') as f:
            key = eval(f.read())
            alice_h = crypto.HMAC(alice_digestmod, key["private"], key["feed_id"])
            alice_signer = crypto.HMAC(alice_digestmod, bytes.fromhex(alice_h.get_private_key()))

alice_feed = feed.FEED("data/alice/alice-feed.pcap", fid=alice_h.get_feed_id(), signer=alice_signer, create_if_notexisting=True, digestmod=alice_digestmod)

## Bob
bob_digestmod = "sha256"
bob_h, bob_signer = None, None

if not os.path.isfile("data/bob/bob-secret.key"):
    # Bob did not create a key pair yet, lets create it!
    bob_h = crypto.HMAC(bob_digestmod)
    bob_h.create()
    with open("data/bob/bob-secret.key", "w") as f:
        f.write('{\n  '+(',\n '.join(bob_h.as_string().split(','))[1:-1])+'\n}')
        bob_signer = crypto.HMAC(bob_digestmod, bob_h.get_private_key())
else:
    with open("data/bob/bob-secret.key", 'r') as f:
            key = eval(f.read())
            bob_h = crypto.HMAC(bob_digestmod, key["private"], key["feed_id"])
            bob_signer = crypto.HMAC(bob_digestmod, bytes.fromhex(bob_h.get_private_key()))


bob_feed = feed.FEED("data/bob/bob-feed.pcap", fid=bob_h.get_feed_id(), signer=bob_signer, create_if_notexisting=True, digestmod=bob_digestmod)


alice_feed.write(["bacnet/chat", "Hey, it is me Alice!"])
bob_feed.write(["bacnet/chat", "Hey, it is me Bob!"])

print(bob_feed.hprev)
