"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# general imports

import os

# BACnet imports

# import BACnetCore
# import BACnetTransport

# internal imports

from typing import List, Tuple
from BackEnd import keys, settings, core
import threading

# third party imports

from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Cipher import AES
from base64 import b64encode


# CORE INTERFACING FUNCTIONS

def run_log_merge_ui():
    pass
# MAIN CONTROL FUNCTIONS

preferences = settings.Preferences()

def secret_to_buffered_shares(secret: bytes, id_string: str, threshold: int, number: int) -> None:
    """Sends a secret, split into its packaged shares into the shareBuffer."""
    shares = split_secret_into_shares(secret, threshold, number)
    new_sending_share_buffer(threshold, id_string)
    for share in shares:
        package_share(id_string, share[0], share[1])


def resolve_packages_to_secret(id_string):
    if secret_can_be_resolved(id_string):
        packages = resolve_share_buffer(id_string)
        shares = unpack_shares(packages)
        return recover_secret(shares)
    else:
        raise ValueError("Not enough data.")


def scrape_database():
    #...
    pass


# SHAMIR INTERFACING FUNCTIONS

def split_large_secret_into_share_packages(secret: bytes, number_packages: int):
    """Splits a secret of size 0 < s < 4.096 Mb into share packages. To keep it simple the threshold is equal to the
    number of shares created in total. """

    if not 0 < len(secret) < 4096:
        raise ValueError("Secret size is not supported, expected between 0 and 4.096 Mb.")

    secret_padded = core.pad(secret, 16)  # pad secret so len(s) % 16 == 0
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
            int.to_bytes(number_sub_secrets, byteorder="little", length=1),
            int.to_bytes(number_packages, byteorder="little", length=1),
            int.to_bytes(j, byteorder="little", length=1),
            b''.join(buffer[j])
        ]) for j in range(0, number_packages)
    ]


def recover_large_secret(packages):
    number_sub_secrets = int.from_bytes(packages[0][0:1], "little")
    number_packages = int.from_bytes(packages[0][1:2], "little")
    sub_shares = [[] for i in range(number_sub_secrets)]

    for i in range(0, number_packages):
        share_id, share = int.from_bytes(packages[i][2:3], byteorder="little"), \
                          packages[i][3:len(packages[i])]

        for j in range(0, number_sub_secrets):
            next_length, buffer = int.from_bytes(share[0:1], byteorder="little"), share[1:]
            sub_shares[j].append((share_id + 1, buffer[0:next_length]))
            share = buffer[next_length:]

    buffer = b''
    for i in range(0, len(sub_shares)):
        buffer += Shamir.combine(sub_shares[i], ssss=False)

    padding = int.from_bytes(buffer[len(buffer) - 2:len(buffer) - 1], byteorder="little")
    return buffer[0:-padding]


def split_secret_into_shares(secret: bytes, threshold: int, number: int) -> List[Tuple[int, bytes]]:
    if len(secret) == 16:
        raise ValueError("Currently only a secret of 16 bytes supported. Pad or shorten.")
    return Shamir.split(threshold, number, secret, ssss=False)


def recover_secret(shares: List[Tuple[int, bytes]]):
    """Takes a list of encrypted shares and decrypts with the temporary private key."""
    return Shamir.combine(shares, ssss=False)


# Share Buffering
shareBuffer = settings.ShareBuffer()


def secret_can_be_resolved(id_string: int) -> bool:
    """True if a buffer contains equal or more shares than its threshold."""
    shareBuffer.load()
    if not shareBuffer.keys().__contains__(id_string):
        raise ValueError("No such shared secret.")
    if shareBuffer[id_string]["io"] == "out":
        pass  # Todo
    threshold = int(shareBuffer[id_string]["threshold"])
    number_of_shares = len(shareBuffer[id_string]["packages"])
    return threshold <= number_of_shares


def __open_share_package(package) -> Tuple:
    """Opens up share and returns its contents decrypted."""
    raw_data, data = package, package.encode('ISO-8859-1')
    id, threshold, index, share = \
        int.from_bytes(data[0:1], byteorder="little"), \
        int.from_bytes(data[1:2], byteorder="little"), \
        int.from_bytes(data[2:3], byteorder="little"), \
        data[3:]
    return id, threshold, index, share, raw_data


def receive_contact_share(contact_id, package) -> None:
    """Receive a share to store for request.
    When we receive a share from a friend we need to know whom
    it belongs to and to which secret, in the case we store multiple secrets
    of the same person, the "contact_id + id" should be unique. All the sender
    needs to request is his id number of the secret and his name."""
    id, threshold, _, _, _ = __open_share_package(package)
    shareBuffer.load()
    id_string = contact_id + str(id)
    map_new_id(id_string)
    shareBuffer[id_string] = {
        "io": "keep",
        "threshold": str(threshold),
        "packages": [package]
    }
    shareBuffer.save()


def receive_returned_share(package) -> None:
    """Receives a returned share package. Takes the persistent Mappings and the information in the package to
    correspond the package to a buffer."""
    id, threshold, _, _, data = __open_share_package(package)
    shareBuffer.load()
    id_string = shareBuffer["mapping"][str(id)]
    if not shareBuffer.keys().__contains__(id_string):
        shareBuffer[id_string] = {
            "io": "in",
            "threshold": str(threshold),
            "packages": [package]
        }
    elif not shareBuffer[id_string]["packages"].__contains__(data):
        shareBuffer[id_string]["packages"].append(data)
    else:
        # ignoring duplicates rn smh
        print("Duplicate package.")
        return
    shareBuffer.save()


def new_sending_share_buffer(threshold: int, id_string: str) -> None:
    """Creates a new shareBuffer entry with the id_string as an id of the secret."""
    if threshold > 255:
        raise ValueError("Arguments should be 0 - 255, byte-sized.")
    shareBuffer.load()
    if shareBuffer.keys().__contains__(id_string):
        raise ValueError("Id already taken.")
    map_new_id(id_string)
    shareBuffer[id_string] = {
        "io": "out",
        "threshold": str(threshold),
        "packages": []
    }
    shareBuffer.save()


def resolve_share_buffer(id_string: str) -> list:
    shareBuffer.load()
    entry = shareBuffer[id_string]
    # Todo clear_mapping(id_string)
    return entry["packages"]


def package_share(id_string: str, index: int, share: bytes) -> None:
    """Packages a Share and pushes it into a corresponding shareBuffer entry.
    First byte signals secret, second threshold, third byte is the index of the
            share, rest is the share data."""
    shareBuffer.load()
    if not shareBuffer.keys().__contains__(id_string):
        raise ValueError("No such shared secret.")
    id = shareBuffer["mapping"][id_string]

    data = \
        bytearray(int.to_bytes(int(id), byteorder="little", signed=False, length=1)) + \
        bytearray(int.to_bytes(int(shareBuffer[id_string]["threshold"]), byteorder="little", signed=False, length=1)) + \
        bytearray(int.to_bytes(index, byteorder="little", signed=False, length=1)) + \
        bytearray(share)

    shareBuffer[id_string]["packages"].append(bytes(data).decode("ISO-8859-1"))
    shareBuffer.save()


def unpack_shares(packages) -> list:
    unpacked = []
    for package in packages:
        _, _, index, share, _ = __open_share_package(package)
        unpacked.append((index, share))
    return unpacked


def map_new_id(id_string) -> int:
    for i in range(0, 255):
        if not list(shareBuffer["mapping"].values()).__contains__(str(i)):
            shareBuffer["mapping"][str(i)] = id_string
            shareBuffer["mapping"][id_string] = str(i)
            shareBuffer.save()
            return i
    raise ValueError("Mappings exhausted.")


def insert_mapping(id_string, i):
    """DevOp function, shouldn't be used."""
    shareBuffer["mapping"][str(i)] = id_string
    shareBuffer["mapping"][id_string] = str(i)
    shareBuffer.save()


def clear_mapping(id_string) -> None:
    id = shareBuffer["mapping"][id_string]
    del shareBuffer["mapping"][id_string]
    del shareBuffer["mapping"][id]
# ...


# Contact Information
contacts = settings.Contacts()


def new_contact(contact, public_key, password_hash):
    contacts[contact] = {"pk": public_key, "pw": password_hash}


def get_list_of_all_friends():
    return contacts.keys()


# ...
# ...
