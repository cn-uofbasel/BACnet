from ..interface.event import Event
from .sql_alchemy_connector import SQLITE, Database


class DatabaseHandler:
    """
    The Database Handler is a class which holds some higher logic functions that work upon the atomic functions served
    by the Database class which is the lowest level interface to the Data.

    Important: Most methods in database-handler doesn't contain verification or checks. This is done in the
    StorageController
    """

    def __init__(self, db_path="NodeBase.sqlite", db_type=SQLITE):
        self.__Connector = Database(db_type, db_path)
        self.__Connector.create_event_table()
        self.__Connector.create_master_table()
        self.__Connector.create_feed_table()

    def get_owned_feed_ids(self):
        """
        Returns all feed_ids that are owned by this node. Includes own Master-feed
        """
        host_master_id = self.get_host_master_id()
        return self.get_all_master_ids_feed_ids(host_master_id) + [self.get_host_master_id()]

    def get_current_seq_no(self, feed_id):
        """"
        Return the current sequence number of a given feed_id, returns an integer with the currently largest
        sequence number for the given feed. Returns -1 if there is no such feed_id in the database.
        """
        seq_no = self.__Connector.get_current_seq_no(feed_id)
        if seq_no == -1:
            raise UnknownFeedError(feed_id)
        return seq_no

    def get_event(self, feed_id, seq_no) -> Event:
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
                there is no such entry."""
        result = self.__Connector.get_event(feed_id, seq_no)
        if result is None:
            if feed_id not in self.get_all_known_feed_ids():
                raise UnknownFeedError(feed_id)
            else:
                raise EventNotFoundError(seq_no, feed_id)
        return Event.from_cbor(result)

    def get_current_event_as_cbor(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
                there is no such feed_id in the database."""
        return self.__Connector.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids_in_db(self):
        """"Return all current feed ids in the database."""
        return self.__Connector.get_all_feed_ids_in_db()

    def get_all_known_feed_ids(self) -> set:
        """
        Returns all known feeds, no matter if they are blocked, trusted or in range. Once they are known due to a
        master event, they are known.
        Returns
        -------
        A set that contains the feed_ids of all known feeds(incl masters)
        """
        known_feeds = set(self.get_all_master_ids())

        for master in self.get_all_master_ids():
            for feed in self.get_all_master_ids_feed_ids(master):
                known_feeds.add(feed)
        return known_feeds

    def get_trusted(self, master_id):
        return self.__Connector.get_trusted(master_id)

    def get_blocked(self, master_id):
        return self.__Connector.get_blocked(master_id)

    def get_all_master_ids(self):
        return self.__Connector.get_all_master_ids()

    def get_all_master_ids_feed_ids(self, master_id):
        """
        This Method takes a feed_id of a master-feed as argument and returns a list of all feeds the master owns.
        If the given id is unknown, an UnknownFeedError is raised.
        """
        if master_id not in self.get_all_master_ids():
            raise UnknownFeedError(master_id)
        return self.__Connector.get_all_master_ids_feed_ids(master_id)

    def get_username(self, master_id):
        """
        This method queries the Database Instance to get the latest chosen username for the master.
        If no username was found, an UsernameNotfoundError is raised.
        """
        res = self.__Connector.get_username(master_id)
        if res is None:
            raise UsernameNotFoundError(master_id)
        else:
            return res

    def get_my_last_event(self):
        return Event.from_cbor(self.__Connector.get_my_last_event())

    def get_host_master_id(self):
        return self.__Connector.get_host_master_id()

    def get_radius(self):
        return self.__Connector.get_radius()

    def get_master_id_from_feed(self, feed_id):
        """
        This method returns the master_id of the master_feed, which owns the feed with given feed_id.
        If feed_id is not known or If no parent master is found, None is returned.
        (In normal use this will never happen since feeds must be propagated by master before import)
        """
        return self.__Connector.get_master_id_from_feed(feed_id)

    def get_application_name(self, feed_id):
        return self.__Connector.get_application_name(feed_id)

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        return self.__Connector.get_feed_ids_from_application_in_master_id(master_id, application_name)

    def get_feed_ids_in_radius(self):
        return self.__Connector.get_feed_ids_in_radius()

    def set_feed_ids_radius(self, feed_id, radius):
        return self.__Connector.set_feed_ids_radius(feed_id, radius)

    def import_event_dispatch(self, event: Event):
        feed_id = event.meta.feed_id
        seq_no = event.meta.seq_no
        fst_ident, snd_ident = event.content.identifier.split("/")
        content = event.content.data
        # if Event is a master event then additionally save it into the master table that is a functional abstraction
        # of the raw master-events
        if fst_ident == "MASTER":
            self.import_master_dispatch(seq_no, feed_id, content, snd_ident, event.get_as_cbor())
        self.__Connector.insert_event(feed_id, seq_no, event.get_as_cbor())

    def import_master_dispatch(self, seq_no, feed_id, content, event_ident, event_as_cbor):
        """Handle master events and insert the events corresponding to their definition:"""
        if event_ident == 'MASTER':
            self.__Connector.insert_master_event(True, feed_id, None, None, seq_no, None, None, 0, event_as_cbor, None)
        elif event_ident == 'Trust':
            self.__Connector.insert_master_event(False, feed_id, None, content['feed_id'], seq_no, True,
                                                 None, None, event_as_cbor, None)
            self.calculate_radius()
        elif event_ident == 'Block':
            self.__Connector.insert_master_event(False, feed_id, None, content['feed_id'], seq_no, False,
                                                 None, None, event_as_cbor, None)
            self.calculate_radius()
        elif event_ident == 'Name':
            self.__Connector.insert_master_event(False, feed_id, None, None, seq_no, None,
                                                 content[1]['name'], None, event_as_cbor, None)
        elif event_ident == 'NewFeed':
            self.__Connector.insert_master_event(False, feed_id, content['feed_id'], None, seq_no, True,
                                                 None, None, event_as_cbor, content['app_name'])
        elif event_ident == 'Radius':
            self.__Connector.insert_master_event(False, feed_id, None, None, seq_no,
                                                 None, None, content['radius'], event_as_cbor, None)
        else:
            raise InvalidApplicationError('Invalid action called %s' % event_ident)

    def calculate_radius(self):
        self.__check_trusted(self.get_host_master_id(), self.get_radius(), 'MASTER')

    def __check_trusted(self, master_id, radius, prev_app_name, step=1, ):
        if radius and step is not None:
            if radius < 1 or step > radius:
                return
            trusted = self.get_trusted(master_id)
            if not len(trusted) == 0:
                for trusted_id in trusted:
                    application_name = self.get_application_name(trusted_id)
                    master = None
                    if application_name == 'MASTER':
                        master = trusted_id
                        if master != self.get_host_master_id():
                            self.set_feed_ids_radius(master, step)
                    elif application_name == prev_app_name or prev_app_name == 'MASTER':
                        master = self.get_master_id_from_feed(trusted_id)
                        if master != self.get_host_master_id():
                            self.set_feed_ids_radius(master, step)
                    else:
                        return
                    self.__check_trusted(master, radius, application_name, step + 1)
            else:
                return

    def is_owned(self, feed_id):
        """
        Checks if the feed with the given feed_id is owned by this node
        """
        return feed_id in self.get_owned_feed_ids()

    def is_blocked(self, feed_id):
        """
        Checks if the feed with the given feed_id is blocked by this node
        """
        return feed_id in self.get_blocked(self.get_host_master_id())

    def get_private_key(self, feed_id, first_insertion=False):
        """
        This method returns the private key of a owned feed! If the feed is not owned, FeedNotOwnedError is raised.
        If the feed is unknown, UnknownFeedError is raised!
        On first insertion the feed can't be known so one can set the flag to bypass these checks.
        """
        if feed_id not in self.get_all_known_feed_ids() and not first_insertion:
            raise UnknownFeedError(feed_id)
        if first_insertion or self.is_owned(feed_id):
            return self.__Connector.get_private_key(feed_id)
        else:
            raise FeedNotOwnedError(feed_id)

    def insert_feed_information(self, feed_id, private_key='', is_owned=False, is_master=False):
        """
        This method is used gto insert feed information of new known feeds into the database.
        """
        if is_owned:
            self.__Connector.create_feed(feed_id, private_key, is_master)
        else:
            # arbitrary value for curr_seq -> in this version feed_table entries are just used to store private_keys
            self.__Connector.import_new_feed(feed_id, 123, is_master)


class InvalidApplicationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnknownFeedError(Exception):
    def __init__(self, message):
        super().__init__(f"The Feed: {message} hasn't been found in the database!")


class EventNotFoundError(Exception):
    def __init__(self, seq_num, feed_id):
        super().__init__(f"The Event from feed {feed_id} with seq_num {seq_num} could not be found in the database!")


class UsernameNotFoundError(Exception):
    def __init__(self, master_id):
        super().__init__(f"The username for the master-feed {master_id} could not be found!")


class FeedNotOwnedError(Exception):
    def __init__(self, feed_id):
        super().__init__(f"The feed of the feed_id {feed_id} is not owned and tho has no private key to access!")



