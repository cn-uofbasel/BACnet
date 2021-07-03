import os
import Crypto.PublicKey.RSA as RSA
from BackEnd.settings import KEY_DIR
import nacl


def get_keyfiles():
    return os.listdir(KEY_DIR)


def keyfile_exists(filename):
    return os.listdir(KEY_DIR).__contains__(filename)


class RSA_Keys:
    """Helper Class to deal with RSA key pairs and single keys in memory."""
    def __init__(self, filename, public_key=None, passphrase=None):
        self.filename = filename
        if public_key:
            # We are storing a foreign publicKey
            k = RSA.import_key(public_key)
            self.pubkey = k
            self.__write_key(filename + "/public.pem", k, passphrase=passphrase)
        else:
            # We are either loading a key in or generating a new one.
            try:
                k = open(os.path.join(KEY_DIR, filename, "public.pem"), "rb").read()
                self.pubkey = RSA.importKey(k, passphrase=passphrase)
            except FileNotFoundError:
                self.pubkey = None
            try:
                k = open(os.path.join(KEY_DIR, filename, "private.pem"), "rb").read()
                self.privateKey = RSA.importKey(k, passphrase=passphrase)
                pass
            except FileNotFoundError:
                self.privateKey = None
            if not self.pubkey and not self.privateKey:
                # generate new key
                k = RSA.generate(2048, os.urandom)
                self.privateKey, self.pubkey = k, k.publickey()
                os.mkdir(os.path.join(KEY_DIR, filename))
                self.__write_file(passphrase=passphrase)

    def as_string(self):  # debug
        return str(
            {
                'secret': self.pubkey.exportKey(),
                'pubkey': self.privateKey.exportKey(),
            }
        )
        
    def __write_file(self, passphrase=""):
        self.__write_key(self.filename + "/public.pem", self.pubkey, passphrase=passphrase)
        self.__write_key(self.filename + "/private.pem", self.privateKey, passphrase=passphrase)

    def __write_key(self, filename: str, key: RSA.RsaKey, passphrase=None) -> None:
        with open(os.path.join(KEY_DIR, filename), "wt") as fd:
            fd.write(key.exportKey(passphrase=passphrase).decode("utf-8"))
