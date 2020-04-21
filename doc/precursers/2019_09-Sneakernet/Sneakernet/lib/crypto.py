# sn/lib/crypto.py

import nacl.signing
import nacl.encoding
import nacl.public
import nacl.exceptions


class ED25519:

    def __init__(self):
        self.seed = 0
        self.public = b'...'
        self.private = b'...'

    def create(self):
        self.private = nacl.signing.SigningKey.generate()
        self.public = bytes(self.private.verify_key)
        self.private = bytes(self.private)

    def sign(self, blob):
        signing_key = nacl.signing.SigningKey(self.private)
        signed = signing_key.sign(blob)
        return signed.signature

    @staticmethod
    def validate(public, blob, signature):
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
