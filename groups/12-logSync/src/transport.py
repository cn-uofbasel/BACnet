import sync
import cbor2
import pcap

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
:rtype: list
"""


def get_i_have_list():
    # TODO: Change directory to database
    list_of_files = sync.create_list_of_files('udpDir/')  # 4
    return cbor2.dumps(list_of_files)


"""
Device B receives an "I HAVE"-list. It consists of information about all the files of Device A and its specific
directory. The "I HAVE"-list is used to compare it with the files of this device's specific directory (Comparing what
does Device A have and what does Device B have). When it's done, it returns a list with the necessary extensions 
(a list of the differences of both device's "I HAVE"-list).
"""


def get_i_want_list(i_have_list):
    list_of_extensions = sync.compare_files(cbor2.loads(i_have_list))
    return cbor2.dumps(list_of_extensions)


"""
Device A receives an "I WANT"-list. It consists of the extensions that Device B needs. If the list is empty, it means
that there are no differences of both directories, therefore Device B is up-to-date. Otherwise, Device A filters the
necessary extensions and creates a list of it. 
"""


def get_event_list(i_want_list):
    list_with_necessary_extensions = cbor2.loads(i_want_list)
    if not list_with_necessary_extensions:
        print("The other device is up-to-date0")
        return []

    event_list = []
    for file_info in list_with_necessary_extensions:
        filename = file_info[0]
        seq = file_info[2]

        # TODO: Change directory to database
        extension = pcap.get_meta_and_cont_bits('udpDir/' + filename, seq)  # 10
        event_list.append(extension)

    return cbor2.dumps(event_list)
