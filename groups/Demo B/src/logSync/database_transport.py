from logSync import database_sync as sync
import cbor2

"""
TRANSPORT PROTOCOL:

Device A                                    Device B

- Creates "I HAVE"-list
- Serializes "I HAVE"-list
- Sends "I HAVE"-list
                                            - Receives "I HAVE"-list
                                            - Deserializes "I HAVE"-list
                                            - Compares "I HAVE"-list with own feeds
                                            - Creates "I WANT"- list
                                            - Serializes "I WANT"- list
                                            - Sends "I WANT"- list
- Receives "I WANT"-list
- Deserializes "I WANT"-list
- Filters events according to the list
- Creates event list
- Serializes event list
- Sends event list
                                            - Receives event list
                                            - Deserializes event list
                                            - Synchronisation
"""

"""
Device A creates a list of all feeds of the database. 

:return: list of feeds (every entry has [feedID, seq number])
:rtype: bytes (cbor2)
"""


def get_i_have_list():
    return cbor2.dumps(sync.create_list_of_feeds())


"""
Device B receives an "I HAVE"-list. It consists of information about all the feeds of Device A. The "I HAVE"-list is 
used to compare it with the feeds of this device (Comparing what does Device A have and what does Device B have). When 
it's done, it returns a list with the necessary extensions (a list of the differences of both device's "I HAVE"-list).

:param i_have_list: list of files (every entry has [feedID, seq number])
:type i_have_list: bytes (cbor2)
:return: list of the feeds of which we need the extensions ([feedID, seq number (of device B!)])
:rtype: bytes (cbor2)
"""


def get_i_want_list(i_have_list):
    list_of_extensions = sync.compare_feeds(cbor2.loads(i_have_list))
    return cbor2.dumps(list_of_extensions), list_of_extensions


"""
Device A receives an "I WANT"-list. It consists of the extensions that Device B needs. If the list is empty, it means
that there are no differences of both databases, therefore Device B is up-to-date. Otherwise, Device A filters the
necessary extensions and creates a list of it. 

:param i_want_list: list of the feeds of which we need the extensions [feed id, seq number]
:type i_want_list: bytes (cbor2)
:return: list with the extensions[[event1, event2, ...], [event1, event2, ...], ...]
:rtype: bytes (cbor2)
"""


def get_event_list(i_want_list):
    list_with_necessary_extensions = cbor2.loads(i_want_list)
    if not list_with_necessary_extensions:
        print("The other device is up-to-date")
        return cbor2.dumps([])

    event_list = sync.filter_events(list_with_necessary_extensions)
    return cbor2.dumps(event_list)
