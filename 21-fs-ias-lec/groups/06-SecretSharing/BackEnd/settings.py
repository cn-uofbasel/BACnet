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
