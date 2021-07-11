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
import logging


# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
logger = logging.getLogger(__name__)
ENCODING = 'ISO-8859-1'


# ~~~~~~~~~~~~ Utility  ~~~~~~~~~~~~

def pad(data) -> bytes:
    logger.debug("called")
    padding = AES.block_size - len(data) % AES.block_size
    data += bytes([padding]) * padding
    return data


def unpad(data) -> bytes:
    logger.debug("called")
    return data[0:-data[-1]]


# ~~~~~~~~~~~~ Events  ~~~~~~~~~~~~

class E_TYPE(Enum):
    SHARE = 1,
    REQUEST = 2,
    REPLY = 3


def sub_event(t: E_TYPE, receivers_pubkey=None, shard=None, password=None) -> str:
    # content of a message
    content = {
        "TYPE": t.value,
        "SHARD": shard,
    }

    # random AES cipher
    aes_key = urandom(16)
    aes_iv = urandom(16)
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)

    # encrypt complete content as padded string
    encrypted_content = aes_cipher.encrypt(pad(json.dumps(content).encode(ENCODING)))

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
    logger.debug("called")
    return split_normal_secret_into_share_packages(mapping, pad(secret), threshold, number)


def split_normal_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is exactly 16 bytes. No padding required."""
    logger.debug("called")

    shares = Shamir.split(threshold, number, secret, ssss=False)

    indexes = [sh[0] for sh in shares]
    shares = [sh[1] for sh in shares]  # Todo Cleanup

    # plaintext info
    return [
        bytearray(int.to_bytes(mapping, byteorder="little", signed=False, length=1)) +
        bytearray(int.to_bytes(indexes[i], byteorder="little", signed=False, length=1)) +
        bytearray(shares[i]) for i in range(0, len(shares))
    ]


def split_large_secret_into_share_packages(mapping: int, secret: bytes, number_packages: int, threshold: int):
    """Splits a secret of size 0.016 < s < 4.096 Kb into share packages. To keep it simple the threshold is equal to the
    number of shares created in total. """
    logger.debug("called")

    if not 0 < len(secret) < 4096:
        raise ValueError("Secret size is not supported, expected between 0 and 4.096 Kb.")

    secret_padded = pad(secret)  # pad secret so len(s) % 16 == 0
    sub_secrets = [secret_padded[i*16:(i+1)*16] for i in range(len(secret_padded)//16)]
    number_sub_secrets = len(sub_secrets)

    buffer = [[] for i in range(0, number_packages)]

    for i in range(0, len(sub_secrets)):  # split and package so none contain 2 shares of same sub secret
        sub_shares = Shamir.split(threshold, number_packages, sub_secrets[i], ssss=False)

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
            int.to_bytes(threshold, byteorder="little", length=1),
            int.to_bytes(j, byteorder="little", length=1),
            b''.join(buffer[j])
        ]) for j in range(0, number_packages)
    ]


def recover_normal_secret(packages):
    """Reconstructs a secret from packages, padding not removed yet."""
    logger.debug("called")
    return Shamir.combine([(int.from_bytes(package[1:2], "little"), package[2:]) for package in packages], ssss=False)


def recover_large_secret(packages):
    """Reconstructs a larger secret from packages, padding not removed yet."""
    logger.debug("called")
    number_sub_secrets = int.from_bytes(packages[0][1:2], "little")
    threshold = int.from_bytes(packages[0][2:3], "little")
    sub_shares = [[] for i in range(number_sub_secrets)]

    for i in range(0, threshold):
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



# Lieber Colin,
#
# Ich wuerde von Nein ausgehen, aber es ist euer Projekt, also ihr koennt selber auch annahmen treffen
#
# Ein ganz einfacher Gedanke zu dem Nein fall:
# Ist das Secret mit einem Passwort verschlüsselt, kann der shareholder es ohne das Passwort herrausgeben.
# Denn es gibt nur 2 Faelle:
# 1) Entweder das Passwort ist sicher, dann wird egal wer das verschluesselte Secret in die Haende bekommt damit nichts anfangen koennen.
# 2) Oder das Passwort ist nicht sicher, dann koennen die Shareholder es aber auch selber Bruteforcen.
#
# Wird das Secret heraussgegeben, dann kann hier vielleicht eine Sicherheitsfrage verwendet werden, damit es nicht direkt jeder bekommt.
#
# Erhaelt der legitime User nach beantworten der Sicherheitsfrage kann der das Passwort lokal eingeben. Und keinen anderer sieht es.
#
# Liebe Gruese
# Christopher