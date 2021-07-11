"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# BACnet imports
# import BACnetCore
# import BACnetTransport

import logging
import sys
from enum import Enum
from typing import List

import bcrypt
from json import dumps
from BackEnd import core

from BackEnd import settings
from BackEnd.exceptions import MappingError, SecretPackagingError, PasswordError, SecretSharingError, StateEncryptedError


# ~~~~~~~~~~~~ Logging ~~~~~~~~~~~~

def setup_logging():
    import logging.config
    _format = '%(msecs)dms %(name)s %(levelname)s line %(lineno)d %(funcName)s %(message)s'
    formatter = logging.Formatter(_format)
    logging.basicConfig(
        filename=settings.os.path.join(settings.DATA_DIR, "backend.log"),
        format=_format,
        filemode="w",
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh)


logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
ENCRYPTED_FILES = ["shareBuffer.json", "preferences.json", "contacts.json", "secrets.json"]
SPECIAL_CHARACTERS = ['.', ',', '-', '=', '[', '@', '_', '!', '#', '$', '%', '^', '&', '*',
                      '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':', ']']
ENCODING = core.ENCODING
MAP = "mapping"


# ~~~~~~~~~~~~ State Files  ~~~~~~~~~~~~
# State Files are keeping persistent information in json format.
pwd_gate = settings.State("pwd_gate.json", settings.DATA_DIR, {"encrypted": False, "pwd": None})  # stores password hash
STATE_ENCRYPTED = pwd_gate["encrypted"]

if not STATE_ENCRYPTED:
    preferences = settings.State("preferences.json", settings.DATA_DIR, {})  # stores preferences for ui
    shareBuffer = settings.State("shareBuffer.json", settings.DATA_DIR, {})   # stores shares in between send/recv
    contacts = settings.State("contacts.json", settings.DATA_DIR, {})   # stores contact information/pubkeys
    secrets = settings.State("secrets.json", settings.DATA_DIR, {MAP: {}})   # stores secret-specific information,
else:
    raise StateEncryptedError("State is encrypted")  # Todo catch this and prompt password for application


def save_state():
    logger.debug("called")
    pwd_gate.save()
    preferences.save()
    shareBuffer.save()
    contacts.save()
    secrets.save()


# def load_state():  # not really necessary done by State class
#     logger.debug("called")
#     pwd_gate.load()
#     preferences.load()
#     shareBuffer.load()
#     contacts.load()
#     secrets.load()


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
    """Interface function to split a secret into share packages. Gives back the packages and a
    dictionary containing useful information about the secret"""
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

    secret_info_package = {
        "name": id_string,
        MAP: mapping,
        "size": size.value,
        "parts": number_of_packages,
        "threshold": threshold,
        "holders": []  # who has shares?
    }

    logger.debug("secret_info_package created: \n {}".format(dumps(secret_info_package, indent=4)))
    logger.debug("packages created:\n{}".format('\n'.join('\t{}: {}'.format(*k) for k in enumerate(packages))))

    return packages, secret_info_package


def recover_secret_from_packages(packages: List[bytes], secret_info_package: dict) -> bytes:
    """Interface function to recover a secret from packages."""
    logger.debug("called")

    size = secret_info_package["size"]

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


def push_packages_into_share_buffer(packages: List[bytes], secret_info_package: dict) -> None:
    logger.debug("called")
    id_string = secret_info_package["name"]
    secrets[id_string] = secret_info_package
    shareBuffer[id_string] = [package.decode(ENCODING) for package in packages]


def push_package_into_share_buffer(package: bytes, secret_info_package: dict) -> None:
    logger.debug("called")
    id_string = secret_info_package["name"]
    secrets[id_string] = secret_info_package
    if id_string in shareBuffer:
        if not package in shareBuffer[id_string]:
            shareBuffer[id_string].append(package)
        else:
            # If this happens somebody is trying to send or read the same package twice.
            raise SecretPackagingError("Duplicate package in shareBuffer, package: {}, "
                                       "secret_info_package: {}".format(package, secret_info_package), b'')
    else:
        shareBuffer[id_string] = [package.decode(ENCODING)]


def get_packages_from_share_buffer(id_string: str) -> List[bytes]:
    logger.debug("called with {}".format(id_string))
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
    return core.create_sub_event(core.E_TYPE.SHARE, receivers_pubkey=key, shard=package, password=password_hash)


def process_package_return(package):
    id_string = secrets[MAP][get_mapping(package)]
    push_package_into_share_buffer(package, secrets[id_string])


def process_sending_return_request(key, password):
    return core.create_sub_event(core.E_TYPE.REQUEST, receivers_pubkey=key, password=password)


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
    if not bcrypt.checkpw(password.encode(ENCODING), sinfo["pw"].encode(ENCODING)):
        raise PasswordError("Password incorrect.", password)
    package = shareBuffer[sinfo[MAP]].encode(ENCODING)

    # clear data
    clear_mapping(contact + their_mapping)
    del secrets[contact + their_mapping]
    del shareBuffer[sinfo[MAP]]

    return core.create_sub_event(core.E_TYPE.REPLY, key, package)

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


# ~~~~~~~~~~~~ Passwords  ~~~~~~~~~~~~

def check_password(password: str):
    if pwd_gate["pwd"]:
        return bcrypt.checkpw(password.encode(ENCODING), pwd_gate["pwd"].encode(ENCODING))
    else:
        raise PasswordError("No password set.", password)


def pw_viable(password):
    """Returns true if the password checks against standard complexity."""
    logging.debug("called")
    return not any([
        not password,
        len(password) < 8,
        not any(map(lambda x: x.isdigit(), password)),
        not any(map(lambda x: x.isupper(), password)),
        not any(map(lambda x: x.islower(), password)),
        not any(map(lambda x: x in SPECIAL_CHARACTERS, password)),
    ])


def change_password(password: str, old_password=None):
    """Changes the current password, needs old password if there is one."""
    logging.debug("called")
    if not pwd_gate:
        raise PasswordError("No password gate given.", password)
    if pwd_gate["pwd"]:
        if not bcrypt.checkpw(old_password.encode(ENCODING), pwd_gate["pwd"].encode(ENCODING)):
            raise PasswordError("Old password doesn't match.", old_password)
        else:
            pwd_gate["pwd"] = password
    else:
        pwd_gate["pwd"] = bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt())


def encrypt_files(password: str) -> None:
    """Encrypts the files stored in the FILENAMES variable."""
    logging.debug("called")
    if not ENCRYPTED_FILES or not settings.DATA_DIR:
        raise SecretSharingError("No filenames or no directory given to encrypt_files.")
    key = core.SHA512.new(password.encode(ENCODING)).digest()
    for filename in ENCRYPTED_FILES:
        with open(settings.os.path.join(settings.DATA_DIR, filename), "rb+") as fd:
            iv = core.urandom(16)
            cipher = core.AES.new(key, core.AES.MODE_CBC, iv)
            data = fd.read()
            data = core.pad(data)
            data = b''.join([iv, cipher.encrypt(data)])
            fd.seek(0)
            fd.write(data)
            fd.truncate()


def decrypt_files(password: str) -> None:
    """Decrypts the files stored in the FILENAMES variable."""
    logging.debug("called")
    if not ENCRYPTED_FILES or not settings.DATA_DIR:
        raise SecretSharingError("No filenames or no directory given to decrypt_files.")
    key = core.SHA512.new(password.encode(ENCODING)).digest()
    for filename in ENCRYPTED_FILES:
        with open(settings.os.path.join(settings.DATA_DIR, filename), "rb+") as fd:
            data = fd.read()
            cipher = core.AES.new(key, core.AES.MODE_CBC, data[0:16])
            data = cipher.decrypt(data[16:])
            data = core.unpad(data)
            fd.seek(0)
            fd.write(data)
            fd.truncate()
