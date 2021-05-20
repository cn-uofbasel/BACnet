import os
import json


class Preferences:
    """Class to manage Preferences related to the SecretSharing API. Not thread safe.
    To change an entry retrieve the preferences by calling the get_preferences() method. To update the preferences pass the changed
    dictionary to set_preferences(preferences: dict).
    -  Handles preferences like a dictionary.
    -  To manipulate a dictionary type:
            dict["key"] = any   or
            dict["key"].foo(any)
    -  Preferences can be of any standard type, numbers, lists, sets, dictionaries, strings.
    -  To add paths to preferences use the os.path module.
    """
    __PREF: str = "preferences.json"  # json file with any persistent preferences
    __CWD: os.path = os.path.join(os.path.dirname(__file__), "..")
    __DEFAULT: dict = {
        "keys": os.path.join(__CWD, "keys"),
        # add default preferences here
    }

    def __init__(self):
        """To access the Preferences an instance has to be created. All instances
        point to the same preferences file privately, up one directory from this files
        location."""
        default_keys: os.path = os.path.join(self.__CWD, "keys")
        default_preferences: os.path = os.path.join(self.__CWD, self.__PREF)
        if not os.path.isdir(default_keys):
            os.mkdir(default_keys)
        if not os.path.isfile(default_preferences):
            # create preferences file and key folder
            with open(default_preferences, "w") as fd:
                fd.write(json.dumps(self.__DEFAULT))
                fd.close()

    def get_preferences(self) -> dict:
        """To retrieve the preferences file as a dictionary."""
        with open(os.path.join(self.__CWD, self.__PREF), "r") as fd:
            preferences: dict = json.loads(fd.read())
            fd.close()
            return preferences

    def set_preferences(self, preferences: dict) -> None:
        """To overwrite the preferences file with a dictionary."""
        with open(os.path.join(self.__CWD, self.__PREF), "w") as fd:
            fd.write(json.dumps(preferences))
            fd.close()