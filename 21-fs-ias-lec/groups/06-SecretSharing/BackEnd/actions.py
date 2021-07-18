"""
The actions script is the interface between the UI and the BackEnd of the SecretSharing project.
"""

# BACnet imports
# import BACnetCore
# import BACnetTransport

import logging
import atexit
from enum import IntEnum
from threading import Thread
from time import sleep
from typing import List, Tuple
from nacl.exceptions import CryptoError
import bcrypt

from BackEnd import core

from BackEnd import settings
from BackEnd.exceptions import *
from secrets import compare_digest

# ~~~~~~~~~~~~ Logging ~~~~~~~~~~~~

logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
SPECIAL_CHARACTERS = ['.', ',', '-', '=', '[', '@', '_', '!', '#', '$', '%', '^', '&', '*',
                      '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':', ']']
ENCODING = core.ENCODING
MAP = "mapping"
NAME = "name"
THR = "threshold"
PARTS = "parts"
SIZE = "size"


# ~~~~~~~~~~~~ Master Password ~~~~~~~~~~~~

master_password = None  # session password


# ~~~~~~~~~~~~ State Files  ~~~~~~~~~~~~
# State Files are keeping persistent information in json format.
pwd_gate = settings.State("pwd_gate", settings.DATA_DIR, {"encrypted": False, "pwd": ""})  # stores password hash
STATE_ENCRYPTED = pwd_gate["encrypted"]

if not STATE_ENCRYPTED:
    preferences = settings.State("preferences", settings.DATA_DIR, {"auto_save": 60})      # stores preferences for ui
    shareBuffer = settings.State("shareBuffer", settings.DATA_DIR, {})      # stores shares in between send/recv
    contacts = settings.State("contacts", settings.DATA_DIR, {})            # stores contact information/pubkeys
    secrets = settings.State("secrets", settings.DATA_DIR, {})       # stores secret-specific information,
    # keys = settings.State("master", settings.KEY_DIR, core.generate_keys())  # stores secret-specific information,
else:
    # catch and exit application
    raise StateEncryptedException("State is encrypted")


def save_state():
    """Saves all states to file."""
    logger.debug("called")
    pwd_gate.save()
    preferences.save()
    shareBuffer.save()
    contacts.save()
    secrets.save()


# ~~~~~~~~~~~~ Auto Save ~~~~~~~~~~~~

class SaverDaemon(Thread):
    def __init__(self):
        super().__init__()
        self.isDaemon()

    def run(self):
        while True:
            sleep(1)
            auto_save = preferences.get("auto_save")
            sleep(1)
            save_state()
            sleep(auto_save - 2)


def set_auto_save_duration(seconds: int):
    if 10 > seconds:
        raise SecretSharingException("Please keep it cool. 10 at minimum.")
    preferences["auto_save"] = seconds


def run_auto_save_for_session():
    SaverDaemon().start()


def exit_handler():
    """Saves state at exit."""
    logger.debug("Application exit caught.")
    save_state()


# register exit handler
atexit.register(exit_handler)


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


def split_secret_into_share_packages(name: str, secret: bytes, threshold: int, number_of_packages: int, holders: List[str]):
    """Interface function to split a secret into share packages. Gives back the packages and a
    dictionary containing useful information about the secret"""
    logger.debug("Called with secret: {}".format(secret))

    if not threshold:
        logger.debug("default threshold")
        threshold = number_of_packages

    size = s_size(secret)

    if size == S_SIZE.SMALL:
        packages = core.split_small_secret_into_share_packages(secret, threshold, number_of_packages)
    elif size == S_SIZE.NORMAL:
        packages = core.split_normal_secret_into_share_packages(secret, threshold, number_of_packages)
    elif size == S_SIZE.LARGE:
        packages = core.split_large_secret_into_share_packages(secret, threshold, number_of_packages)
    else:
        raise SecretPackagingError("The secret given has a size that is not supported, "
                                   "it should be between 0 and 4.096 Kb.", secret)

    add_information(
        name,
        {
            "Holders": holders,
            SIZE: size.value,
            PARTS: number_of_packages,
            THR: threshold
        }
    )

    logger.debug("packages created:\n{}".format('\n'.join('\t{}: {}'.format(*k) for k in enumerate(packages))))

    return packages


def recover_secret_from_packages(name: str, packages: List[bytes]) -> bytes:
    """Interface function to recover a secret from packages."""
    logger.debug("called")

    if name not in secrets:
        raise SecretSharingError("No information to recover the secret, try from scratch.")

    size = S_SIZE(secrets.get(name).get(SIZE))
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

# ~~~~~~~~~~~~ Secret Information  ~~~~~~~~~~~~
# per name contains a dictionary with size, number of pck and threshold


def add_information_from_scratch(name: str, threshold=None, number_of_packages=None, holders=None, size=None):
    if name in secrets:
        raise SecretSharingError("Secret with same name already exists.")

    if not size:
        logger.warning("This will create problems, please recover from scratch as soon as you have your shares.")
    else:
        size = S_SIZE(size).value

    secrets[name] = {
        NAME: name,
        THR: threshold,
        PARTS: number_of_packages,
        SIZE: size,
        "Holders": holders
    }


def add_information(name: str, info: dict) -> None:
    if name in secrets:
        raise SecretSharingError("Secret with same name already exists.")
    secrets[name] = info


def get_information(name: str) -> dict:
    if name in secrets:
        raise SecretSharingError("Secret with same name does not exists.")
    return secrets.get(name)


def clear_information(name: str) -> None:
    if name not in secrets:
        raise SecretSharingError("Secret with same name does not exists.")
    del secrets[name]


# ~~~~~~~~~~~~ Share Buffering  ~~~~~~~~~~~~
# Shares that are not immediately send or restored are buffered in the shareBuffer

def secret_can_be_recovered(name: str, recover_from_scratch=False) -> bool:
    logger.debug("called")
    """True if a buffer contains equal or more shares than its threshold."""
    if name in shareBuffer:
        if recover_from_scratch:
            return secret_can_be_recovered_from_scratch(name)
        else:
            return len(shareBuffer[name]) >= secrets[name][THR]
    elif name in secrets:
        return False
    else:
        raise MappingError("No such secret exists.", (name,))


def secret_can_be_recovered_from_scratch(name: str):
    # Todo If Method is called from secret_can_be_recovered with the right parameter: If a secret is recovered
    #  here it raises a RecoveryFromScratchException that can be caught and contains the recovered secret.
    logger.warning("Recovery from scratch can produce unexpected results.")
    packages = get_packages_from_share_buffer(name)
    try:
        secret = core.recover_normal_secret(packages)
        raise RecoveryFromScratchException("Normal secret was recovered, it could still be padded!", secret)
    except RecoveryFromScratchException:
        raise
    except Exception:
        logger.debug("Failed to recover as 16 byte secret.")
        pass
    try:
        secret = core.recover_large_secret(packages)
        raise RecoveryFromScratchException("Large secret was recovered.", secret)
    except RecoveryFromScratchException:
        raise
    except Exception:
        logger.debug("Failed to recover as large secret.")
        return False


def push_packages_into_share_buffer(name: str, packages: List[bytes]) -> None:
    logger.debug("called")
    if name in shareBuffer:
        raise SecretSharingError("ShareBuffer already exists. Please add packages individually.")
    shareBuffer[name] = [package.decode(ENCODING) for package in packages]


def push_package_into_share_buffer(name: str, package: bytes) -> None:
    logger.debug("called")
    if name in shareBuffer:
        if package not in shareBuffer[name]:
            shareBuffer[name].append(package.decode(ENCODING))
        else:
            raise SecretPackagingError("Duplicate package in shareBuffer, name: {}".format(name), package)
    else:
        shareBuffer[name] = [package.decode(ENCODING)]


def get_packages_from_share_buffer(name: str) -> List[bytes]:
    logger.debug("called with {}".format(name))
    try:
        return [package.encode(ENCODING) for package in shareBuffer[name]]
    except KeyError:
        raise MappingError("No shareBuffer was mapped to this name: {}.".format(name), (name,))


def delete_packages_from_share_buffer(name: str) -> None:
    logger.debug("called with {}".format(name))
    if name not in shareBuffer:
        raise SecretSharingError("BufferEntry with same name does not exists.")
    del shareBuffer[name]


# ~~~~~~~~~~~~ Sub Event Processing  ~~~~~~~~~~~~
# Packages need to be processed and new sub-events created.

def process_incoming_sub_event(sub_event_tpl: Tuple[core.E_TYPE, bytes, str]):
    """Processes incoming secret sharing sub-events.
    Parameters
    ----------
    sub_event_tpl: Tuple[core.E_TYPE, bytes, str]
    A tuple of three; type, package and name. Created by
    """
    t, package, name = sub_event_tpl
    if t == core.E_TYPE.SHARE:
        process_incoming_share(name, package)
    elif t == core.E_TYPE.REQUEST:
        raise IncomingRequestException("Incoming request.", name)
    elif t == core.E_TYPE.REPLY:
        process_incoming_reply(name, package)
    else:
        raise SecretSharingError("Event Type couldn't be evaluated.")


def process_incoming_reply(name, package):
    """Called if a package returns to the client."""
    push_package_into_share_buffer(name, package)


def process_incoming_share(name: str, package: bytes) -> None:
    """Called to store a package for a peer."""
    push_package_into_share_buffer(name, package)

def process_incoming_request(private_key: bytes, feed_id: bytes, name: str) -> str:
    """Creates a reply package with the requested share."""
    try:
        package = shareBuffer[name]
    except KeyError:
        raise SecretSharingError("Someone requested a non-existent share.")
    return core.create_sub_event(core.E_TYPE.REPLY, sk=private_key, pk=feed_id, name=name, shard=package)


def process_outgoing_sub_event(t: core.E_TYPE, private_key: bytes, feed_id: bytes, name: str,  password=None, package=None) -> str:
    """Processes outgoing events.
    Parameters
    ----------
    t : E_TYPE
    Event type.
    private_key : bytes
    Secret key of sending client.
    feed_id: bytes
    Public key of receiving client.
    password: str
    Password used for nested encryption.
    name: str
    Name of the secret associated with this message.
    package: bytes
    Share package as created by the application.
    """

    if not password and master_password:
        password = master_password
    elif not password:
        raise PasswordError("No password or master-password provided", "")

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
    """Called to create an event replying with a package."""
    if not package:
        raise SecretSharingError("No package given.")
    return core.create_sub_event(t=core.E_TYPE.REPLY, sk=private_key, pk=feed_id, name=name, shard=package)


# ~~~~~~~~~~~~ Event Processing  ~~~~~~~~~~~~

def handle_incoming_events(events: List[any], private_key: bytes, feed_id: bytes, password: str):
    """Handles incoming raw events."""
    for event in events:
        try:
            handle_incoming_event(event, private_key, feed_id, password)
        except SubEventDecryptionException:
            logger.warning("Skipped event with decryption exception.")
            pass


def handle_incoming_event(event: any, private_key: bytes, feed_id: bytes, password: str):
    """Handles incoming raw event."""
    sub_event_tpl = core.decrypt_sub_event(event, private_key, feed_id, password)
    try:
        process_incoming_sub_event(sub_event_tpl)
    except IncomingRequestException as e:
        handle_event_request_exception(e, private_key, feed_id, password)


def handle_event_request_exception(e: IncomingRequestException, private_key: bytes, feed_id: bytes, password: str):
    """Handles a request by auto-pushing reply."""
    name = e.get()
    if name in secrets:  # prevents people from requesting your packages.
        raise PackageStealException("Somebody tried to grab packages.", feed_id)
    elif name not in shareBuffer:
        raise SecretSharingError("Somebody requests packages you don't have: {}".format(name))

    packages = get_packages_from_share_buffer(name)

    reply_sub_events = [
        process_outgoing_sub_event(core.E_TYPE.REPLY, private_key, feed_id, name, password, package) for package in packages
    ]

    handle_outgoing_sub_events(reply_sub_events)


def handle_outgoing_sub_events(sub_events: List[any]):
    """Pushes events into the database."""
    events = [core.create_event(sub_event) for sub_event in sub_events]
    core.push_events(events)


def handle_new_events(private_key, password=None):
    """Handles new events coming from the database."""
    if not password and master_password:
        password = master_password
    elif not password:
        raise PasswordError("No password or master-password provided", "")

    # get all feed ids and seq_no from contacts
    feed_seq_tuples = []

    for contact in contacts:
        feed_id = get_contact_feed_id(contact)
        current_feed_seq = core.current_sequence_number(feed_id)
        if contacts[contact]["seq_no"] != current_feed_seq:
            #we already update the sequence number if necessary
            #update_seq_no(contact, current_feed_seq + 1)
            pass
        feed_seq_tuples.append((feed_id, contacts[contact]["seq_no"]))

    event_tuples = core.pull_events(feed_seq_tuples)
    for event, feed_id in event_tuples:
        try:
            handle_incoming_event(core.extract_sub_event(event), private_key, feed_id, password)
        except CryptoError:
            # means the event wasn't meant for you
            pass
        except SecretSharingError as sse:
            logger.debug(sse.msg())

    for contact in contacts:
        current_feed_seq = core.current_sequence_number(feed_id)
        if contacts[contact]["seq_no"] != current_feed_seq:
            update_seq_no(contact, current_feed_seq + 1)

def attemptReconstruction(secret_name):
    if secrets.get(secret_name).get("size") is not None:
        if secret_can_be_recovered(secret_name, False):
            secret = recover_secret_from_packages(secret_name, get_packages_from_share_buffer(secret_name))
            raise RecoverySuccessException(f"The secret \"{secret_name}\" has been recoverd", secret, secret_name)
    else:
        try:
            secret_can_be_recovered(secret_name, True)
        except RecoveryFromScratchException as rse:
            raise RecoverySuccessException("", rse.secret, secret_name, rse.message)

# ~~~~~~~~~~~~ Contact Interface  ~~~~~~~~~~~~
# To process identifying information from contacts over BacNet

def create_new_contact(contact: str, feed_id: bytes) -> None:
    if contact in contacts:
        raise MappingError("Contact already exists.", (contact, feed_id))
    contacts[contact] = {'feed_id': feed_id.decode(ENCODING),
                         'seq_no': 1}


def clear_contact(contact: str) -> None:
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, b''))
    del contacts[contact]


def get_contact_feed_id(contact: str) -> bytes:
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, b''))
    return contacts.get(contact).get("feed_id").encode(ENCODING)


def get_seq_no(contact: str) -> int:
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, b''))
    return contacts[contact]["seq_no"]


def update_seq_no(contact: str, seq_no: int) -> None:
    if contact not in contacts:
        raise MappingError("Contact doesn't exists.", (contact, b''))
    contacts[contact]["seq_no"] = seq_no


def get_contact_name(feed_id: bytes) -> str:
    for contact in contacts:
        if contacts.get(contact).get("feed_id").encode(ENCODING) == feed_id:
            return contact
    raise MappingError("Contact doesn't exists.", ('', feed_id))


def get_all_contacts_dict() -> dict:
    contact_dict = {}
    for contact in contacts:
        contact_dict[contact] = contacts.get(contact).get("feed_id").encode(ENCODING).hex()
    return contact_dict

# ~~~~~~~~~~~~ Passwords  ~~~~~~~~~~~~
# Todo subject to change


def check_password(password: str) -> bool:
    if pwd_gate["pwd"]:
        return bcrypt.checkpw(password.encode(ENCODING), pwd_gate.get("pwd").encode(ENCODING))
    else:
        raise PasswordError("No password set.", password)


def pw_is_viable(password: str) -> bool:
    """Returns true if password is 8 """
    logging.debug("called")
    # TODO remove early return, added for testing purposes
    return True
    # if not any([
    #     not password,
    #     len(password) < 8,
    #     not any(map(lambda x: x.isdigit(), password)),
    #     not any(map(lambda x: x.isupper(), password)),
    #     not any(map(lambda x: x.islower(), password)),
    #     not any(map(lambda x: x in SPECIAL_CHARACTERS, password)),
    # ]):
    #     return True
    # else:
    #     raise PasswordError("Password should contain at least a digit, an uppercase, a lower case, and special "
    #                         "characters and should be at least 8 digits in total.", password)


def change_password(password: str, old_password=None) -> None:
    """Changes the current password, needs old password if there is one.
    Raises PasswordError if not successful."""
    logging.debug("called")
    if not pwd_gate:
        raise SecretSharingError("No password gate given.")
    if pwd_gate["pwd"]:
        if not bcrypt.checkpw(old_password.encode(ENCODING), pwd_gate.get("pwd").encode(ENCODING)):
            raise PasswordError("Old password doesn't match.", old_password)
        else:
            if not pw_is_viable(password):
                raise PasswordError("Password not complex enough.", password)
            pwd_gate["pwd"] = bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt()).decode(ENCODING)
    else:
        if not pw_is_viable(password):
            raise PasswordError("Password not complex enough.", password)
        pwd_gate["pwd"] = bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt()).decode(ENCODING)


# ~~~~~~~~~~~~ LOGIN  ~~~~~~~~~~~~

def create_user(username: str, password: str, password_repeat: str) -> None:
    if not core.rq_handler:
        raise SecretSharingError("No request handler for database connection.")
    first_login(password, password_repeat)
    core.create_user(username)


def first_login(password: str, password_repeat: str) -> None:
    if all(first_login_aux(password, password_repeat)):
        change_password(password)
        global master_password
        master_password = password
    else:
        raise PasswordError("Please enter a viable combination.", password)


def first_login_aux(password: str, password_repeat: str) -> [bool]:
    """Returns if entries are viable."""
    return [
        pw_is_viable(password),
        compare_digest(password_repeat, password)
    ]


def login(password: str) -> None:
    if not pwd_gate.get("pwd"):
        raise PasswordError("No password set for the application.", password)
    if check_password(password):
        global master_password
        master_password = password
    else:
        raise PasswordError("Password incorrect.", password)


def user_exists() -> bool:
    if not pwd_gate.get("pwd"):
        return False
    else:
        return True