"""
::Export Module::
The core script contains all functions interfacing with the BACNetCore but not directly with other SecretSharing
related scripts. Other groups can import SecretSharing.BackEnd.core to make use of the functionality without getting
complications.
"""

# BACnet imports

# import BACnetCore
# import BACnetTransport
#Kind of breaks the export feature of this module...
import Event

import os
from json import JSONDecodeError
from typing import Tuple, List

from BackEnd.exceptions import *

from Crypto.Protocol.SecretSharing import Shamir
from nacl.public import PublicKey, PrivateKey, Box
from nacl.signing import SigningKey, VerifyKey
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
import enum

from os import urandom
import json
import logging


# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~

logger = logging.getLogger(__name__)
ENCODING = 'ISO-8859-1'

# Todo expand application for larger secrets
# Prefix length is 1 byte right now. So MAX supported secret length is < 255*16 bytes.
# BYTE_O Needed to grab and place the prefixes. But it is possible to expand the prefixes
# for packages, (ctrl f plaintext info & ctrl f int.from_bytes) to support really large packages in theory,
# it will just take more time to debug than incentives exist at this time. :)

BYTE_O = "little"



# ~~~~~~~~~~~~ Request Handler ~~~~~~~~~~~~

rq_handler = None


def set_request_handler(rqh) -> None:
    rq_handler = rqh


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
        content = {"TYPE": t.value, "SHARE": pwd_encrypt_btos(password, shard), "NAME": pwd_encrypt_name(password, name)}
    elif t == E_TYPE.REQUEST:
        logger.debug("Creating REQUEST Sub-Event:")
        content = {"TYPE": t.value, "SHARE": "None", "NAME": pwd_encrypt_name(password, name)}
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
    content_dict = {
        # encrypt aes key with asymmetric encryption
        "AES": Box(SigningKey(sk).to_curve25519_private_key(), VerifyKey(pk).to_curve25519_public_key()).encrypt(key).decode(ENCODING),
        "CONTENT": encrypted_content.decode(ENCODING)
    }
    return json.dumps(content_dict)

def decrypt_sub_event(sub_event_string: str, sk: bytes, pk: bytes, password: str) -> Tuple[E_TYPE, bytes, str]:
    """Decrypts a plaintext event."""
    sub_event: dict = json.loads(sub_event_string)
    try:
        key = Box(SigningKey(sk).to_curve25519_private_key(), VerifyKey(pk).to_curve25519_public_key()).decrypt(sub_event.get("AES").encode(ENCODING))
        ciphertext = sub_event.get("CONTENT").encode(ENCODING)
        content = AES.new(key, AES.MODE_CBC, ciphertext[0:16]).decrypt(ciphertext[16:])
        c: dict = json.loads(unpad(content).decode(ENCODING))
    except JSONDecodeError:
        # Trying to decrypt event meant for someone else, means wrong pubkey used to decrypt aes key.
        raise SubEventDecryptionException("Can't decrypt sub-event.", sub_event)
    logger.debug(json.dumps(c, indent=4))
    if E_TYPE(c.get("TYPE")) == E_TYPE.SHARE or E_TYPE(c.get("TYPE")) == E_TYPE.REQUEST:
        return E_TYPE(c.get("TYPE")), c.get("SHARE").encode(ENCODING), c.get("NAME")
    elif E_TYPE(c.get("TYPE")) == E_TYPE.REPLY:
        share = c.get("SHARE")
        return E_TYPE(c.get("TYPE")), pwd_decrypt_stob(password, c.get("SHARE")), pwd_decrypt_name(password, c.get("NAME"))
    else:
        raise SecretSharingError("Unable to identify event-type.")


# ~~~~~~~~~~~~ Shamir / Packages  ~~~~~~~~~~~~


def split_small_secret_into_share_packages(secret: bytes, threshold: int, number_of_packages: int):
    """For a secret that is less than 16 bytes. Pads the secret before passing it to split_normal..()"""
    logger.debug("called")
    return split_normal_secret_into_share_packages(pad(secret), threshold, number_of_packages)


def split_normal_secret_into_share_packages(secret: bytes, threshold: int, number_of_packages: int):
    """For a secret that is exactly 16 bytes. No padding required."""
    logger.debug("called")

    shares = Shamir.split(threshold, number_of_packages, secret, ssss=False)

    # plaintext info
    return [
        bytearray(int.to_bytes(index, byteorder=BYTE_O, signed=False, length=1)) +
        bytearray(share) for index, share in shares
    ]


def split_large_secret_into_share_packages(secret: bytes, threshold: int, number_of_packages: int):
    """Splits a secret of size 0.016 < s < 4.080 Kb into share packages. To keep it simple the threshold is equal to the
    number of shares created in total. """
    logger.debug("called")

    if not 0 < len(secret) < 4080:
        raise ValueError("Secret size is not supported, expected between 0 and 4.080 Kb.")

    secret_padded = pad(secret)  # pad secret so len(s) % 16 == 0
    sub_secrets = [secret_padded[i*16:(i+1)*16] for i in range(len(secret_padded)//16)]
    number_sub_secrets = len(sub_secrets)

    buffer = [[] for i in range(0, number_of_packages)]

    for i in range(0, len(sub_secrets)):  # split and package so none contain 2 shares of same sub secret
        sub_shares = Shamir.split(threshold, number_of_packages, sub_secrets[i], ssss=False)

        for j in range(0, number_of_packages):
            sub_idx, sub_share = sub_shares[j]

            sub_package = b''.join([
                int.to_bytes(len(sub_share), byteorder=BYTE_O, length=1),
                bytes(sub_share)
            ])

            buffer[j].append(sub_package)

    return [
        b''.join([  # add plaintext info
            int.to_bytes(number_sub_secrets, byteorder=BYTE_O, length=1),
            int.to_bytes(threshold, byteorder=BYTE_O, length=1),
            int.to_bytes(j, byteorder=BYTE_O, length=1),
            b''.join(buffer[j])
        ]) for j in range(0, number_of_packages)
    ]


def recover_normal_secret(packages):
    """Reconstructs a secret original size 16 bytes from packages, padding not removed yet."""
    logger.debug("called")
    return Shamir.combine([(int.from_bytes(package[0:1], BYTE_O), package[1:]) for package in packages], ssss=False)


def recover_large_secret(packages):
    """Reconstructs a larger secret from packages, padding not removed yet."""
    logger.debug("called")
    number_sub_secrets = int.from_bytes(packages[0][0:1], BYTE_O)
    threshold = int.from_bytes(packages[0][1:2], BYTE_O)
    sub_shares = [[] for i in range(number_sub_secrets)]

    for i in range(0, threshold):  # only iterate over minimum number
        share_id, share = int.from_bytes(packages[i][2:3], byteorder=BYTE_O), \
                          packages[i][3:len(packages[i])]

        for j in range(0, number_sub_secrets):  # reorder shares according to secret id
            next_length, buffer = int.from_bytes(share[0:1], byteorder=BYTE_O), share[1:]
            sub_shares[j].append((share_id + 1, buffer[0:next_length]))
            share = buffer[next_length:]

    _secret = b''
    for i in range(0, len(sub_shares)):
        _secret += Shamir.combine(sub_shares[i], ssss=False)  # recombine sub-secrets and concentrate

    return unpad(_secret)


# ~~~~~~~~~~~~ Password Share Encryption ~~~~~~~~~~~~

# auxiliary for readability

def pwd_encrypt_stos(password: str, plaintext: str) -> str:
    return pwd_encrypt(password, plaintext.encode(ENCODING)).decode(ENCODING)


def pwd_encrypt_btos(password: str, plaintext: bytes) -> str:
    return pwd_encrypt(password, plaintext).decode(ENCODING)


def pwd_decrypt_stos(password: str, plaintext: str):
    return pwd_decrypt(password, plaintext.encode(ENCODING)).decode(ENCODING)


def pwd_decrypt_stob(password: str, plaintext: str):
    return pwd_decrypt(password, plaintext.encode(ENCODING))


def pwd_encrypt_name(password: str, plain_name: str):
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    cipher = AES.new(key, AES.MODE_ECB)
    data_padded = pad(plain_name.encode(ENCODING))
    ciphertext = cipher.encrypt(data_padded)
    return ciphertext.decode(ENCODING)


def pwd_decrypt_name(password: str, encrypted_name: str):
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = cipher.decrypt(encrypted_name.encode(ENCODING))
    name = unpad(padded_data)
    return name.decode(ENCODING)


def pwd_encrypt(password: str, data: bytes) -> bytes:
    logging.debug("called")
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    data_padded = pad(data)
    iv = urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b''.join([iv, cipher.encrypt(data_padded)])


def pwd_decrypt(password: str, data: bytes) -> bytes:
    logging.debug("called")
    key = SHA512.new(password.encode(ENCODING)).digest()[0:16]
    cipher = AES.new(key, AES.MODE_CBC, IV=data[0:16])
    return unpad(cipher.decrypt(data[16:]))


def encrypt_files(password: str, directory: str, files: List[str]) -> None:
    """Encrypts the files stored in the FILENAMES variable."""
    logging.debug("called")
    for filename in files:
        with open(os.path.join(directory, filename), "rb+") as fd:
            data = fd.read()
            encrypted_data = pwd_encrypt(password, data)
            fd.seek(0)
            fd.write(encrypted_data)
            fd.truncate()


def decrypt_files(password: str, directory: str, files: List[str]) -> None:
    """Decrypts the files stored in the FILENAMES variable."""
    logging.debug("called")
    for filename in files:
        with open(os.path.join(directory, filename), "rb+") as fd:
            encrypted_data = fd.read()
            data = pwd_decrypt(password, encrypted_data)
            fd.seek(0)
            fd.write(data)
            fd.truncate()




# ~~~~~~~~~~~~ Keys ~~~~~~~~~~~~
# Interfacing with nacl

def generate_keys() -> tuple:
    sk = PrivateKey.generate()
    return sk, sk.public_key

# ~~~~~~~~~~~~ Events ~~~~~~~~~~~~


def create_event(sub_event) -> any:
    """Creates an event from a sub_event and returns it in appropriate from."""
    content = {
        'messagekey': sub_event,
        'chat_id': 'secret',  # Todo fill with something that makes sense
        'timestampkey': 666  # Todo fill with actual timestamp
    }
    return content  # Todo str here or dict or json, cbor?!


def extract_sub_event(event) -> any:
    """Extracts sub_event from event."""
    #sub_event = sub_event.replace('\\', '\\\\')
    return event["messagekey"]


# ~~~~~~~~~~~~ BACNetCore ~~~~~~~~~~~~
# Interfacing functions here


def push_events(events: List[any]) -> None:
    if not rq_handler:
        raise SecretSharingError("No request handler for database connection.")

    for event in events:
        next_event = rq_handler.event_factory.next_event("chat/secret", event)
        rq_handler.db_connection.insert_event(next_event)
    return


def pull_events(feed_seq_tuples: List[Tuple[bytes, int]]) -> List[Tuple[any, bytes]]:
    if not rq_handler:
        raise SecretSharingError("No request handler for database connection.")

    event_list = []
    for tuples in feed_seq_tuples:
        feed_id, old_seq_no = tuples
        current_seq_no = rq_handler.db_connection.get_current_seq_no(feed_id) + 1
        for seq_no in range(old_seq_no, current_seq_no):
            event = rq_handler.db_connection.get_event(feed_id, seq_no)
            event_list.append((Event.Event.from_cbor(event).content.content[1], feed_id))

    return event_list


def current_sequence_number(feed_id: bytes) -> int:
    if not rq_handler:
        raise SecretSharingError("No request handler for database connection.")
    return rq_handler.db_connection.get_current_seq_no(feed_id)


def create_user(username: str) -> None:
    if not rq_handler:
        raise SecretSharingError("No request handler for database connection.")

    rq_handler.create_user(username)


def do_things_with_the_core():
    print(":,)")

