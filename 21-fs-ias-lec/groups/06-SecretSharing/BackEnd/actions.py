# general imports

import os

# BACnet imports

# import BACnetCore
# import BACnetTransport

# internal imports

from BackEnd import keys, settings

# CORE INTERFACING FUNCTIONS
# examples ...

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

# SHAMIR INTERFACING FUNCTIONS
# examples ...

def split_secret_into_shares(secret): # shamir actions
    # ...
    pass

# ...
# ...


# OTHER UI INTERFACING FUNCTIONS
# examples ...

# alternatively to instantiating contacts each time
# it could be a global variable or passed to the functions

def edit_contact(name: str, public_key, feed_id, favfood):
    contacts = settings.Contacts()
    content = contacts.get_content()
    content[name] = {"public": public_key, "feed": feed_id, "favorite food": favfood}
    contacts.set_content(content)


def get_list_of_all_friends():
    contacts = settings.Contacts()
    return contacts.get_content().keys()


def get_joe_biden_contact():
    contacts = settings.Contacts()
    joe_biden_public_key = contacts.get_content()["joe biden"]["public"]
    joe_biden_feed = contacts.get_content()["joe biden"]["feed"]
    # ...

# ...
# ...
