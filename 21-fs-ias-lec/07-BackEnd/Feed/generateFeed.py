import sys

# add the lib to the module folder
sys.path.append("./lib")

import os
import crypto
import feed

name = input("please enter your name: ")
print("your feed-name: " + name)

if not os.path.isdir("data"):
    os.mkdir("data")

if not os.path.isdir("data/" + name):
    os.mkdir("data/" + name)

# Generate a key pair

## generate a feed
digestmod = "sha256"
h, signer = None, None

# Generate a Key if non exists
if not os.path.isfile("data/" + name + "/" + name + "-secret.key"):
    print("Create " + name + "'s key pair at data/" + name + "/" + name + "-secret.key")
    h = crypto.HMAC(digestmod)
    h.create()
    with open("data/" + name + "/" + name + "-secret.key", "w") as f:
        f.write('{\n  ' + (',\n '.join(h.as_string().split(','))[1:-1]) + '\n}')
        signer = crypto.HMAC(digestmod, h.get_private_key())

print("Read " + name + "'s secret key.")
with open("data/" + name + "/" + name + "-secret.key", 'r') as f:
    key = eval(f.read())
    h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
    signer = crypto.HMAC(digestmod, bytes.fromhex(h.get_private_key()))

print("Create or load" + name + "'s feed at data/" + name + "/" + name + "-feed.pcap")
myfeed = feed.FEED(fname="data/" + name + "/" + name + "-feed.pcap", fid=h.get_feed_id(), signer=signer,
                       create_if_notexisting=True, digestmod=digestmod)



