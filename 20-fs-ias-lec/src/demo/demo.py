from lib.crypto import HMAC
import os.path


if not os.path.isdir("data"): 
    os.mkdir("data")
    os.mkdir("data/alice")
    os.mkdir("data/bob")

# Generate a key pair 

## Alice
digestmod = "sha256"
h = HMAC(digestmod)
h.create()

f = open("data/alice/alice-secret.key", "w")
f.write(h.as_string())
f.close()

## Bob
digestmod = "sha256"
h = HMAC(digestmod)
h.create()
f = open("data/bob/bob-secret.key", "w")
f.write(h.as_string())
f.close()


