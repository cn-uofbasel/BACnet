from logStore.appconn import feed_ctrl_connection
import Event, EventCreationTool

import json
import os
from typing import List, Tuple


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)



@Singleton
class RequestHandler:
    """ This class acts as an Instance for the database connection of logStore and the EventCreationTool of logMerge"""
    def __init__(self):
        self.num = 0
        self.logged_in = False
        self.event_factory = None
        self.db_connection = feed_ctrl_connection.FeedCtrlConnection()
        print(f"Host Master Feed Id: {self.db_connection.get_host_master_id()}")
        self.username = ""
        self.load_user()

    def load_user(self):
        """Mainly for the Secret sharing application"""
        script_dir = os.path.dirname(__file__)
        rel_path = "data/keys/user.json"
        abs_path = os.path.join(script_dir, rel_path)

        if os.path.isfile(abs_path):
            with open(abs_path, "r") as fd:
                user_dict = json.loads(fd.read())
                feed_id = bytes.fromhex(user_dict["feed_id"])
                self.username = user_dict["username"]
                self.event_factory = EventCreationTool.EventFactory(last_event=self.db_connection.get_current_event(feed_id),
                                                                    path_to_keys=os.path.join(script_dir, "data/keys/"),
                                                                    path_to_keys_relative=False)

    def create_user(self, username):
        """Mainly for the Secret sharing application"""
        print("creating new user")
        script_dir = os.path.dirname(__file__)
        rel_path = "data/keys/user.json"
        abs_path = os.path.join(script_dir, rel_path)
        self.event_factory = EventCreationTool.EventFactory()
        feed_id = self.event_factory.get_feed_id()
        first_event = self.event_factory.first_event("chat", self.db_connection.get_host_master_id())
        print(first_event)
        if self.db_connection.insert_event(first_event) == -1:
            print("Inserting first event failed")
        print(f"feed_id:{feed_id} with username: {username} created")
        os.replace(script_dir +"/"+  feed_id.hex() + ".key", os.path.join(script_dir,"data/keys/" + feed_id.hex() + ".key"))
        self.event_factory.set_path_to_keys(os.path.join(script_dir, "data/keys/"))
        with open(abs_path, "w") as fd:
            user_dict = {
                "username": username,
                "feed_id": feed_id.hex()
            }
            fd.write(json.dumps(user_dict, indent=4))

    def get_feed_ids(self):
        """This Function gets all the feed id's in the database, NO MASTER FEED IDS"""
        feed_ids = self.db_connection.get_all_feed_ids()
        master_ids = self.db_connection.get_all_master_ids()
        own_ids = self.event_factory.get_own_feed_ids()
        master_ids.append(self.db_connection.get_host_master_id())

        # remove master feed ids
        feed_ids = [feed_id for feed_id in feed_ids if feed_id not in master_ids]
        # remove own feed ids
        feed_ids = [feed_id for feed_id in feed_ids if feed_id not in own_ids]

        return feed_ids

    def insert_new_events(self, events: List[dict]):
        """creates new Events with feeds EventFactory and inserts it into the database"""
        for event in events:
            next_event = self.event_factory.next_event("chat/secret", event)
            self.db_connection.insert_event(next_event)

    def pull_new_events(self, feed_seq_tuples: List[Tuple[bytes, int]]):
        """pulls Events for specified feed_id starting at the specified seq_no"""
        event_list = []
        for tuples in feed_seq_tuples:
            feed_id, old_seq_no = tuples
            current_seq_no = self.db_connection.get_current_seq_no(feed_id) + 1
            for seq_no in range(old_seq_no, current_seq_no):
                event = self.db_connection.get_event(feed_id, seq_no)
                event_list.append((Event.Event.from_cbor(event).content.content[1], feed_id))
        return event_list