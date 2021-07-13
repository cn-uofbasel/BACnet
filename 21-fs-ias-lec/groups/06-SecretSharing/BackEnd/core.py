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

from json import JSONDecodeError
from typing import Tuple

from BackEnd.exceptions import SecretSharingError

from Crypto.Protocol.SecretSharing import Shamir
from nacl.public import PublicKey, PrivateKey, Box
from lib.crypto import ED25519
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
import enum

from os import urandom
from ast import literal_eval
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

class E_TYPE(enum.IntEnum):
    SHARE = 1,
    REQUEST = 2,
    REPLY = 3


def create_sub_event(t: E_TYPE, sk: bytes, pk: bytes, password=None, shard=None, name=None) -> str:
    if t == E_TYPE.SHARE:
        logger.debug("Creating SHARE Sub-Event:")
        content = {"TYPE": t.value, "SHARE": __aux_encrypt_bToS(password, shard), "NAME": __aux_encrypt_sToS(password, name)}
    elif t == E_TYPE.REQUEST:
        logger.debug("Creating REQUEST Sub-Event:")
        content = {"TYPE": t.value, "SHARE": "None", "NAME": __aux_encrypt_sToS(password, name)}
    elif t == E_TYPE.REPLY:
        logger.debug("Creating REPLY Sub-Event:")
        content = {"TYPE": t.value, "SHARE": shard.decode(ENCODING), "NAME": name}
    else:
        raise SecretSharingError("Unable to identify event-type.")

    # random AES cipher
    key = urandom(16)
    iv = urandom(16)
    aes_cipher = AES.new(key, AES.MODE_CBC, iv=iv)

    # encrypt complete content with aes key
    encrypted_content = b''.join([iv, aes_cipher.encrypt(pad(json.dumps(content).encode(ENCODING)))])

    return json.dumps({
        # encrypt aes key with asymmetric encryption
        "AES": Box(PrivateKey(sk), PublicKey(pk)).encrypt(key).decode(ENCODING),
        "CONTENT": encrypted_content.decode(ENCODING)
    })


def decrypt_sub_event(sub_event_string: str, sk: bytes, pk: bytes, password: str) -> Tuple[E_TYPE, bytes, str]:
    """Decrypts a plaintext event."""
    sub_event: dict = literal_eval(sub_event_string)
    key = Box(PrivateKey(sk), PublicKey(pk)).decrypt(sub_event.get("AES").encode(ENCODING))
    ciphertext = sub_event.get("CONTENT").encode(ENCODING)
    content = AES.new(key, AES.MODE_CBC, ciphertext[0:16]).decrypt(ciphertext[16:])

    try:
        c: dict = json.loads(unpad(content).decode(ENCODING))
    except JSONDecodeError:
        # Trying to decrypt event meant for someone else, means wrong pubkey used to decrypt aes key.
        raise SecretSharingError("Can't decrypt sub-event.")

    logger.debug(json.dumps(c, indent=4))

    if E_TYPE(c.get("TYPE")) == E_TYPE.SHARE or E_TYPE(c.get("TYPE")) == E_TYPE.REQUEST:
        return E_TYPE(c.get("TYPE")), c.get("SHARE").encode(ENCODING), c.get("NAME")
    elif E_TYPE(c.get("TYPE")) == E_TYPE.REPLY:
        return E_TYPE(c.get("TYPE")), __aux_decrypt_sToB(password, c.get("SHARE")), __aux_decrypt_sToS(password, c.get("NAME"))
    else:
        raise SecretSharingError("Unable to identify event-type.")


# ~~~~~~~~~~~~ Shamir / Packages  ~~~~~~~~~~~~


def split_small_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is less than 16 bytes. Pads the secret before passing it to split_normal..()"""
    logger.debug("called")
    return split_normal_secret_into_share_packages(mapping, pad(secret), threshold, number)


def split_normal_secret_into_share_packages(mapping: int, secret: bytes, threshold: int, number: int):
    """For a secret that is exactly 16 bytes. No padding required."""
    logger.debug("called")

    shares = Shamir.split(threshold, number, secret, ssss=False)

    # plaintext info
    return [
        bytearray(int.to_bytes(mapping, byteorder="little", signed=False, length=1)) +
        bytearray(int.to_bytes(index, byteorder="little", signed=False, length=1)) +
        bytearray(share) for index, share in shares
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
    """Reconstructs a secret original size 16 bytes from packages, padding not removed yet."""
    logger.debug("called")
    return Shamir.combine([(int.from_bytes(package[1:2], "little"), package[2:]) for package in packages], ssss=False)


def recover_large_secret(packages):
    """Reconstructs a larger secret from packages, padding not removed yet."""
    logger.debug("called")
    number_sub_secrets = int.from_bytes(packages[0][1:2], "little")
    threshold = int.from_bytes(packages[0][2:3], "little")
    sub_shares = [[] for i in range(number_sub_secrets)]

    for i in range(0, threshold):  # only iterate over minimum number
        share_id, share = int.from_bytes(packages[i][3:4], byteorder="little"), \
                          packages[i][4:len(packages[i])]

        for j in range(0, number_sub_secrets):  # reorder shares according to secret id
            next_length, buffer = int.from_bytes(share[0:1], byteorder="little"), share[1:]
            sub_shares[j].append((share_id + 1, buffer[0:next_length]))
            share = buffer[next_length:]

    _secret = b''
    for i in range(0, len(sub_shares)):
        _secret += Shamir.combine(sub_shares[i], ssss=False)  # recombine sub-secrets and concentrate

    return unpad(_secret)


# ~~~~~~~~~~~~ Password Share Encryption ~~~~~~~~~~~~

# auxiliary encryption for readability

def __aux_encrypt_sToS(password: str, plaintext: str) -> str:
    return pwd_encrypt(password, plaintext.encode(ENCODING)).decode(ENCODING)


def __aux_encrypt_bToS(password: str, plaintext: bytes) -> str:
    return pwd_encrypt(password, plaintext).decode(ENCODING)


def __aux_decrypt_sToS(password: str, plaintext: str):
    return pwd_decrypt(password, plaintext.encode(ENCODING)).decode(ENCODING)


def __aux_decrypt_sToB(password: str, plaintext: str):
    return pwd_decrypt(password, plaintext.encode(ENCODING))


# password encryption

def pwd_encrypt(password: str, shard: bytes) -> bytes:
    logging.debug("called")
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    shard_padded = pad(shard)
    iv = urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b''.join([iv, cipher.encrypt(shard_padded)])


def pwd_decrypt(password: str, encrypted_secret: bytes) -> bytes:
    logging.debug("called")
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    cipher = AES.new(key, AES.MODE_CBC, IV=encrypted_secret[0:16])
    return unpad(cipher.decrypt(encrypted_secret[16:]))


# ~~~~~~~~~~~~ Keys ~~~~~~~~~~~~

def generate_keys() -> dict:
    ed25519 = ED25519()
    ed25519.create()
    return literal_eval(ed25519.as_string())

