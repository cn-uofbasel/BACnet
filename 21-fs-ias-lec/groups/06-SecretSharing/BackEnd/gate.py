"""All sensitive stored information can be password encrypted."""

from os import path
from BackEnd import settings
from BackEnd import core
from BackEnd.exceptions import PasswordError
import bcrypt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from os import urandom
from enum import Enum


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
    def encrypt_secret(password: str, secret: bytes) -> tuple:
        key = SHA256.new(password.encode(ENCODING)).digest()

        padding = AES.block_size - len(secret) % AES.block_size
        secret += bytes([padding]) * padding

        print(secret)

        iv = urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_secret = cipher.encrypt(secret)

        return encrypted_secret, iv

    @staticmethod
    def decrypt_secret(password, encrypted_secret, iv) -> bytes:
        key = SHA256.new(password.encode(ENCODING)).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_secret)
        return decrypted[:-decrypted[-1]]

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