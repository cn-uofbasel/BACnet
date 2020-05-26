from logStore.transconn.database_connector import DatabaseConnector
import cbor2
import hashlib


def get_hash(blob):
    return hashlib.sha256(blob).digest()


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


def create_list_of_feeds():
    dc = DatabaseConnector()
    list_of_feeds = dc.get_all_feed_ids()  # 4
    new_list = []
    for i, feedID in enumerate(list_of_feeds):
        new_list.append([feedID, dc.get_current_seq_no(feedID)])
    return new_list


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
        print(len(appended_events))
        event_list.append(appended_events)
    return event_list


def sync_database(i_want_extensions_list, received_extensions):
    received_extensions = cbor2.loads(received_extensions)
    dc = DatabaseConnector()
    if len(i_want_extensions_list) != len(received_extensions):
        print("Something went wrong..")
        return

    for i, val in enumerate(i_want_extensions_list):
        appended_events_list = received_extensions[i]
        # Check if valid
        if verify_validation(val, appended_events_list[0]):
            for ev in appended_events_list:
                dc.add_event(ev)
        else:
            print("The extension is not valid! Sync not possible.")
            return

    print("Finished synchronising!")


def verify_validation(i_want_list, received_event):
    feed_id = i_want_list[0]
    seq_num = i_want_list[1]

    dc = DatabaseConnector()
    last_event = dc.get_event(feed_id, seq_num)

    # Controlling if last event exists
    if last_event is None:
        # If the list has -1, it means it is a new feed to create
        if seq_num == -1:
            print("Awaiting creation of new feeds:", feed_id)
            return True
        else:
            return False

    last_event = cbor2.loads(last_event)
    last_meta = cbor2.loads(last_event[0])  # meta

    received_event = cbor2.loads(received_event)
    received_meta = cbor2.loads(received_event[0])  # meta

    # Controlling feed ids
    if last_meta[0] != received_meta[0]:
        return False
    print(last_meta[0])
    print(received_meta[0])

    # Controlling sequence numbers
    if last_meta[1] != received_meta[1]:
        return False
    print(last_meta[1])
    print(received_meta[1])

    # Controlling last meta hash value / prev hash value
    if received_meta[2][0] != 0 or get_hash(last_event[0]) != received_meta[2][1]:
        return False
    print(get_hash(last_event[0]))
    print(received_meta[2][1])

    if last_meta[3] != received_meta[3]:
        return False
    print(last_meta[3])
    print(received_meta[3])

    return True
