"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# BACnet imports
# import BACnetCore
# import BACnetTransport

# Internal
from BackEnd import keys
from BackEnd import settings
from BackEnd import core
from BackEnd import gate
from enum import Enum
#only temporary or find better spot
import database_connector
import json
# the rq_handler can create events with its eventFactory and write to the database
# with the db_connection
rq_handler = database_connector.RequestHandler.Instance()

# Other
from typing import List
from bcrypt import checkpw, hashpw, gensalt
from time import gmtime, strftime

# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
ENCODING = 'ISO-8859-1'
MAP = "mapping"

# ~~~~~~~~~~~~ State Files  ~~~~~~~~~~~~
# State Files are keeping persistent information in json format.
preferences = settings.Preferences()  # stores preferences for ui
shareBuffer = settings.ShareBuffer()  # stores shares
contacts = settings.Contacts()  # stores contact information
secrets = settings.Secrets()  # stores secret-specific information,


def save_state():
    gate.encryption.save()
    preferences.save()
    shareBuffer.save()
    contacts.save()
    secrets.save()


def load_state():
    gate.encryption.load()
    preferences.load()
    shareBuffer.load()
    contacts.load()
    secrets.load()


# ~~~~~~~~~~~~ Secret-Mapping  ~~~~~~~~~~~~
# Secrets are mapped to an integer in [0...255]. This information is later included
# in plaintext within packages to determine to which secret a package belongs.


def new_mapping(id_string: str) -> int:
    if id_string in secrets[MAP]:
        raise ValueError("Duplicate Mapping.")
    for mapping in range(0, 255):
        if mapping not in secrets[MAP]:
            secrets[MAP][mapping] = id_string
            secrets[MAP][id_string] = mapping
            secrets.save()
            return mapping
    raise ValueError("Mappings exhausted.")


def clear_mapping(id_string: str) -> None:
    if id_string not in secrets[MAP]:
        raise ValueError("Trying to clear non-existing mapping.")
    mapping = secrets[MAP][id_string]
    del secrets[MAP][id_string]
    del secrets[MAP][mapping]


def get_mapping(package: bytes) -> int:
    return int.from_bytes(package[0:1], byteorder="little", signed=False)


# ~~~~~~~~~~~~ Shamir Interface  ~~~~~~~~~~~~

class S_SIZE(Enum):
    SMALL = 1,
    NORMAL = 2,
    LARGE = 3


def s_size(secret: bytes):
    sz = len(secret)
    if 0 < sz < 16:
        return S_SIZE.SMALL
    elif sz == 16:
        return S_SIZE.NORMAL
    elif 0 < sz < 4096:
        return S_SIZE.LARGE
    else:
        return None


def split_secret_into_share_packages(id_string: str, secret: bytes, number_of_packages: int, password: str, threshold=None):
    """Interface function to split a secret into share packages. Gives back the packages and a dictionary containing useful
    information about the secret"""
    if not threshold:
        threshold = number_of_packages
    size = s_size(secret)
    mapping = new_mapping(id_string)

    if size == S_SIZE.SMALL:
        packages = core.split_small_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.NORMAL:
        packages = core.split_normal_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.LARGE:
        packages = core.split_large_secret_into_share_packages(mapping, secret, number_of_packages)
        threshold = number_of_packages
    else:
        raise ValueError("The secret given has a size that is not supported, it should be between 0 and 4.096 Mb.")

    sinfo = {
        "name": id_string,
        MAP: mapping,
        "size": size.value,
        "bytes": len(secret),
        "parts": number_of_packages,
        "pw": hashpw(password.encode(ENCODING), gensalt(12)).decode(ENCODING),  # password hash
        "threshold": threshold,
        "holders": []  # who has shares?
    }

    return packages, sinfo


def recover_secret_from_packages(packages: List[bytes], sinfo: dict) -> bytes:
    """Interface function to recover a secret from packages."""
    size = sinfo["size"]
    length = sinfo["bytes"]

    if size == S_SIZE.SMALL:
        secret = core.recover_normal_secret(packages)  # it's padded
    elif size == S_SIZE.NORMAL:
        secret = core.recover_normal_secret(packages)
    elif size == S_SIZE.LARGE:
        secret = core.recover_large_secret(packages)
    else:
        raise ValueError("The secret given has a size that is not supported, it should be between 0 and 4.096 Mb.")

    if len(secret) > length:
        secret = core.unpad(secret)

    return secret


# ~~~~~~~~~~~~ Share Buffering  ~~~~~~~~~~~~

def secret_can_be_resolved(id_string: int) -> bool:
    """True if a buffer contains equal or more shares than its threshold."""
    try:
        return len(shareBuffer[id_string]) >= secrets[id_string]["threshold"]
    except KeyError:
        print("No such secret exists.")
        return False


def push_packages_into_share_buffer(packages: List[bytes], sinfo: dict):
    id_string = sinfo["name"]
    secrets[id_string] = sinfo
    shareBuffer[id_string] = [package.decode('ISO-8859-1') for package in packages]


def push_package_into_share_buffer(package: bytes, sinfo: dict):
    id_string = sinfo["name"]
    secrets[id_string] = sinfo
    if id_string in shareBuffer:
        if not package in shareBuffer[id_string]:
            shareBuffer[id_string].append(package)
        else:
            raise ValueError("Duplicate package in shareBuffer, package: {}, sinfo: {}".format(package, sinfo))
    else:
        shareBuffer[id_string] = [package.decode('ISO-8859-1')]


def get_packages_from_share_buffer(id_string: str) -> list:
    try:
        return [package.encode('ISO-8859-1') for package in shareBuffer[id_string]]
    except KeyError:
        raise ValueError("No such buffer exists.")


# ~~~~~~~~~~~~ Sub Event Processing  ~~~~~~~~~~~~

def process_incoming(einfo):
    t, package, password = einfo
    # Todo Need internal ID for Contacts and their feed-ids to do this. !!!
    if t == core.E_TYPE.SHARE:
        process_package_keep_request("CONTACT_ID", package=package, password_hash=password)
    elif t == core.E_TYPE.REQUEST:
        process_package_return_request("CONTACT_ID", "THEIR PUBKEY", password, get_mapping(package))
    elif t == core.E_TYPE.REPLY:
        process_package_return(package)


def process_package_depart(contact, key, password_hash, package) -> str:
    # Get information on the secret the package belongs to.
    mapping = get_mapping(package)
    name = secrets[MAP][mapping]
    sinfo = secrets[name]

    # update the information
    sinfo["holder"].append(contact)
    sinfo["pw"] = password_hash
    secrets[name] = sinfo

    # return the subevent to be sent
    return core.sub_event(core.E_TYPE.SHARE, receivers_pubkey=key, shard=package, password=password_hash)


def process_package_return(package):
    id_string = secrets[MAP][get_mapping(package)]
    push_package_into_share_buffer(package, secrets[id_string])


def process_sending_return_request(key, password):
    return core.sub_event(core.E_TYPE.REQUEST, receivers_pubkey=key, password=password)


def process_package_keep_request(contact, password_hash, package) -> None:
    # every user has a unique secret-to-number mapping on their end,
    # we need only know an identifying attribute about the contact
    # and that number to uniquely store it

    their_mapping = get_mapping(package)
    mapping = new_mapping(contact + their_mapping)
    sinfo = {
        MAP, mapping,
        "password", password_hash
    }
    secrets[contact + their_mapping] = sinfo
    shareBuffer[mapping] = package.decode(ENCODING)


def process_package_return_request(contact, key, password: str, their_mapping) -> str:
    sinfo = secrets[contact + their_mapping]
    if not checkpw(password.encode(ENCODING), sinfo["pw"].encode(ENCODING)):
        raise ValueError("Password incorrect.")
    package = shareBuffer[sinfo[MAP]].encode('ISO-8859-1')

    # clear data
    clear_mapping(contact + their_mapping)
    del secrets[contact + their_mapping]
    del shareBuffer[sinfo[MAP]]

    return core.sub_event(core.E_TYPE.REPLY, key, package)

# ~~~~~~~~~~~~ Event Processing  ~~~~~~~~~~~~


def create_event(sub_event):
    content = {
        'content': sub_event,
        '-': '-',
        'timestamp': strftime("%Y-%m-%d %H:%M:%S", gmtime())
    }
    event = rq_handler.event_factory.next_event("chat/secret", content)
    rq_handler.db_connection.insert_event(event)


#~~~~~~~~~~~ Testing for database (temporary) ~~~~~~~ ~~~~~~~


def create_user(username):
    rq_handler.create_user(username)

def logged_in():
    return rq_handler.logged_in

def append_test_message():

    content = {
        'messagekey': json.dumps({'test': "this is a test dict"}),
        'chat_id': "fuck you",
        'timestampkey': 11}
    event = rq_handler.event_factory.next_event("chat/secret", content)
    rq_handler.db_connection.insert_event(event)

# ~~~~~~~~~~~~ Contact Interface  ~~~~~~~~~~~~
# To process identifying information from contacts over BacNet

def create_new_contact(contact, key):
    if contact in contacts:
        raise ValueError("Contact already exists.")
    contacts[contact] = key


def get_contact_key(contact):
    return contacts[contact]


# ~~~~~~~~~~~~ Encryption Interface  ~~~~~~~~~~~~

def set_password(password, previous_password=None):
    gate.change_password(password, previous_password)


def encrypt_state(password):
    gate.encrypt(password)


def decrypt_state(password):
    gate.decrypt(password)