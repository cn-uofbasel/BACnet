import os
import lib.crypto
from ast import literal_eval

from BackEnd import settings


class KeyManager:
    """Class for managing keys in the SecretSharing API. Should streamline key
    generation and keyfile management."""
    def __init__(self):
        self.preferences = settings.Preferences()

    def get_key_files(self) -> dict:
        """To retrieve a mapping of keyfile names to their paths."""
        directory: os.path = self.preferences.get_preferences()["keys"]
        list_dir = os.listdir(directory)
        return dict(zip(
            list_dir,
            [os.path.join(directory, key_file) for key_file in list_dir]
        ))

    def __write_key_file(self, ed25519: lib.crypto.ED25519, filename: str) -> None:
        """Creates or overwrites key-files. Private access."""
        with open(os.path.join(self.preferences.get_preferences()["keys"], filename), "wt") as fd:
            fd.write(ed25519.as_string())

    @staticmethod
    def get_keys(filename: str, key_files: dict) -> tuple:
        """Returns contents of a key-file."""
        with open(key_files[filename], "rt") as fd:
            pack: dict = literal_eval(fd.read())
            _secret = bytes.fromhex(pack.get("private"))
            _pubkey = bytes.fromhex(pack.get("public"))
            return _secret, _pubkey

    def generate_key_pair(self, filename, private_key=None) -> tuple:
        """Generates new key-pairs. If key-argument filename is not specified it will use the default
        class member. Returns tuple of bytes (private, public) keys and saves it in the current folder"""
        if private_key:
            ed25519 = lib.crypto.ED25519(privateKey=private_key)
        else:
            ed25519 = lib.crypto.ED25519()
            ed25519.create()
        self.__write_key_file(ed25519, filename)
        return ed25519.get_private_key(), ed25519.get_public_key()