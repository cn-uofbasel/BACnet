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


cType = Enum("Shard", "Request")


def pad(s, block_size):
    return s + (block_size - len(s) % block_size) * int.to_bytes(block_size - len(s) % block_size, byteorder="little", length=1)


def unpad(s):
    padding = int.from_bytes(s[len(s) - 2:len(s) - 1], byteorder="little")
    return s[0:-padding]


def event(type: str, receivers_pubkey=None, shard=None, auth_msg=None, index=None, keyid=None, text=None):
    # random HMAC cipher
    hash_key = urandom(16)
    hash_cipher = HMAC.new(hash_key, digestmod=SHA256)
    # Maybe whole content? New Field?

    content = {
        "TYPE": type.name,
        "SHARD": shard,
        "HASH": auth_msg,
        "INDEX": index,
        "KEYID": keyid,
        "RECV": receivers_pubkey,
        "TEXT": text
    }

    # random AES cipher
    aes_key = urandom(16)
    aes_iv = urandom(16)
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)

    # encrypt complete content as padded string
    encrypted_content = aes_cipher.encrypt(pad(json.dumps(content).encode("utf-8"), 16))

    e = {
        "HMAC": receivers_pubkey.encrypt(hash_key).decode("utf-8"),
        "AES": receivers_pubkey.encrypt(aes_key).decode("utf-8"),
        "IV": aes_iv.decode("utf-8"),
        "CONTENT": encrypted_content.decode("utf-8")
    }

    return json.dumps(e)


def decrypt_event(event, private_key):
    """Decrypts a plaintext event."""
    e: dict = literal_eval(event)
    hash_key = private_key.decrypt(e["HMAC"].encode("utf-8"))
    aes_key = private_key.decrypt(e["AES"].encode("utf-8"))
    aes_iv = e["IV"].encode("utf-8")
    ciphertext = e["CONTENT"].encode("utf-8")
    del e

    # Authentication

    # Decryption
    plaintext_p = AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(ciphertext)
    c: dict = json.loads(plaintext_p[:-plaintext_p[-1]].decode("utf-8"))
    t = cType(c["TYPE"])

    # Switch type in subroutines, return through this function eg


# SHAMIR INTERFACING FUNCTIONS


def split_small_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is less than 16 bytes."""
    return split_normal_secret_into_share_packages(mapping, pad(secret, 16), threshold, number)


def split_normal_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is exactly 16 bytes."""
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

    secret_padded = pad(secret, 16)  # pad secret so len(s) % 16 == 0
    sub_secrets = [secret_padded[i*16:(i+1)*16] for i in range(len(secret_padded)//16)]
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
    return Shamir.combine([(int.from_bytes(package[1:2], "little"), package[2:]) for package in packages], ssss=False)


def recover_large_secret(packages):
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