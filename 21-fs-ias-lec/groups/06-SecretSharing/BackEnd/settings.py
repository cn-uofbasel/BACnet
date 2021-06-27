import os
import json


# global data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# autogenerate
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)


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
        "keys": os.path.join(DATA_DIR, "keys"),  # maybe custom key directories/usb stick
        "db": os.path.join(DATA_DIR, "database")  # this folder will host the BACnet Core Database
    }

    def __init__(self):
        # autogenerate keys folder
        default_keys: os.path = os.path.join(DATA_DIR, "keys")
        if not os.path.isdir(default_keys):
            os.mkdir(default_keys)
        # autogenerate database folder
        default_database: os.path = os.path.join(DATA_DIR, "database")
        if not os.path.isdir(default_database):
            os.mkdir(default_database)
        super(Preferences, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


class Contacts(State):
    """Mini database for keeping track of who you meet, what their keys are, just normal things
    really, so you don't have to type in 19 public keys by hand."""
    __ID: str = "contacts.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Contacts, self).__init__(self.__ID, DATA_DIR, self.__DEFAULT)


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