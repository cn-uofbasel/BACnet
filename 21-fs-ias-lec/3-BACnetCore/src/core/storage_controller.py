from .storage.database_handler import DatabaseHandler, UnknownFeedError, EventNotFoundError
from .security.verification import Verification
from .security.crypto import create_keys
from .interface.event import Event, Content
from .interface.subscribed_subfeed import SubscribedSubFeed
from .interface.owned_subfeed import OwnedSubFeed
from .interface.subscribed_masterfeed import SubscribedMasterFeed
from .interface.owned_masterfeed import OwnedMasterFeed
from .interface.feed import Feed
from .storage.event_factory import EventFactory

"""
The storage Controller class is the main component in the BACNet core it consists of methods that are triggered by feeds
or the Com-Link.

The StorageController gives well defined abstract functionality for basic operation of the BACNet. For more manual
Control or direct access to functionality which is not served by the storage-controller, developers can use the
DatabaseHandler that provides all kind of functions to access BACNet Information and Data. 
"""


class StorageController:

    def __init__(self, path: str, db_type: str, node):
        """
        Snd Constructor, that takes a path/Url to a database as well as the type of the Database and creates the
        Database-Connector that is essential to operate.

        Parameters
        ----------
        path        Is the path or the Url to the database the BaCNet-Node's operational data is stored in
        dbType      Is the type of the database ex SQLITE or MYSQL, must be defined in Database.DB_ENGINE
        com_link    A reference to a com-Link that the storage Controller uses to trigger and set synchronization
        """
        self.database_handler = DatabaseHandler(db_type=db_type, db_path=path)
        self.verification = Verification(self.database_handler)
        self.com_link = node.get_com_link()
        self.factory = EventFactory(self.database_handler)
        self._create_own_master()

    def get_database_handler(self):
        """
        This method returns the current used Database-Handler, and thus allows the user to get better manual control
        over the used Database. Can for example be used to implement extensions or plugins.

        Returns
        -------
        If an instance of DatabaseHandler (self.database_handler) is present it is returned
        """
        if self.database_handler:
            return self.database_handler

    def get_com_link(self):
        return self.com_link

    def insert_event(self, feed_id: str, content: Content):
        """
        Method that is used to insert a created event into one of the owned feeds of this node. First the event to
        Insert is validated, then signed and inserted into the Database. NOTE: at this point the event is not sent to
        others as they must explicitly ask for it.
        Since a genesis event is created when creating a feed, there will be always a previous event

        Parameters
        ----------
        event   the id of the feed that we want to insert the event into
        content the content of the inserted event

        Returns
        -------
        True if insert successful False if not
        """
        if feed_id in self.database_handler.get_owned_feed_ids():
            prev_event = Event.from_cbor(self.database_handler.get_current_event_as_cbor(feed_id))
            if prev_event is not None:
                new_ev = self.factory.create_event_from_previous(prev_event, content.identifier,
                                                                 content.data)
                self.database_handler.import_event_dispatch(new_ev)

    def import_event(self, event: Event) -> bool:
        """
        This Method is used by the COM-Link to import a new Event that has been received. It is first verified and then
        inserted into the database, returns True if import was successful, False if not.

        Parameters
        ----------
        event   the event that should be imported

        Returns
        -------
        bool whether import has been successful
        """
        if self.verification.verify_event_import(event):
            self.database_handler.import_event_dispatch(event)
            return True
        return False

    def create_feed(self, name, feed_id=None, signature_type=0, hash_type=0):
        """
        Tries to create a feed. Returns the feed_id when successful. False when not.
        There can be Feeds with the same name! In this version they don't need to be unique.
        """
        # if feed_id is given and it already exists, then abort
        if feed_id is not None and feed_id in self.database_handler.get_all_feed_ids_in_db():
            return False
        else:
            # create key pair and store it
            key_pair = create_keys(signature_type)
            self.database_handler.insert_feed_information(key_pair[0], key_pair[1], is_master=False, is_owned=True)
            # load last master event
            last_master_event = self.database_handler.get_my_last_event()
            # create master event to propagate new_feed and insert
            master_ev_new_feed = self.factory.create_event_from_previous(last_master_event, "MASTER/NewFeed",
                                                                         {'feed_id': key_pair[0], 'app_name': name})
            self.database_handler.import_event_dispatch(master_ev_new_feed)
            # create master event trust and insert it
            master_ev_trust = self.factory.create_event_from_previous(master_ev_new_feed, "MASTER/Trust",
                                                                      {'feed_id': key_pair[0]})
            self.database_handler.import_event_dispatch(master_ev_trust)
            # insert genesis event of new feed
            first_ev = self.factory.create_first_event(key_pair[0], f"{name}/MASTER",
                                                       {'master_feed_id': self.database_handler.get_host_master_id()})
            self.database_handler.import_event_dispatch(first_ev)
            return key_pair[0]

    def get_feed(self, feed_id) -> Feed:
        """
        This method checks whether the given feed_id is known. If it is, an appropriate interface Instance is returned.
        Otherwise an UnknownFeedError is raised.
        """
        # If feed exists in Database
        if self.feed_is_known(feed_id):
            # if feed is own feed
            if self.database_handler.is_owned(feed_id):
                if feed_id == self.database_handler.get_host_master_id():
                    return OwnedMasterFeed(feed_id, self)
                else:
                    return OwnedSubFeed(feed_id, self)
            else:
                if feed_id in self.database_handler.get_all_master_ids():
                    return SubscribedMasterFeed(feed_id, self)
                else:
                    return SubscribedSubFeed(feed_id, self)
        else:
            raise UnknownFeedError(feed_id)

    def subscribe(self, feed_id) -> bool:
        """
        If you subscribe a feed, you trust it! You can just trust a feed if it is known.
        Parameters
        ----------
        feed_id     The feed_id of the feed you want to trust

        Returns
        -------
        true if subscription successful, false if not
        """
        # if feed is known and not yet trusted then proceed
        if feed_id in self.get_known_feeds() and feed_id not in self.get_trusted_feeds():
            last_master_event = self.database_handler.get_my_last_event()
            to_insert = self.factory.create_event_from_previous(last_master_event, "MASTER/Trust", {'feed_id': feed_id})
            self.import_event(to_insert)
            return True
        return False

    def get_known_feeds(self) -> list:
        """
        Returns all Feeds that are known to exist (even if there are currently no events in the database)
        It therefore check the feeds of all known Masters.
        Returns
        -------
        List of all available feed_ids
        """
        return list(self.database_handler.get_all_known_feed_ids())

    def get_all_stored_feeds(self):
        return self.database_handler.get_all_feed_ids_in_db()

    def get_owned_feeds(self):
        return self.database_handler.get_owned_feed_ids()

    def get_trusted_feeds(self):
        return self.database_handler.get_trusted(self.database_handler.get_host_master_id())

    def block(self, feed_id) -> bool:
        """
        This method takes a feed_id. It checks if its owned or not or if it is already blocked. If its not owned
        and not already blocked -> The feed gets blocked. Existence is not checked so that you can block any feed.
        """
        if not self.database_handler.is_owned(feed_id) and not self.database_handler.is_blocked(feed_id):
            block_event = self.factory.create_event_from_previous(self.database_handler.get_my_last_event(),
                                                                  "MASTER/Block", {'feed_id': feed_id})
            self.database_handler.import_event_dispatch(block_event)
            return True
        else:
            return False

    def get_event(self, seq_num, feed_id):
        """
        This method returns the event from a given feed with ta given seq_nom. It can raise UnknownFeedError or
        EventNotFoundError.
        """
        return self.database_handler.get_event(feed_id, seq_num)

    def get_events_since(self, feed_id, last_seq_num):
        """
        This Method checks if the feed_id exists in the database and returns a list of all events that have a higher seq
        number than the one that was given. If the feed is not found, an exception is raised. if seq num is >=
        current seq num, an empty list is returned.
        :param: last_seq_num: The last_seq-num that exists in foreign database. Therefor is excluded in list.
        """
        if not self.feed_is_known(feed_id):
            raise UnknownFeedError(feed_id)
        events = []
        curr_local_seq_num = self.get_current_seq_num(feed_id)
        for i in range(last_seq_num + 1, curr_local_seq_num + 1):
            events.append(self.get_event(i, feed_id))
        return events

    def get_current_seq_num(self, feed_id):
        """
        This method returns the current seq-num(= seq num of the most fresh event in the database) of the given feed_id.
        UnknownFeedException is raised when not found. It is catched and -1 is returned.
        """
        try:
            return self.database_handler.get_current_seq_no(feed_id)
        except UnknownFeedError:
            return -1

    def feed_is_known(self, feed_id):
        """
        Returns whether a feed is known to this Node or not.
        """
        return feed_id in self.get_known_feeds()

    def sync(self):
        """
        Triggers the manual synchronization
        """
        # send request to get database-status of peer_node
        self.com_link.request_sync()
        # read all inputs from the queue
        self.com_link.parse_all_inputs()

    def set_sync_mode(self, mode):
        self.com_link.set_operation_mode(mode)

    def get_database_status(self):
        """
        return a dict of all known feeds and corresponding current_seq_num
        """
        status = dict()
        for feed_id in self.get_known_feeds():
            status[feed_id] = self.get_current_seq_num(feed_id)
        return status

    def get_name_by_feed_id(self, feed_id):
        """
        Tries to resolve a given feed_id into a name. If the feed exists the name is returned.
        Else raise UnknownFeedError
        """
        return self.get_event(0, feed_id).content.identifier.split("/")[0]

    def get_feed_id_for_name(self, name):
        """
        This Method returns a feed_id for the given name. If no feed_id for the given name is found, then an
        UnknownFeedError is raised. ATTENTION: Just the first feed_id with this name is returned!!
        """
        name_mapping = self.get_feed_name_list()
        for feed_id in name_mapping.keys():
            if name_mapping[feed_id] == name:
                return feed_id
        raise UnknownFeedError(name)

    def get_feed_name_list(self):
        """
        Creates a dict which maps all known feed_ids to their names. If the feed is not in database yet, None is
        chosen as the name-placeholder.
        """
        name_dict = dict()
        for feed_id in self.get_known_feeds():
            try:
                name = self.get_name_by_feed_id(feed_id)
            except EventNotFoundError:
                name = None
            name_dict[feed_id] = name
        return name_dict

    def get_owned_master(self):
        """
        Returns an OwnedMasterFeed Instance. Doesn't need to check the existence since it is ensured in the
        Constructor
        """
        return self.get_feed(self.database_handler.get_host_master_id())

    def _create_own_master(self):
        """
        This method checks whether an owned master feed exists and creates one if not.
        """
        if self.database_handler.get_host_master_id() is None:
            keypair = create_keys()
            self.database_handler.insert_feed_information(keypair[0], keypair[1], True, True)
            master_genesis = self.factory.create_first_event(keypair[0], "MASTER/MASTER", {})
            self.database_handler.import_event_dispatch(master_genesis)

