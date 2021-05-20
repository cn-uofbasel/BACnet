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

def edit_contact(contact: str, public_key, feed, radius):
    contacts = settings.Contacts()
    content = contacts.get_content()
    content[contact] = dict(
        {
            "public": public_key,
            "feed": feed,
            "radius": radius
        }
    )
    contacts.set_content(content)


def get_list_of_all_friends():
    contacts = settings.Contacts()
    return contacts.get_content().keys()


def get_contact(contact):
    contacts = settings.Contacts()
    contact_public_key = contacts.get_content()[contact]["public"]
    contact_feed = contacts.get_content()[contact]["feed"]
    # ...

# ...
# ...
