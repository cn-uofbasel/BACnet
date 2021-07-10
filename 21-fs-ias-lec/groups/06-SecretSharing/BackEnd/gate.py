"""All sensitive stored information can be password encrypted."""

from os import path
from BackEnd import settings
from BackEnd.exceptions import PasswordError
import bcrypt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from os import urandom

ENCODING = 'ISO-8859-1'
SALT_STRENGTH = 4
SPECIAL = ['.', ',', '-', '=', '[', '@', '_', '!', '#', '$', '%', '^', '&', '*',
           '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':', ']']

pw_gate = settings.State("password_gate.json", settings.DATA_DIR, {})


def change_password(p_password, p_password_prev=None):
    if "pw" in pw_gate and bcrypt.checkpw(p_password_prev, pw_gate["pw"]) or "pw" not in pw_gate:
        if check_password_strength_okay(p_password):
            pw_gate["pw"] = bcrypt.hashpw(p_password.encode(ENCODING), bcrypt.gensalt(SALT_STRENGTH)).decode(ENCODING)
        else:
            raise PasswordError("Password not good, misses spice. At least 1 upper-case, "
                                "1 lower-case, one digit, one special character.", p_password)
    else:
        raise PasswordError("Sorry.", p_password)


def check_password_strength_okay(p_password):
    return not any([
        not p_password,
        len(p_password) < 8,
        not any(map(lambda x: x.isdigit(), p_password)),
        not any(map(lambda x: x.isupper(), p_password)),
        not any(map(lambda x: x.islower(), p_password)),
        not any(map(lambda x: x in SPECIAL, p_password)),
    ])


def encrypt(p_password):
    if bcrypt.checkpw(p_password.encode(ENCODING), pw_gate["pw"].encode(ENCODING)):
        key = SHA256.new(p_password.encode(ENCODING)).digest()
        iv = urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pw_gate["iv"] = iv.decode(ENCODING)
        pw_gate.save()

        __encrypt_file("shareBuffer.json", cipher)
        __encrypt_file("preferences.json", cipher)
        __encrypt_file("contacts.json", cipher)
        __encrypt_file("secrets.json", cipher)
    else:
        raise PasswordError("Password is incorrect.", p_password)


def __encrypt_file(filename, cipher):
    with open(path.join(settings.DATA_DIR, filename), "rb+") as fd:
        data = fd.read()

        padding = AES.block_size - len(data) % AES.block_size
        data += bytes([padding]) * padding
        data = cipher.encrypt(data)

        fd.seek(0)
        fd.write(data)
        fd.truncate()


def decrypt(p_password):
    if bcrypt.checkpw(p_password.encode(ENCODING), pw_gate["pw"].encode(ENCODING)):
        key = SHA256.new(p_password.encode(ENCODING)).digest()
        iv = pw_gate["iv"].encode(ENCODING)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        __decrypt_file("shareBuffer.json", cipher)
        __decrypt_file("preferences.json", cipher)
        __decrypt_file("contacts.json", cipher)
        __decrypt_file("secrets.json", cipher)
    else:
        raise PasswordError("Password is incorrect.", p_password)


def __decrypt_file(filename, cipher):
    with open(path.join(settings.DATA_DIR, filename), "rb+") as fd:
        data = fd.read()

        data = cipher.decrypt(data)

        data = data[:-data[-1]]

        fd.seek(0)
        fd.write(data)
        fd.truncate()


def check_password(p_password):
    try:
        return bcrypt.checkpw(p_password.encode(ENCODING), pw_gate["pw"].encode(ENCODING))
    except KeyError:
        raise PasswordError("No password has been set.", "")
