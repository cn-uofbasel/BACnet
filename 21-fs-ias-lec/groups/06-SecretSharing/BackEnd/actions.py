# The FrontEnd has to connect somewhere, how about right here

import os

# import BACnetCore
# import BACnetTransport

from BackEnd import keys, settings


def setup_environment():  # core stuff
    preferences = settings.Preferences()
    database_path: os.path = preferences.get_content()["db"]
    # storage = BACnetCore.Storage.SQLiteConnector(os.path.join(database_path, "db"))
    # myChannel = BACnetTransport.Paths(?)
    # ...
    # ...
    pass

# ...
# ...


def get_list_of_all_friends():  # and direct ui actions
    contacts = settings.Contacts()
    return contacts.get_content().keys()


def get_joe_biden_public_key():  # example
    contacts = settings.Contacts()
    joe_biden_public_key = contacts.get_content()["joe biden"]["public"]

# ...
# ...
