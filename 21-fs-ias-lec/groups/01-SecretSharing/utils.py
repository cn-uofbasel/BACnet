# Imports

from lib import crypto
from ast import literal_eval
from os import listdir


class SSKeys:
    """Class for managing keys and keyfiles in the SecretSharing API."""
    def __init__(self, filename="standard_key"):
        self.filename = filename  # used when no key is specified
        self.files = {filename}
        self.scan_for_keys()

    def get_files(self) -> set:
        """Returns a set of strings, all names of key-files."""
        return self.files

    def scan_for_keys(self) -> None:
        """Searches the directory for key-files."""
        self.files = self.files.union(filter(lambda f: "key" in f.lower(), listdir()))

    def __write_key_file(self, ed25519: crypto.ED25519, filename=None) -> None:
        """Creates or overwrites key-files. Private."""
        if not filename:
            filename = self.filename
        else:
            self.files.add(filename)
        try:
            with open(filename, "wt") as file:
                file.write(ed25519.as_string())
        except IOError as error:
            print(error)

    def read_key_file(self, filename=None) -> tuple:
        """Returns contents of a key-file."""
        if not filename:
            filename = self.filename
        try:
            with open(filename, "rt") as file:
                pack: dict = literal_eval(file.read())
                _secret = bytes.fromhex(pack.get("private"))
                _pubkey = bytes.fromhex(pack.get("public"))
                return _secret, _pubkey
        except IOError as error:
            print(error)

    def generate_key_pair(self, filename=None) -> tuple:
        """Generates new key-pairs. If key-argument filename is not specified it will use the default
        class member. Returns tuple of bytes (private, public) keys and saves it in the current folder"""
        if filename and "key" not in filename.lower():
            raise ValueError("The filename should contain 'key'. Filename: {}".format(filename))
        ed25519 = crypto.ED25519()
        ed25519.create()
        self.__write_key_file(ed25519, filename=filename)
        return ed25519.get_private_key(), ed25519.get_public_key()


if __name__ == '__main__':

    # --- SSKeys ---
    # key generation:

    ss_keys = SSKeys()
    secret, pubkey = ss_keys.generate_key_pair()  # key is automatically stored as "standard_key"

    print("Generated secret: {}, Generated pubkey: {}".format(secret, pubkey))

    ss_keys.generate_key_pair(filename="onlyfans_key")  # generate a different one

    # key retrieval:

    # clear stack
    del secret
    del pubkey
    del ss_keys

    ss_keys = SSKeys()
    ss_keys.scan_for_keys()  # to retrieve keyfiles

    files = ss_keys.get_files()  # to get the filenames
    print("Loaded files: {}".format(files))

    for file in files:  # iterate over files
        secret, pubkey = ss_keys.read_key_file(file)
        print("Retrieved secret: {}, Retrieved_pubkey: {}".format(secret, pubkey))
