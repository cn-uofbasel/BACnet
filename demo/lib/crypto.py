#!/usr/bin/env python3

# lib/crypto.py


try:
    import hmac
    import nacl.signing
    import nacl.exceptions
    import os

    def to_hex(b):
        return b.hex()
except:
    import binascii
    import lopy4_hmac as hmac
    import os

    def to_hex(b):
        return binascii.hexlify(b)

# signature info
SIGNINFO_ED25519     = 0
SIGNINFO_HMAC_SHA256 = 1
SIGNINFO_HMAC_SHA1   = 2
SIGNINFO_HMAC_MD5    = 3


sinfo2mod = {
    SIGNINFO_HMAC_SHA256: 'sha256',
    SIGNINFO_HMAC_SHA1: 'sha1',
    SIGNINFO_HMAC_MD5: 'md5'
}

mod2sinfo = {
    'sha256': SIGNINFO_HMAC_SHA256,
    'sha1': SIGNINFO_HMAC_SHA1,
    'md5': SIGNINFO_HMAC_MD5
}

class ED25519:

    def __init__(self, privateKey = None):
        self.sinfo = SIGNINFO_ED25519
        try:
            self.sk = nacl.signing.SigningKey(privateKey)
        except:
            self.sk = None

    def get_sinfo(self):
        return self.sinfo

    def create(self):
        self.sk = nacl.signing.SigningKey.generate()

    def sign(self, blob):
        signed = self.sk.sign(blob)
        return signed.signature

    def get_public_key(self):
        return bytes(self.sk.verify_key)

    def get_private_key(self):
        return bytes(self.sk)

    @staticmethod
    def verify(public, blob, signature=None):
        """
        :param public: public key as bytes
        :param blob: Binary Large Object
        :param signature: The signature of the blob to verify against. If the value of blob is the concated signature and blob, this parameter can be None.
        :return: True when the Blob is successfully verified
        """
        verify_key = nacl.signing.VerifyKey(public)
        try:
            verify_key.verify(blob, signature)
        except nacl.exceptions.BadSignatureError:
            return False
        else:
            return True

    def as_string(self):
        return str({'type': 'ed25519',
                    'public': to_hex(self.get_public_key()),
                    'private': to_hex(self.get_private_key())})


class HMAC:
    
    def __init__(self, mod='sha256', sharedSecret = None, fid=None):
        self.mod = mod
        self.sinfo = mod2sinfo[mod]
        self.ss = sharedSecret
        self.fid = fid

    def get_sinfo(self):
        return self.sinfo

    def create(self):
        self.ss = os.urandom(16)
        self.fid = os.urandom(8)

    def sign(self, blob):
        h = hmac.new(self.ss, blob, self.mod)
        return h.digest()

    def get_feed_id(self):
        return self.fid

    def get_private_key(self):
        return self.ss

    @staticmethod
    def verify(mod, secret, blob, signature=None):
        """
        :param blob: Binary Large Object
        :param signature: The signature of the blob to verify against. If the value of blob is the concated signature and blob, this parameter can be None.
        :return: True when the Blob is successfully verified
        """
        h = HMAC(mod, secret)
        if signature == None:
            hm = hmac.new(b'', b'', mod)
            signature = blob[:hm.digest_size]
            blob = blob[hm.digest_size:]
        return hmac.compare_digest(h.sign(blob), signature)

    def as_string(self):
        return str({'type': 'hmac_' + self.mod,
                    'feed_id': to_hex(self.get_feed_id()),
                    'private': to_hex(self.get_private_key())})


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='BACnet key generation')
    parser.add_argument('--hmac', choices=['sha256','sha1','md5'],
                             help='choose HMAC hash, instead of ED25519')
    parser.add_argument('test', nargs='?',
                        help='run test code instead generating a key(pair)')
    args = parser.parse_args()

    if args.test == None:
        # default action: create a key (pair) and pretty print the key values:
        if args.hmac != None:
            digestmod = args.hmac
            h = HMAC(digestmod)
            h.create()
            print("# new HMAC_" + digestmod.upper() + ": share it ONLY with trusted peers")
            print('{\n  '+(',\n '.join(h.as_string().split(','))[1:-1])+'\n}')
        else:
            key_pair = ED25519()
            key_pair.create()
            print("# new ED25519 key pair: ALWAYS keep the private key as a secret")
            print('{\n  '+(',\n '.join(key_pair.as_string().split(','))[1:-1])+'\n}')
    else:
        if args.hmac != None:
            digestmod = args.hmac
            print("Creating an HMAC_" + digestmod.upper() + " key, testing signing")
            
            # generate random key
            h = HMAC(digestmod)
            h.create()
            print("shared key is", h.as_string())
            secret = h.get_private_key()

            msg = ("hello world test 1234 / hmac_" + digestmod).encode()
            signature = h.sign(msg)
            print("signature length is", len(signature), "bytes")

            print("verify1:", HMAC.verify(digestmod, secret, msg, signature))
            print("verify2:", HMAC.verify(digestmod, secret, signature+msg))
        else:
            print("Creating an ED25519 key pair, testing signing")

            # generate random key pair
            key_pair = ED25519()
            key_pair.create()
            print("key pair is", key_pair.as_string())
            secret = key_pair.get_private_key()

            msg = "hello world test 1234 / ed25519".encode()
            signature = key_pair.sign(msg)

            print("verify1:", ED25519.verify(key_pair.get_public_key(),
                                             msg, signature))


            # use previously generated (secret) key, test with concatenated sign+msg
            kp2 = ED25519(secret)
            print("verify2:", ED25519.verify(kp2.get_public_key(), signature+msg))

# eof
