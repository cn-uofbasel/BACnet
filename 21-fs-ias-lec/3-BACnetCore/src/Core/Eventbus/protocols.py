import enum

"""
Defines the protocol used to work with the different types of messages.
For each message type, there exist several options, depending on the requested
action to be taken.
"""


class InterfaceProtocol(enum.Enum):
    create_feed = 1
    get_feed = 2
    subscribe = 3
    unsubscribe = 4
    get_available_feeds = 5
    set_radius = 6
    get_all_feeds = 7
    get_owned_feeds = 8
    block = 9
    unblock = 10
    push = 11
    send = 12
    get_owner_id = 13
    receive = 14
    get_content = 15
    get_current_seq_number = 16
    get_last_event = 17


class SyncProtocol(enum.Enum):  # TODO define protocol
    quer_info = 1  # query information
    quer_data = 2  # query data
    answ_info = 3  # answer information
    answ_data = 4  # answer data
    error = 5      # error code
