"""
The actions script is the interface between the UI and the BackEnd of the Secret sharing Projekt.
"""

# general imports

import os

# BACnet imports

# import BACnetCore
# import BACnetTransport

# internal imports

from typing import List, Tuple
from BackEnd import keys, settings, core

# third party imports

from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Cipher import AES


preferences = settings.Preferences()

# CORE INTERFACING FUNCTIONS


def setup_environment():  # core stuff
    database_path: os.path = preferences.get_content()["db"]
    # storage = BACnetCore.Storage.SQLiteConnector(os.path.join(database_path, "db"))
    # myChannel = BACnetTransport.Paths(?)
    # ...
    # ...
    pass

    # ...
    # ...

# SHAMIR INTERFACING FUNCTIONS


def split_secret_into_shares(secret: bytes, threshold: int, number: int) -> List[Tuple[int, bytes]]:
    return Shamir.split(threshold, number, secret, ssss=False)


def encrypt_shares_with_keys(shares: List[Tuple[int, bytes]], public_keys: List[bytes]) -> List[bytes]:
    """Encrypts a given number of shares with a given number of public keys."""
    if len(shares) != len(public_keys):
        raise ValueError("Not as many keys as shares.")
    encrypted_shares = []
    for share, public_key in shares, public_keys:
        # maybe use another encryption method, or RSA (what about the IV?)
        cipher = AES.new(public_key, AES.MODE_ECB)
        encrypted_shares.append(cipher.encrypt(share[1], public_key))
    return encrypted_shares


def recover_secret(shares: List[bytes], temp_private_key: bytes):
    """Takes a list of encrypted shares and decrypts with the temporary private key."""
    cipher = AES.new(temp_private_key, AES.MODE_ECB)
    return Shamir.combine(list(zip(
        [idx for idx in range(0, len(shares))],
        [cipher.decrypt(share) for share in shares])),
        ssss=False
    )

    # ...
    # ...


# OTHER UI INTERFACING FUNCTIONS
# examples ...

# alternatively to instantiating contacts each time
# it could be a global variable or passed to the functions


contacts = settings.Contacts()
shareBuffer = settings.ShareBuffer()

# Storing Shares


def buff_share(share: bytes, share_buffer_id: str) -> None:
    # if someone returns a share to us we need a place to store it
    # until we have the threshold number of shares to restore the secret
    share_buffer = shareBuffer.get_content()
    if share_buffer.keys().__contains__(share_buffer_id):
        share_buffer[share_buffer_id].append(share)
    else:
        share_buffer[share_buffer_id] = list(share,)


def get_share_buffer(share_buffer_id: str) -> Tuple[int, List[bytes]]:
    buffer = shareBuffer.get_content()[share_buffer_id]
    return len(buffer), buffer  # returns the length too to check number of shares

# ...

# Contact Information


def edit_contact(contact: str, public_key, feed, radius):
    content = contacts.get_content()
    content[contact] = dict(
        {
            "public": public_key,
            "feed": feed,
            "radius": radius
        }
    )
    contacts.set_content(content)


def get_list_of_all_friends(self):
    return contacts.get_content().keys()


def get_contact(contact):
    contact_public_key = contacts.get_content()[contact]["public"]
    contact_feed = contacts.get_content()[contact]["feed"]
    # ...

# ...
# ...
