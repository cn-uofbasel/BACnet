from logStore.transconn.database_connector import DatabaseConnector
import cbor2


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


def sync_database(i_want_extensions_list, feed_extensions):
    feed_extensions = cbor2.loads(feed_extensions)
    dc = DatabaseConnector()
    if len(i_want_extensions_list) != len(feed_extensions):
        print("Something went wrong..")
        return

    for i, val in enumerate(i_want_extensions_list):
        appended_events_list = feed_extensions[i]
        for ev in appended_events_list:
            dc.add_event(ev)
    print("Finished synchronising!")
