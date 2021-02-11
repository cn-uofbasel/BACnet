from xeddsa.implementations import XEdDSA25519
from helpers import FOLDERNAME_KEYS
import os

# This is not cryptographically safe. To be that the program should be a fixed set of operations that run every time.

''' HOW TO USE
from signing import xeddsa_sign, xeddsa_verify

##### SENDING PART #####
msg = 'This is a secret message.'
pubkey, signed_msg = xeddsa_sign(msg)

#### RECEIVING PART ####
if xeddsa_verify(pubkey=pubkey, data=msg, signature=signed_msg):
    print('Verification successful!')
else:
    print('Verification failed!')
'''

path_keys = os.getcwd() + FOLDERNAME_KEYS + '/xed_keys.key'


def load_key():
    try:
        with open(path_keys, 'rb') as f:
            privkey = f.read()
            assert (len(privkey) == 32)
            print("Loaded saved xed private key.")
    except FileNotFoundError:
        print("No XEd private key found. Creating new key...")
        xed = XEdDSA25519(mont_priv=None, mont_pub=None)
        privkey = xed.generate_mont_priv()
        with open(path_keys, 'wb') as f:
            f.write(privkey)
            print("Xed private key saved.")
        pass
    return privkey


def xeddsa_sign(msg) -> (bytes, bytes):
    # Returns: public key, signed message
    xed_private_key = load_key()
    xed_send = XEdDSA25519(mont_priv=xed_private_key)
    xed_public_key = xed_send.mont_pub_from_mont_priv(xed_private_key)
    signed_msg = xed_send.sign(msg)
    return xed_public_key, signed_msg


def xeddsa_verify(pubkey, data, signature) -> bool:
    # Returns: True or False
    xed_recv = XEdDSA25519(mont_priv=None, mont_pub=pubkey)
    return xed_recv.verify(data=data, signature=signature)
