"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# BACnet imports
# import BACnetCore
# import BACnetTransport

import logging
from enum import Enum
# Other
from typing import List

from bcrypt import checkpw
from json import dumps

from BackEnd import core
from BackEnd import gate
# Internal
from BackEnd import settings
from BackEnd.exceptions import MappingError, SecretPackagingError, PasswordError


# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
logger = logging.getLogger(__name__)
ENCODING = core.ENCODING
MAP = "mapping"

# ~~~~~~~~~~~~ State Files  ~~~~~~~~~~~~
# State Files are keeping persistent information in json format.
preferences = settings.State("preferences.json", settings.DATA_DIR, {})  # stores preferences for ui
shareBuffer = settings.State("shareBuffer.json", settings.DATA_DIR, {})   # stores shares
contacts = settings.State("contacts.json", settings.DATA_DIR, {})   # stores contact information
secrets = settings.State("secrets.json", settings.DATA_DIR, {MAP: {}})   # stores secret-specific information,


def save_state():
    logger.debug("called")
    gate.pw_gate.save()
    preferences.save()
    shareBuffer.save()
    contacts.save()
    secrets.save()


def load_state():
    logger.debug("called")
    gate.pw_gate.load()
    preferences.load()
    shareBuffer.load()
    contacts.load()
    secrets.load()


# ~~~~~~~~~~~~ Secret-Mapping  ~~~~~~~~~~~~
# Secrets are mapped to an integer in [0...255]. This information is later included
# in plaintext within packages to determine to which secret a package belongs.


def new_mapping(id_string: str) -> int:
    logger.debug("called")
    if id_string in secrets[MAP]:
        raise MappingError("Duplicate Mapping.", (id_string,))
    for mapping in range(0, 255):
        if mapping not in secrets[MAP]:
            secrets[MAP][mapping] = id_string
            secrets[MAP][id_string] = mapping
            secrets.save()
            return mapping
    raise MappingError("Mappings exhausted.", (id_string,))


def clear_mapping(id_string: str) -> None:
    logger.debug("called")
    if id_string not in secrets[MAP]:
        raise MappingError("Trying to clear non-existing mapping.", (id_string,))
    mapping = secrets[MAP][id_string]
    del secrets[MAP][id_string]
    del secrets[MAP][mapping]


def get_mapping(package: bytes) -> int:
    logger.debug("called")
    return int.from_bytes(package[0:1], byteorder="little", signed=False)


# ~~~~~~~~~~~~ Shamir Interface  ~~~~~~~~~~~~

class S_SIZE(Enum):
    SMALL = 1,
    NORMAL = 2,
    LARGE = 3


def s_size(secret: bytes):
    logger.debug("called")
    sz = len(secret)
    if 0 < sz < 16:
        return S_SIZE.SMALL
    elif sz == 16:
        return S_SIZE.NORMAL
    elif 0 < sz < 4096:
        return S_SIZE.LARGE
    else:
        return None


def split_secret_into_share_packages(id_string: str, secret: bytes, number_of_packages: int, threshold=None):
    """Interface function to split a secret into share packages. Gives back the packages and a dictionary containing useful
    information about the secret"""
    logger.debug("Called with secret: {}".format(secret))

    if not threshold:
        logger.debug("default threshold")
        threshold = number_of_packages

    mapping = new_mapping(id_string)

    size = s_size(secret)

    if size == S_SIZE.SMALL:
        packages = core.split_small_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.NORMAL:
        packages = core.split_normal_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.LARGE:
        packages = core.split_large_secret_into_share_packages(mapping, secret, number_of_packages, threshold=threshold)
    else:
        raise SecretPackagingError("The secret given has a size that is not supported, "
                                   "it should be between 0 and 4.096 Kb. (After Encryption)", secret)

    sinfo = {
        "name": id_string,
        MAP: mapping,
        "size": size.value,
        "parts": number_of_packages,
        "threshold": threshold,
        "holders": []  # who has shares?
    }

    logger.debug("sinfo created: \n {}".format(dumps(sinfo, indent=4)))

    logger.debug("packages created:\n{}".format('\n'.join('\t{}: {}'.format(*k) for k in enumerate(packages))))

    return packages, sinfo


def recover_secret_from_packages(packages: List[bytes], sinfo: dict) -> bytes:
    """Interface function to recover a secret from packages."""
    logger.debug("called")

    size = sinfo["size"]

    if size == S_SIZE.SMALL.value:
        secret = core.unpad(core.recover_normal_secret(packages))
    elif size == S_SIZE.NORMAL.value:
        secret = core.recover_normal_secret(packages)
    elif size == S_SIZE.LARGE.value:
        secret = core.unpad(core.recover_large_secret(packages))

    else:
        raise SecretPackagingError("The secret given has a size that is not supported, "
                                   "it should be between 0 and 4.096 Kb.", b'')

    logger.debug("Secret Reconstructed: {}".format(secret))

    return secret


# ~~~~~~~~~~~~ Share Buffering  ~~~~~~~~~~~~

def secret_can_be_resolved(id_string: int) -> bool:
    logger.debug("called")
    """True if a buffer contains equal or more shares than its threshold."""
    try:
        return len(shareBuffer[id_string]) >= secrets[id_string]["threshold"]
    except KeyError:
        raise MappingError("No such secret exists.", (id_string,))


def push_packages_into_share_buffer(packages: List[bytes], sinfo: dict):
    logger.debug("called")
    id_string = sinfo["name"]
    secrets[id_string] = sinfo
    shareBuffer[id_string] = [package.decode(ENCODING) for package in packages]


def push_package_into_share_buffer(package: bytes, sinfo: dict):
    logger.debug("called")
    id_string = sinfo["name"]
    secrets[id_string] = sinfo
    if id_string in shareBuffer:
        if not package in shareBuffer[id_string]:
            shareBuffer[id_string].append(package)
        else:
            raise SecretPackagingError("Duplicate package in shareBuffer, package: {}, sinfo: {}".format(package, sinfo), b'')
    else:
        shareBuffer[id_string] = [package.decode(ENCODING)]


def get_packages_from_share_buffer(id_string: str) -> list:
    logger.debug("called")
    try:
        return [package.encode(ENCODING) for package in shareBuffer[id_string]]
    except KeyError:
        raise MappingError("No shareBuffer was mapped to this id_string: {}.".format(id_string), (id_string,))


# ~~~~~~~~~~~~ Sub Event Processing  ~~~~~~~~~~~~
# secret sharing messages are split into types: shares, requests and replies.
# {  <- event
    # {     <- sub_event
    #     pubkey encrypted(aes key)
    #     iv
    #     pubkey encrypted(
    #         {     <- message
    #             type      <- type of message
    #             package   <- optional share
    #         }
    #     )
    # }
# {

def process_incoming_message(einfo: tuple):
    """processes incoming tuples from a message, (type, package, password)"""
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
        raise PasswordError("Password incorrect.", password)
    package = shareBuffer[sinfo[MAP]].encode(ENCODING)

    # clear data
    clear_mapping(contact + their_mapping)
    del secrets[contact + their_mapping]
    del shareBuffer[sinfo[MAP]]

    return core.sub_event(core.E_TYPE.REPLY, key, package)

# ~~~~~~~~~~~~ Event Processing  ~~~~~~~~~~~~


# def create_event(sub_event):
#     content = {
#         'msg': sub_event,
#         '-': '-',
#         'timestamp': strftime("%Y-%m-%d %H:%M:%S", gmtime())
#     }
#     event = rq_handler.event_factory.next_event("chat/secret", content)
#     rq_handler.db_connection.insert_event(event)
#
#
# #~~~~~~~~~~~ Testing for database (temporary) ~~~~~~~ ~~~~~~~
#
#
# def create_user(username):
#     rq_handler.create_user(username)
#
# def logged_in():
#     return rq_handler.logged_in
#
# def append_test_message():
#
#     content = {
#         'messagekey': json.dumps({'test': "this is a test dict"}),
#         'chat_id': "fuck you",
#         'timestampkey': 11}
#     event = rq_handler.event_factory.next_event("chat/secret", content)
#     rq_handler.db_connection.insert_event(event)
#

# ~~~~~~~~~~~~ Contact Interface  ~~~~~~~~~~~~
# To process identifying information from contacts over BacNet

def create_new_contact(contact, key):
    if contact in contacts:
        raise MappingError("Contact already exists.", (contact, key))
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