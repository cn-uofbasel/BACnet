#!/usr/bin/env python3

# lib/crypto.py


import nacl.signing
import nacl.exceptions


class ED25519:

    def __init__(self, privateKey = None):
        try:
            self.sk = nacl.signing.SigningKey(privateKey)
        except:
            self.sk = None

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
                    'public': self.get_public_key().hex(),
                    'private': self.get_private_key().hex()})


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        # default action: create a key pair and pretty print the key values:
        key_pair = ED25519()
        key_pair.create()
        print("# new ED25519 key pair: ALWAYS keep the private key as a secret")
        print('{\n  '+(',\n '.join(key_pair.as_string().split(','))[1:-1])+'\n}')
    elif sys.argv[1] == 'test':
        print("Creating an ED25519 key pair and testing signing")

        # generate random key pair
        key_pair = ED25519()
        key_pair.create()
        print("key pair is", key_pair.as_string())
        secret = key_pair.get_private_key()

        msg = "hello world test 1234".encode()
        signature = key_pair.sign(msg)

        print("verify:1", ED25519.verify(key_pair.get_public_key(),
                                         msg, signature))


        # use previously generated (secret) key, test with concatenated sign+msg
        kp2 = ED25519(secret)
        print("verify2:", ED25519.verify(kp2.get_public_key(), signature+msg))
    else:
        print(f"usage: {sys.argv[0]} [test]")

# eof
