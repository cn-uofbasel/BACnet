from logStore.transconn.database_connector import DatabaseConnector
import cbor2
import hashlib

"""
Function to calculate the hash value of the meta data
"""


def get_hash(blob):
    return hashlib.sha256(blob).digest()


"""
The functions checks first if there exist any entries with a specific feed ID. If it is the case, it compares the given
seq number of the feed ID with the one of this database. If it is smaller, the sequence number of the entry of 
list_of_feeds gets changed and appended to a new list (need_list). The entries contain only information about the
feed id and sequence number (starting from which seq number do we need extensions).

If there exist no entry with a specific feed ID, this_seq_num will be None. So, we need the whole feed, since it must
be new.

:param list_of_feed: List from device A 
:type list_of_feed: list
:return: list with information about the extensions we need
:rtype: list [feed id, sequence number from device B]
"""


def compare_feeds(list_of_feeds):
    need_list = []
    dc = DatabaseConnector()
    for i, elem in enumerate(list_of_feeds):
        feed_id = elem[0]
        seq_num = elem[1]
        this_seq_num = dc.get_current_seq_no(feed_id)

        # if seq num == -1 that means the feed does not exist in this database
        if this_seq_num is None:
            print("Entry does not exist...")
            need_list.append([feed_id, -1])
        elif this_seq_num < seq_num:
            elem[1] = this_seq_num
            need_list.append(elem)

    return need_list


"""
Creates a list of all feed IDs and their sequence number for the comparison

:return: list of feeds [feed ID, sequence number]
:rtype: list
"""


def create_list_of_feeds():
    dc = DatabaseConnector()
    list_of_feeds = dc.get_all_feed_ids()  # 4
    new_list = []
    for i, feedID in enumerate(list_of_feeds):
        if dc.check_outgoing(feedID):
            new_list.append([feedID, dc.get_current_seq_no(feedID)])
    return new_list


"""
Get all the extensions respectively the events and append them to a list of events

:param list_with_needed_extensions: The "I WANT"-list
:type list_with_needed_extensions: list
:return: list with events
:rtype: list 
"""


def filter_events(list_with_needed_extensions):
    event_list = []
    dc = DatabaseConnector()
    for info in list_with_needed_extensions:
        appended_events = []
        feed_id = info[0]
        seq_num = info[1]
        num = dc.get_current_seq_no(feed_id)
        for i in range(seq_num, num):
            extension = dc.get_event(feed_id, i + 1)
            appended_events.append(extension)
        print("Extension with", len(appended_events), "events")
        event_list.append(appended_events)
    return event_list


"""
Adding the events to the database after verifying the validation

:param i_want_extensions_list: the "I WANT"-list
:type  i_want_extensions_list: list
:param received_extensions: event list
:type  received_extensions: bytes (cbor2)
"""


def sync_database(i_want_extensions_list, received_extensions):
    received_extensions = cbor2.loads(received_extensions)
    dc = DatabaseConnector()
    if len(i_want_extensions_list) != len(received_extensions):
        print("Number of received extensions is not as expected. Sync aborted.")
        return
    print("Number of received extensions:", len(received_extensions))
    for i, val in enumerate(i_want_extensions_list):
        appended_events_list = received_extensions[i]
        # Check if valid
        if verify_validation(val, appended_events_list[0]):
            for ev in appended_events_list:
                app_name = cbor2.loads(ev)
                app_name = cbor2.loads(app_name[2])
                app_name = str(app_name[0]).split("/")
                if dc.check_incoming(val[0], app_name[0]):
                    print(app_name)
                    dc.add_event(ev)
        else:
            print("The extension is not valid! Sync of one received feed is not possible.")
    print("Finished synchronising!")


"""
Before the synchronisation, the function checks different things like:
- Same feed ids
- Correct sequence numbers
- Correct meta hash values
- Same signature

We compare the last event of the given feeds with the first event of the corresponding extension.

:param feed: A feed of the "I WANT"-list
:type feed: [feed id, sequence number] 
:param received_event: first event of the extension of a feed
:type  received_event: event
:return: True or False
"""


def verify_validation(feed, received_event):
    feed_id = feed[0]
    seq_num = feed[1]

    dc = DatabaseConnector()
    last_event = dc.get_event(feed_id, seq_num)

    # Controlling if last event exists
    if last_event is None:
        # If the list has -1, it means it is a new feed to create
        if seq_num == -1:
            print("Awaiting creation of new feed:", feed_id)
            return True
        else:
            return False

    last_event = cbor2.loads(last_event)
    last_meta = cbor2.loads(last_event[0])  # meta

    received_event = cbor2.loads(received_event)
    received_meta = cbor2.loads(received_event[0])  # meta

    # Controlling feed ids
    if last_meta[0] != received_meta[0]:
        print("Feed ID validation... FAILED")
        return False
    print("Feed ID validation... PASSED")

    # Controlling sequence numbers
    if last_meta[1] + 1 != received_meta[1]:
        print("Seq-Num validation... FAILED")
        return False
    print("Seq-Num validation... PASSED")

    # Controlling last meta hash value / prev hash value
    if received_meta[2][0] != 0 or get_hash(last_event[0]) != received_meta[2][1]:
        print("Meta Hash validation... FAILED")
        return False
    print("Meta Hash validation... PASSED")

    # Controlling the signature
    if last_meta[3] != received_meta[3]:
        print("Signature validation... FAILED")
        return False
    print("Signature validation... PASSED")
    print("Extension... VALID")
    return True
