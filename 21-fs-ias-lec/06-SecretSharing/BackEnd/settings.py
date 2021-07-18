import os
import json
import logging

logger = logging.getLogger()

# global folders
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
KEY_DIR: os.path = os.path.join(DATA_DIR, "keys")
if not os.path.isdir(KEY_DIR):
    os.mkdir(KEY_DIR)
# autogenerate database folder
RECOVERY_DIR: os.path = os.path.join(DATA_DIR, "recovery")
if not os.path.isdir(RECOVERY_DIR):
    os.mkdir(RECOVERY_DIR)


class State(dict):
    """Persistent mini database interface class in the SecretSharing API implemented with json."""
    def __init__(self, filename: str, directory: os.path, default: dict):
        logger.debug(
            "Creating {} in directory {} with default content: \n{}"
            .format(filename, directory, json.dumps(default, indent=4))
        )
        super().__init__()
        self.abs_path = os.path.join(directory, filename)
        if not os.path.isfile(self.abs_path):
            self.update(default)
            with open(self.abs_path, "w") as fd:
                fd.write(json.dumps(default, indent=4))
                fd.close()
        else:
            self.load()

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