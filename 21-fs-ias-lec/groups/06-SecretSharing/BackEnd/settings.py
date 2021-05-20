import os
import json


class State:
    """Persistent database interface class in the SecretSharing API implemented with json."""
    def __init__(self, filename: str, directory: os.path,  default: dict):
        self.abs_path = os.path.join(directory, filename)
        if not os.path.isfile(self.abs_path):
            with open(self.abs_path, "w") as fd:
                fd.write(json.dumps(default, indent=4))
                fd.close()

    def get_content(self) -> dict:
        """Returns database as dictionary."""
        with open(self.abs_path, "r") as fd:
            state: dict = json.loads(fd.read())
            fd.close()
            return state

    def set_content(self, content: dict) -> None:
        """Overwrites database."""
        with open(self.abs_path, "w") as fd:
            fd.write(json.dumps(content, indent=4))
            fd.close()


class Preferences(State):
    """Interface for a Json database of persistent preferences."""
    __PATH: os.path = os.path.join(os.path.dirname(__file__), "..")  # filepath
    __ID: str = "preferences.json"  # filename
    __DEFAULT: dict = {  # default content
        "keys": os.path.join(__PATH, "keys"),
        "db": os.path.join(__PATH, "database")
    }

    def __init__(self):
        # autogenerate keys folder
        default_keys: os.path = os.path.join(self.__PATH, "keys")
        if not os.path.isdir(default_keys):
            os.mkdir(default_keys)
        # autogenerate database folder
        default_database: os.path = os.path.join(self.__PATH, "database")
        if not os.path.isdir(default_database):
            os.mkdir(default_database)
        super(Preferences, self).__init__(self.__ID, self.__PATH, self.__DEFAULT)


class Contacts(State):
    """Mini database for keeping track of who you meet, what their keys are, just normal things
    really, so you don't have to type in 19 public keys by hand."""
    __PATH: os.path = os.path.join(os.path.dirname(__file__), "..")  # filepath
    __ID: str = "contacts.json"  # filename
    __DEFAULT: dict = {  # default content
        "joe biden": {"public": b'123', "favorite_food": b'pizza'},
        "nedib eoj": {"public": b'321', "favorite_food": b'azzip'}
    }

    def __init__(self):
        super(Contacts, self).__init__(self.__ID, self.__PATH, self.__DEFAULT)


# -------------- TEMPLATE --------------

class Data(State):
    """Interface for a Json database of data."""
    __PATH: os.path = os.path.join(os.path.dirname(__file__), "..")  # filepath
    __ID: str = "data.json"  # filename
    __DEFAULT: dict = {  # default content
    }

    def __init__(self):
        super(Data, self).__init__(self.__ID, self.__PATH, self.__DEFAULT)