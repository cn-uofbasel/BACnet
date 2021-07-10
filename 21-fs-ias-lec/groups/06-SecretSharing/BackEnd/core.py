"""
::Export Module::
The core script contains all functions interfacing with the BACNetCore but not directly with other SecretSharing
related scripts. Other groups can import SecretSharing.BackEnd.core to make use of the functionality without getting
complications. core.py will be imported into actions.py and the UI can therefore interface with all functions
here as well. For example private messages should be implemented here.
"""

# BACnet imports

# import BACnetCore
# import BACnetTransport

from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.PublicKey import RSA
from enum import Enum
from os import urandom
from ast import literal_eval
import cbor2
import json


# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~

ENCODING = 'ISO-8859-1'


# ~~~~~~~~~~~~ Utility  ~~~~~~~~~~~~

def pad(s, block_size):
    return s + (block_size - len(s) % block_size) * int.to_bytes(block_size - len(s) % block_size, byteorder="little", length=1)


def unpad(s):
    padding = int.from_bytes(s[len(s) - 2:len(s) - 1], byteorder="little")
    return s[0:-padding]


# ~~~~~~~~~~~~ Events  ~~~~~~~~~~~~

class E_TYPE(Enum):
    SHARE = 1,
    REQUEST = 2,
    REPLY = 3


def sub_event(t: E_TYPE, receivers_pubkey=None, shard=None, password=None) -> str:
    # content of a message
    content = {
        "TYPE": t.value,
        "PASSWORD": password,
        "SHARD": shard,
    }

    # random AES cipher
    aes_key = urandom(16)
    aes_iv = urandom(16)
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)

    # encrypt complete content as padded string
    encrypted_content = aes_cipher.encrypt(pad(json.dumps(content).encode(ENCODING), 16))

    s_event = {
        "AES": receivers_pubkey.encrypt(aes_key).decode(ENCODING),
        "IV": aes_iv.decode(ENCODING),
        "CONTENT": encrypted_content.decode(ENCODING)
    }

    return json.dumps(s_event)


def decrypt_sub_event(s_event, private_key):
    """Decrypts a plaintext event."""
    # Decryption
    e: dict = literal_eval(s_event)
    aes_key = private_key.decrypt(e["AES"].encode(ENCODING))
    aes_iv = e["IV"].encode(ENCODING)
    ciphertext = e["CONTENT"].encode(ENCODING)
    del e
    plaintext_p = AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(ciphertext)
    c: dict = json.loads(plaintext_p[:-plaintext_p[-1]].decode(ENCODING))

    return E_TYPE(c["TYPE"]), c["SHARE"].encode(ENCODING), c["password"].encode(ENCODING)


# ~~~~~~~~~~~~ Shamir / Packages  ~~~~~~~~~~~~


def split_small_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is less than 16 bytes. Pads the secret before passing it to split_normal..()"""
    return split_normal_secret_into_share_packages(mapping, pad(secret, 16), threshold, number)


def split_normal_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is exactly 16 bytes. No padding required."""
    shares = Shamir.split(threshold, number, secret, ssss=False)
    return [
        bytearray(int.to_bytes(mapping, byteorder="little", signed=False, length=1)) +
        bytearray(int.to_bytes(index, byteorder="little", signed=False, length=1)) +
        bytearray(share) for index, share in shares
    ]


def split_large_secret_into_share_packages(mapping: int, secret: bytes, number_packages: int):
    """Splits a secret of size 0.016 < s < 4.096 Kb into share packages. To keep it simple the threshold is equal to the
    number of shares created in total. """

    if not 0 < len(secret) < 4096:
        raise ValueError("Secret size is not supported, expected between 0 and 4.096 Kb.")

    # secret_padded = pad(secret, 16)  # pad secret so len(s) % 16 == 0 ToDo this is done in pw encryption rn... gate.py
    sub_secrets = [secret[i*16:(i+1)*16] for i in range(len(secret)//16)]
    number_sub_secrets = len(sub_secrets)

    buffer = [[] for i in range(0, number_packages)]

    for i in range(0, len(sub_secrets)):  # split and package so none contains 2 shares of same sub secret
        sub_shares = Shamir.split(number_packages, number_packages, sub_secrets[i], ssss=False)

        for j in range(0, number_packages):
            sub_idx, sub_share = sub_shares[j]
            sub_package = b''.join([
                int.to_bytes(len(sub_share), byteorder="little", length=1),
                bytes(sub_share)
            ])
            buffer[j].append(sub_package)

    return [
        b''.join([  # add plaintext info
            int.to_bytes(mapping, byteorder="little", length=1),
            int.to_bytes(number_sub_secrets, byteorder="little", length=1),
            int.to_bytes(number_packages, byteorder="little", length=1),
            int.to_bytes(j, byteorder="little", length=1),
            b''.join(buffer[j])
        ]) for j in range(0, number_packages)
    ]


def recover_normal_secret(packages):
    """Reconstructs a secret from packages, padding not removed yet."""
    return Shamir.combine([(int.from_bytes(package[1:2], "little"), package[2:]) for package in packages], ssss=False)


def recover_large_secret(packages):
    """Reconstructs a larger secret from packages, padding not removed yet."""
    number_sub_secrets = int.from_bytes(packages[0][1:2], "little")
    number_packages = int.from_bytes(packages[0][2:3], "little")
    sub_shares = [[] for i in range(number_sub_secrets)]

    for i in range(0, number_packages):
        share_id, share = int.from_bytes(packages[i][3:4], byteorder="little"), \
                          packages[i][4:len(packages[i])]

        for j in range(0, number_sub_secrets):
            next_length, buffer = int.from_bytes(share[0:1], byteorder="little"), share[1:]
            sub_shares[j].append((share_id + 1, buffer[0:next_length]))
            share = buffer[next_length:]

    buffer = b''
    for i in range(0, len(sub_shares)):
        buffer += Shamir.combine(sub_shares[i], ssss=False)

    return buffer
