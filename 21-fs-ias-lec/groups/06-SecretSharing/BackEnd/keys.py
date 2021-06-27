import os
import lib.crypto
from ast import literal_eval
from abc import ABC, abstractmethod

from BackEnd import settings


class KeyManager(ABC):
    """AbstractClass for managing keys in the SecretSharing API. Its purpose is to integrate the crypto package
    and other key generating Modules into the API and its file systems."""
    def __init__(self):
        super().__init__()
        self.preferences = settings.Preferences()

    def get_files(self) -> dict:
        """To retrieve a mapping of keyfile names to their paths."""
        directory: os.path = self.preferences["keys"]
        list_dir = os.listdir(directory)
        return dict(zip(
            list_dir,
            [os.path.join(directory, key_file) for key_file in list_dir]
        ))

    @abstractmethod
    def get_keys(self, filename: str, files: dict):
        """Returns contents of a key-file."""
        pass

    @abstractmethod
    def write_file(self, filename: str, keys) -> None:
        """Creates or overwrites key-files. Private access."""
        pass

    @abstractmethod
    def generate(self, filename, private_key=None):
        """Generates new key-pairs."""
        pass


class ED25519Keys(KeyManager):
    __TYPE = "ed25519"

    def write_file(self, filename: str, ed25519: lib.crypto.ED25519) -> None:
        with open(os.path.join(self.preferences["keys"], filename), "wt") as fd:
            fd.write(ed25519.as_string())

    def get_keys(self, filename: str, files: dict):
        with open(files[filename], "rt") as fd:
            pack: dict = literal_eval(fd.read())
        if pack["type"] == self.__TYPE:
            return lib.crypto.ED25519(
                privateKey=bytes.fromhex(pack["private"])
            )
        else:
            print("Loaded key is of type " + pack["type"] + ", expected " + self.__TYPE)
            return None

    def generate(self, filename, private_key=None):
        ed25519 = lib.crypto.ED25519(private_key)
        ed25519.create()
        self.write_file(filename, ed25519)
        return ed25519


class HMACKeys(KeyManager):
    __TYPE = "hmac_sha256"

    def write_file(self, filename: str, hmac: lib.crypto.HMAC) -> None:
        with open(os.path.join(self.preferences["keys"], filename), "wt") as fd:
            fd.write(hmac.as_string())

    def get_keys(self, filename: str, files: dict):
        with open(files[filename], "rt") as fd:
            pack: dict = literal_eval(fd.read())
        if pack["type"] == self.__TYPE:
            return lib.crypto.HMAC(
                sharedSecret=bytes.fromhex(pack["private"]),
                fid=bytes.fromhex(pack["feed_id"])
            )
        else:
            print("Loaded key is of type " + pack["type"] + ", expected " + self.__TYPE)
            return None

    def generate(self, filename, shared_secret=None):
        hmac = lib.crypto.HMAC()
        hmac.create()
        self.write_file(filename, hmac)
        return hmac