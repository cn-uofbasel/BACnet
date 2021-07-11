# import logging
# import os
# from ast import literal_eval
#
# import Crypto.PublicKey.RSA as RSA
# import nacl.exceptions
# import nacl.signing
#
# from BackEnd.settings import KEY_DIR
#
# logger = logging.getLogger(__name__)
#
#
# def get_keyfiles():
#     return os.listdir(KEY_DIR)
#
#
# def keyfile_exists(filename):
#     return os.listdir(KEY_DIR).__contains__(filename)


# class RSA_Keys:
#     """Helper Class to deal with RSA key pairs and single keys in memory."""
#     def __init__(self, filename, public_key=None, passphrase=None):
#         self.filename = filename
#         if public_key:
#             # We are storing a foreign publicKey
#             k = RSA.import_key(public_key)
#             self.pubkey = k
#             self.__write_key(filename + "/public.pem", k, passphrase=passphrase)
#         else:
#             # We are either loading a key in or generating a new one.
#             try:
#                 k = open(os.path.join(KEY_DIR, filename, "public.pem"), "rb").read()
#                 self.pubkey = RSA.importKey(k, passphrase=passphrase)
#             except FileNotFoundError:
#                 self.pubkey = None
#             try:
#                 k = open(os.path.join(KEY_DIR, filename, "private.pem"), "rb").read()
#                 self.privateKey = RSA.importKey(k, passphrase=passphrase)
#             except FileNotFoundError:
#                 self.privateKey = None
#             if not self.pubkey and not self.privateKey:
#                 # generate new key
#                 k = RSA.generate(1024, os.urandom)
#                 self.privateKey, self.pubkey = k, k.publickey()
#                 os.mkdir(os.path.join(KEY_DIR, filename))
#                 self.__write_file(passphrase=passphrase)
#
#     def as_string(self):  # debug
#         return str(
#             {
#                 'secret': self.pubkey.exportKey(),
#                 'pubkey': self.privateKey.exportKey(),
#             }
#         )
#
#     def __write_file(self, passphrase=""):
#         self.__write_key(self.filename + "/public.pem", self.pubkey, passphrase=passphrase)
#         self.__write_key(self.filename + "/private.pem", self.privateKey, passphrase=passphrase)
#
#     @staticmethod
#     def __write_key(filename: str, key: RSA.RsaKey, passphrase=None) -> None:
#         with open(os.path.join(KEY_DIR, filename), "wt") as fd:
#             fd.write(key.exportKey(passphrase=passphrase).decode("utf-8"))


# class ED25519:
#     """Helper Class to deal with ED25519 key pairs and single keys in memory."""
#     def __init__(self, filename, new=False, pk: bytes, sk=None):
#         self.filename = filename
#         self.hsk = True
#         if new:
#             self.sk = nacl.signing.SigningKey.generate()
#             self.pk = self.sk.verify_key
#             self.write_key()
#         elif pk:
#             self.pk: nacl.signing.VerifyKey = VerifyKey(pk)
#             self.hsk = False
#             self.write_key()
#         elif sk:
#             self.sk = nacl.signing.SigningKey(sk)
#             self.pk = self.sk.verify_key
#             self.write_key()
#         else:
#             try:
#                 k: dict = literal_eval(open(os.path.join(KEY_DIR, filename), "rt").read())
#             except FileNotFoundError:
#                 raise ValueError("Filename is faulty or key doesn't exist.")
#             if k["hsk"] == "1":
#                 self.sk = k["sk"].encode("ISO-8859-1")
#             self.pk = k["pk"].encode("ISO-8859-1")
#
#     def write_key(self):
#         with open(os.path.join(KEY_DIR, self.filename), "wt") as fd:
#             fd.write(self.as_string(self.hsk))
#             fd.close()
#
#     def get_pk(self):
#         return self.pk
#
#     def get_sk(self):
#         return self.sk
#
#     def as_string(self, hsk: bool):
#         if hsk:
#             return str({'type': 'ed25519',
#                         'hsk': '1',
#                         'pk': bytes(self.get_pk()).decode("ISO-8859-1"),
#                         'sk': bytes(self.get_sk()).decode("ISO-8859-1")
#                         })
#         else:
#             return str({'type': 'ed25519',
#                         'hsk': '0',
#                         'pk': bytes(self.get_pk()).decode("ISO-8859-1"),
#                         })
