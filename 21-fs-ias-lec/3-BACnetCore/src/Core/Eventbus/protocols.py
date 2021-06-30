import enum

"""
Defines the protocol used to work with the different types of messages.
For each message type, there exist several options, depending on the requested
action to be taken.
"""


class InterfaceProtocol(enum.Enum):
    create_feed = 1
    get_feed = 2                    # self id, feed id
    subscribe = 3                   # self id, feed id
    unsubscribe = 4                 # self id, feed id
    get_available_feeds = 5         # self id
    set_radius = 6                  # self id, radius (integer)
    get_all_feeds = 7               # self id
    get_owned_feeds = 8             # self id
    block = 9                       # self id, feed id
    unblock = 10                    # self id, feed id
    push = 11                       # self id, feed id, data type, data
    send = 12                       # self id, feed id
    get_owner_id = 13               # self id
    receive = 14                    # self id
    get_content = 15                # self id, feed id, seq number
    get_current_seq_number = 16     # self id, feed id
    get_last_event = 17             # self id, feed id


class SyncProtocol(enum.Enum):  # TODO define protocol
    quer_info = 1  # query information
    quer_data = 2  # query data
    answ_info = 3  # answer information
    answ_data = 4  # answer data
    error = 5      # error code
