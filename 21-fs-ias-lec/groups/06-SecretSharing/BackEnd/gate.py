"""All sensitive stored information can be password encrypted."""

from os import path
from BackEnd import settings
from BackEnd import core
from BackEnd.exceptions import PasswordError
import bcrypt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, SHA512
from os import urandom
from enum import Enum
import logging


# ~~~~~~~~~~~~ Constants  ~~~~~~~~~~~~
logger = logging.getLogger(__name__)
ENCODING = core.ENCODING
SALT_STRENGTH = 12
SPECIAL_CHARACTERS = ['.', ',', '-', '=', '[', '@', '_', '!', '#', '$', '%', '^', '&', '*',
                      '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':', ']']
FILENAMES = ["shareBuffer.json", "preferences.json", "contacts.json", "contacts.json", "secrets.json"]


class PW_TYPE(Enum):
    FILE = 1
    SECRET = 2


# pw_gate stores hashes of passwords used to encrypt files.
pw_gate = settings.State("password_gate.json", settings.DATA_DIR, {
    PW_TYPE.FILE.value: None,
    PW_TYPE.SECRET.value: None,
})


class Encryptor:
    """Handles password-encryption of files and secrets."""
    def __init__(self):
        pass

    @staticmethod
    def pw_viable(password):
        return not any([
            not password,
            len(password) < 8,
            not any(map(lambda x: x.isdigit(), password)),
            not any(map(lambda x: x.isupper(), password)),
            not any(map(lambda x: x.islower(), password)),
            not any(map(lambda x: x in SPECIAL_CHARACTERS, password)),
        ])

    @staticmethod
    def change_password(t: PW_TYPE, password, old_password=None):
        if pw_gate[t.value]:
            if not bcrypt.checkpw(old_password.encode(ENCODING), pw_gate[t.value].encode(ENCODING)):
                raise PasswordError("Old password doesn't match.", old_password)
            else:
                pw_gate[t.value] = password

    @staticmethod
    def encrypt_shard(password: str, shard: bytes) -> bytes:
        key = SHA256.new(password.encode(ENCODING)).digest()
        shard_padded = core.pad(shard)
        iv = urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return b''.join([iv, cipher.encrypt(shard_padded)])

    @staticmethod
    def decrypt_shard(password: str, encrypted_secret: bytes) -> bytes:
        key = SHA512.new(password.encode(ENCODING)).digest()
        cipher = AES.new(key, AES.MODE_CBC, encrypted_secret[0:16])
        return core.unpad(cipher.decrypt(encrypted_secret[16:]))

    @staticmethod
    def encrypt_files(password) -> bytes:
        key = SHA256.new(password.encode(ENCODING)).digest()
        iv = urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        for filename in FILENAMES:
            with open(path.join(settings.DATA_DIR, filename), "rb+") as fd:
                data = fd.read()
                padding = AES.block_size - len(data) % AES.block_size
                data += bytes([padding]) * padding
                data = cipher.encrypt(data)
                fd.seek(0)
                fd.write(data)
                fd.truncate()
        return iv

    @staticmethod
    def decrypt_files(password, iv) -> None:
        key = SHA256.new(password.encode(ENCODING)).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        for filename in FILENAMES:
            with open(path.join(settings.DATA_DIR, filename), "rb+") as fd:
                data = fd.read()
                data = cipher.decrypt(data)
                data = data[:-data[-1]]
                fd.seek(0)
                fd.write(data)
                fd.truncate()

    @staticmethod
    def get_cipher(password, iv=None):
        key = SHA256.new(password.encode(ENCODING)).digest()
        if not iv:
            iv = urandom(16)
            cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        else:
            cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        return cipher, iv