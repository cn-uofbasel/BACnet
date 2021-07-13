"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# BACnet imports
# import BACnetCore
# import BACnetTransport
import database_connector

import logging
import sys
from enum import IntEnum
from typing import List, Tuple

import bcrypt
from json import dumps
from BackEnd import core

from BackEnd import settings
from BackEnd.exceptions import \
    MappingError, SecretPackagingError, PasswordError, \
    SecretSharingError, StateEncryptedError, IncomingRequestException


# ~~~~~~~~~~~~ Logging ~~~~~~~~~~~~

def setup_logging(level):
    """Call from main!"""
    import logging.config
    _format = '%(msecs)dms %(name)s %(levelname)s line %(lineno)d %(funcName)s %(message)s'
    formatter = logging.Formatter(_format)
    logging.basicConfig(
        filename=settings.os.path.join(settings.DATA_DIR, "backend.log"),
        format=_format,
        filemode="w",
        datefmt='%H:%M:%S',
        level=level
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh)


logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
rq_handler = database_connector.RequestHandler.Instance()
ENCRYPTED_FILES = ["shareBuffer.json", "preferences.json", "contacts.json", "secrets.json"]
SPECIAL_CHARACTERS = ['.', ',', '-', '=', '[', '@', '_', '!', '#', '$', '%', '^', '&', '*',
                      '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':', ']']
ENCODING = core.ENCODING
MAP = "mapping"
NAME = "name"
THR = "threshold"
PARTS = "parts"
SIZE = "size"


# ~~~~~~~~~~~~ State Files  ~~~~~~~~~~~~
# State Files are keeping persistent information in json format.
pwd_gate = settings.State("pwd_gate.json", settings.DATA_DIR, {"encrypted": False, "pwd": None})  # stores password hash
STATE_ENCRYPTED = pwd_gate["encrypted"]

if not STATE_ENCRYPTED:
    preferences = settings.State("preferences", settings.DATA_DIR, {})      # stores preferences for ui
    shareBuffer = settings.State("shareBuffer", settings.DATA_DIR, {})      # stores shares in between send/recv
    contacts = settings.State("contacts", settings.DATA_DIR, {})            # stores contact information/pubkeys
    secrets = settings.State("secrets", settings.DATA_DIR, {MAP: {}})       # stores secret-specific information,
    keys = settings.State("master", settings.KEY_DIR, core.generate_keys())  # stores secret-specific information,
else:
    raise StateEncryptedError("State is encrypted")  # Todo catch this and prompt password for application


def save_state():
    """Saves all states to file."""
    logger.debug("called")
    pwd_gate.save()
    preferences.save()
    shareBuffer.save()
    contacts.save()
    secrets.save()


# ~~~~~~~~~~~~ Secret-Mapping  ~~~~~~~~~~~~
# Secrets are mapped to an integer in [0...255]. This information is later included
# in plaintext within packages to determine to which secret a package belongs.


def new_mapping(name: str) -> int:
    """Generates a new one byte mapping for a secret."""
    logger.debug("called")
    if name in secrets[MAP]:
        raise MappingError("Duplicate Mapping.", (name,))
    for mapping in range(0, 255):
        if mapping not in secrets[MAP]:
            secrets[MAP][mapping] = name
            secrets[MAP][name] = mapping
            secrets.save()
            return mapping
    raise MappingError("Mappings exhausted.", (name,))


def clear_mapping(name: str) -> None:
    """Clears a mapping for a secret."""
    logger.debug("called")
    if name not in secrets[MAP]:
        raise MappingError("Trying to clear non-existing mapping.", (name,))
    mapping = secrets[MAP][name]
    del secrets[MAP][name]
    del secrets[MAP][mapping]


def get_mapping(package: bytes) -> int:
    """Reads mapping from a package."""
    logger.debug("called")
    return int.from_bytes(package[0:1], byteorder="little", signed=False)


# ~~~~~~~~~~~~ Shamir Interface  ~~~~~~~~~~~~
# All UI interfacing functions for the shamir secret sharing algorithm.

class S_SIZE(IntEnum):
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


def split_secret_into_share_packages(name: str, secret: bytes, number_of_packages: int, threshold=None):
    """Interface function to split a secret into share packages. Gives back the packages and a
    dictionary containing useful information about the secret"""
    logger.debug("Called with secret: {}".format(secret))

    if not threshold:
        logger.debug("default threshold")
        threshold = number_of_packages

    mapping = new_mapping(name)

    size = s_size(secret)

    if size == S_SIZE.SMALL:
        packages = core.split_small_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.NORMAL:
        packages = core.split_normal_secret_into_share_packages(mapping, secret, threshold, number_of_packages)
    elif size == S_SIZE.LARGE:
        packages = core.split_large_secret_into_share_packages(mapping, secret, number_of_packages, threshold=threshold)
    else:
        raise SecretPackagingError("The secret given has a size that is not supported, "
                                   "it should be between 0 and 4.096 Kb.", secret)

    secret_info_package = {
        NAME: name,
        MAP: mapping,
        SIZE: size.value,
        PARTS: number_of_packages,
        THR: threshold
    }

    logger.debug("secret_info_package created: \n {}".format(dumps(secret_info_package, indent=4)))
    logger.debug("packages created:\n{}".format('\n'.join('\t{}: {}'.format(*k) for k in enumerate(packages))))

    return packages, secret_info_package


def recover_secret_from_packages(packages: List[bytes], secret_info_package: dict) -> bytes:
    """Interface function to recover a secret from packages."""
    logger.debug("called")

    size = S_SIZE(secret_info_package[SIZE])
    if size == S_SIZE.SMALL:
        secret = core.unpad(core.recover_normal_secret(packages))
    elif size == S_SIZE.NORMAL:
        secret = core.recover_normal_secret(packages)
    elif size == S_SIZE.LARGE:
        secret = core.recover_large_secret(packages)
    else:
        raise SecretPackagingError("The secret given has a size that is not supported, "
                                   "it should be between 0 and 4.096 Kb.", b'')

    logger.debug("Secret Reconstructed: {}".format(secret))

    return secret


# ~~~~~~~~~~~~ Share Buffering  ~~~~~~~~~~~~
# Shares that are not immediately send or restored are buffered in the shareBuffer

def secret_can_be_recovered(name: str) -> bool:
    logger.debug("called")
    """True if a buffer contains equal or more shares than its threshold."""
    if name in shareBuffer:
        return len(shareBuffer[name]) >= secrets[name][THR]
    elif name in secrets:
        return False
    else:
        raise MappingError("No such secret exists.", (name,))


def push_packages_into_share_buffer(packages: List[bytes], secret_info_package: dict) -> None:
    logger.debug("called")
    name = secret_info_package[NAME]
    secrets[name] = secret_info_package
    shareBuffer[name] = [package.decode(ENCODING) for package in packages]


def push_package_into_share_buffer(package: bytes) -> None:
    logger.debug("called")
    name = secrets[MAP][get_mapping(package)]
    if name in shareBuffer:
        if package not in shareBuffer[name]:
            shareBuffer[name].append(package.decode(ENCODING))
        else:
            # If this happens somebody is trying to send or read the same package twice.
            raise SecretPackagingError("Duplicate package in shareBuffer, package: {}, "
                                       "secret_info_package: {}".format(package, secrets[name]), b'')
    else:
        shareBuffer[name] = [package.decode(ENCODING)]


def get_packages_from_share_buffer(name: str) -> Tuple[List[bytes], dict]:
    logger.debug("called with {}".format(name))
    try:
        return [package.encode(ENCODING) for package in shareBuffer[name]], secrets[name]
    except KeyError:
        raise MappingError("No shareBuffer was mapped to this name: {}.".format(name), (name,))


# ~~~~~~~~~~~~ Sub Event Processing  ~~~~~~~~~~~~
# Packages need to be processed and new sub-events created.

def process_incoming_event(sub_event_tpl: Tuple[core.E_TYPE, bytes, str]):
    """Processes incoming secret sharing sub-events. If the return value is not null it is a reply package to be send to the
    source of the incoming message."""
    t, package, name = sub_event_tpl
    if t == core.E_TYPE.SHARE:
        process_incoming_share(name, package)
    elif t == core.E_TYPE.REQUEST:
        raise IncomingRequestException("Incoming request.", name)
        # catch, get name via exception.get() and handle separately
    elif t == core.E_TYPE.REPLY:
        process_incoming_reply(package)
    else:
        raise SecretSharingError("Event Type couldn't be evaluated.")


def process_incoming_reply(package):
    """Called if a package returns to the client."""
    push_package_into_share_buffer(package)


def process_incoming_share(name: str, package: bytes) -> None:
    """Called to store a package for a peer."""
    if name in shareBuffer:
        raise SecretSharingError("Either one in a million name collision or duplicate incoming share.")
    shareBuffer[name] = package.decode(ENCODING)


def process_incoming_request(private_key: bytes, feed_id: bytes, name: str) -> str:
    """Creates a reply package with the requested share."""
    try:
        package = shareBuffer[name]
    except KeyError:
        raise SecretSharingError("Someone requested a share you don't have.")
    return core.create_sub_event(core.E_TYPE.REPLY, sk=private_key, pk=feed_id, name=name, shard=package)


def process_outgoing_event(t: core.E_TYPE, private_key: bytes, feed_id: bytes, password: str, name: str, package=None) -> str:
    if t == core.E_TYPE.SHARE:
        return process_outgoing_share(private_key, feed_id, name, password, package)
    elif t == core.E_TYPE.REQUEST:
        return process_outgoing_request(private_key, feed_id, name, password)
    elif t == core.E_TYPE.REPLY:
        return process_outgoing_reply(private_key, feed_id, name, package)
    else:
        raise SecretSharingError("Event Type couldn't be evaluated.")


def process_outgoing_share(private_key: bytes, feed_id: bytes, name: str, password: str, package: bytes):
    """Called to create a sub-event for sending a share."""
    if not package:
        raise SecretSharingError("No package given.")
    return core.create_sub_event(t=core.E_TYPE.SHARE, sk=private_key, pk=feed_id, name=name, shard=package, password=password)


def process_outgoing_request(private_key: bytes, feed_id: bytes, name: str, password: str):
    """Called to create an event calling for a package return."""
    return core.create_sub_event(t=core.E_TYPE.REQUEST, sk=private_key, pk=feed_id, name=name, password=password)


def process_outgoing_reply(private_key: bytes, feed_id: bytes, name: str, package: bytes):
    if not package:
        raise SecretSharingError("No package given.")
    return core.create_sub_event(t=core.E_TYPE.REPLY, sk=private_key, pk=feed_id, name=name, shard=package)


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

def create_new_contact(contact: str, feed_id: bytes):
    if contact in contacts:
        raise MappingError("Contact already exists.", (contact, feed_id))
    contacts[contact] = feed_id.decode(ENCODING)
    contacts[feed_id.decode(ENCODING)] = contact


def clear_contact(contact: str, feed_id: bytes):
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, feed_id))
    del contacts[contact]
    del contacts[feed_id.decode(ENCODING)]


def get_contact_feed_id(contact: str):
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, b''))
    return contacts[contact].encode(ENCODING)


def get_contact_name(feed_id: bytes):
    if feed_id.decode(ENCODING) not in contacts:
        raise MappingError("Contact doesn't exists.", ('', feed_id))
    return contacts[feed_id.decode(ENCODING)]

def get_all_contact_dict():
    contacts.load()
    contact_dict = contacts
    contacts.save()
    return contact_dict


# ~~~~~~~~~~~~ Passwords  ~~~~~~~~~~~~

def check_password(password: str):
    if pwd_gate["pwd"]:
        return bcrypt.checkpw(password.encode(ENCODING), pwd_gate["pwd"].encode(ENCODING))
    else:
        raise PasswordError("No password set.", password)


def pw_is_viable(password):
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
        raise SecretSharingError("No password gate given.")
    if pwd_gate["pwd"]:
        if not bcrypt.checkpw(old_password.encode(ENCODING), pwd_gate["pwd"].encode(ENCODING)):
            raise PasswordError("Old password doesn't match.", old_password)
        else:
            if not pw_is_viable(password):
                raise PasswordError("Password not complex enough.", password)
            pwd_gate["pwd"] = password
    else:
        if not pw_is_viable(password):
            raise PasswordError("Password not complex enough.", password)
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
