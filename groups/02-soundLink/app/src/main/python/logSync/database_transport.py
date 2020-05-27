from logSync import database_sync as sync
import cbor

"""
TRANSPORT PROTOCOL:

Device A                                    Device B

- Creates "I HAVE"-list
- Serializes "I HAVE"-list
- Sends "I HAVE"-list
                                            - Receives "I HAVE"-list
                                            - Deserializes "I HAVE"-list
                                            - Compares "I HAVE"-list with own files
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
Device A creates a list of all files of a specific directory (later, it will be the database). 

:return: list of files (every entry has [filename, feedID, seq number])
:rtype: bytes (cbor)
"""


def get_i_have_list(path="hello"):
    return cbor.dumps(sync.create_list_of_feeds())


"""
Device B receives an "I HAVE"-list. It consists of information about all the files of Device A and its specific
directory. The "I HAVE"-list is used to compare it with the files of this device's specific directory (Comparing what
does Device A have and what does Device B have). When it's done, it returns a list with the necessary extensions 
(a list of the differences of both device's "I HAVE"-list).

:param i_have_list: list of files (every entry has [filename, feedID, seq number])
:type i_have_list: bytes (cbor)
:return: list of the files of which we need the extensions ([filename, feedID, seq number (of device B!)])
:rtype: bytes (cbor)
"""


def get_i_want_list(i_have_list):
    list_of_extensions = sync.compare_feeds(cbor.loads(i_have_list))
    return cbor.dumps(list_of_extensions), list_of_extensions


"""
Device A receives an "I WANT"-list. It consists of the extensions that Device B needs. If the list is empty, it means
that there are no differences of both directories, therefore Device B is up-to-date. Otherwise, Device A filters the
necessary extensions and creates a list of it. 

:param i_want_list: list of the files of which we need the extensions 
:type i_want_list: bytes (cbor)
:return: list with the extensions
:rtype: bytes (cbor)
"""


def get_event_list(i_want_list):
    list_with_necessary_extensions = cbor.loads(i_want_list)
    if not list_with_necessary_extensions:
        print("The other device is up-to-date")
        return cbor.dumps([])

    event_list = sync.filter_events(list_with_necessary_extensions)
    return cbor.dumps(event_list)



def get_bytes_from_tojava_pyobject(b):
    return bytes(b)