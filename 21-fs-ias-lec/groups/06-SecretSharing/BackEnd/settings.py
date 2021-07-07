import os
import json

# global folders
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
KEY_DIR: os.path = os.path.join(DATA_DIR, "keys")
if not os.path.isdir(KEY_DIR):
    os.mkdir(KEY_DIR)
# autogenerate database folder
DATABASE_DIR: os.path = os.path.join(DATA_DIR, "database")
if not os.path.isdir(DATABASE_DIR):
    os.mkdir(DATABASE_DIR)


class State(dict):
    """Persistent mini database interface class in the SecretSharing API implemented with json."""
    def __init__(self, filename: str, directory: os.path, default: dict):
        super().__init__()
        self.abs_path = os.path.join(directory, filename)
        self.update(default)
        if not os.path.isfile(self.abs_path):
            with open(self.abs_path, "w") as fd:
                fd.write(json.dumps(default, indent=4))
                fd.close()

    def load(self) -> None:
        with open(self.abs_path, "r") as fd:
            state: dict = json.loads(fd.read())
            fd.close()
            self.clear()
            self.update(state)

    def save(self) -> None:
        with open(self.abs_path, "w") as fd:
            fd.write(json.dumps(dict(self), indent=4))
            fd.close()


class Preferences(State):
    """Interface for a mini database of preferences."""
    __ID: str = "preferences.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Preferences, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


class Contacts(State):
    """Mini database for keeping track of who you meet, what their keys are, just normal things
    really, so you don't have to type in 19 public keys by hand."""
    __ID: str = "contacts.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Contacts, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


class Secrets(State):
    __ID: str = "secrets.json"  # filename
    __DEFAULT: dict = {  # default content
        "mapping": {}
    }

    def __init__(self):
        super(Secrets, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


class Encryption(State):
    __ID: str = "encryption.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Encryption, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


class ShareBuffer(State):
    """Keeps shares fresh while reconstructing a secret."""
    __ID: str = "shareBuffer.json"
    __DEFAULT: dict = {
    }

    def __init__(self):
        super(ShareBuffer, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


# -------------- TEMPLATE --------------

class Data(State):
    """Interface for a Json database of data."""
    __ID: str = "data.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Data, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)