from .Storage.database_handler import DatabaseHandler
from .security.verification import Verification
from .security.crypto import create_keys
from .Interface.event import Event, Meta, Content
from .Interface.subscribed_subfeed import SubscribedSubFeed
from .Interface.owned_subfeed import OwnedSubFeed
from .Interface.subscribed_masterfeed import SubscribedMasterFeed
from .Interface.owned_masterfeed import OwnedMasterFeed
from .Interface.feed import Feed, FeedMeta
from .com_link import ComLink
from Storage.event_factory import EventFactory

"""
The Storage Controller class is the main component in the BACNet Core it consists of methods that are triggered by feeds
or the Com-Link.

The StorageController gives well defined abstract functionality for basic operation of the BACNet. For more manual
Control or direct access to functionality which is not served by the Storage-controller, developers can use the
DatabaseHandler that provides all kind of functions to access BACNet Information and Data. 
"""


class StorageController:

    def __init__(self, path: str, db_type: str, com_link: ComLink):
        """
        Snd Constructor, that takes a path/Url to a database as well as the type of the Database and creates the
        Database-Connector that is essential to operate.

        Parameters
        ----------
        path        Is the path or the Url to the database the BaCNet-Node's operational data is stored in
        dbType      Is the type of the database ex SQLITE or MYSQL, must be defined in Database.DB_ENGINE
        com_link    A reference to a com-Link that the Storage Controller uses to trigger and set synchronization
        """
        self.database_handler = DatabaseHandler(dbtype=db_type, dbname=path)
        self.verification = Verification(self.database_handler)
        self.com_link = com_link
        self.factory = EventFactory(self.database_handler)

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

    def insert_event(self, feed_id: str, content: Content) -> bool:
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
                new_ev = self.factory.create_event_from_previous(prev_event.get_as_cbor(), content.identifier,
                                                                 content.data)
                self.database_handler.import_event_dispatch(new_ev)
                return True

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

    def create_feed(self, name, feed_id=None, signature_type=0, hash_type=0) -> bool:
        # if feed_id is given and it already exists, then abort
        if feed_id is not None and feed_id in self.database_handler.get_all_feed_ids():
            return False
        else:
            key_pair = create_keys(signature_type)
            # load last master event
            last_master_event = self.database_handler.get_my_last_event()
            # create master event to propagate new_feed and insert
            master_ev_new_feed = self.factory.create_event_from_previous(last_master_event, "MASTER/NewFeed", {'feed_id': feed_id, 'app_name': name})
            self.database_handler.import_event_dispatch(master_ev_new_feed)
            # create master event trust and insert it
            master_ev_trust = self.factory.create_event_from_previous(master_ev_new_feed, "MASTER/Trust", {'feed_id': feed_id})
            self.database_handler.import_event_dispatch(master_ev_trust)
            # insert genesis event of new feed
            first_ev = self.factory.create_first_event(key_pair[0], f"{name}/MASTER",
                                                       {'master_feed_id': self.database_handler.get_host_master_id()})
            self.database_handler.import_event_dispatch(first_ev)
            return True

    def get_feed(self, feed_id, name) -> Feed:
        # If feed exists in Database
        if feed_id in self.get_available_feeds():
            # if feed is own feed
            if feed_id in self.database_handler.get_owned_feed_ids():
                if feed_id is self.database_handler.get_host_master_id():
                    return OwnedMasterFeed(feed_id, FeedMeta("name", ), self)
                else:
                    return OwnedSubFeed(feed_id)
            else:
                if feed_id in self.database_handler.get_all_master_ids():
                    return SubscribedMasterFeed(feed_id)
                else:
                    return SubscribedSubFeed(feed_id)

    def subscribe(self, feed_id) -> bool:
        """
        If you subscribe a feed, you trust it!
        Parameters
        ----------
        feed_id     The feed_id of the feed you want to trust

        Returns
        -------
        true if subscription successful, false if not
        """
        # if feed is known and not yet trusted then proceed
        if feed_id in self.get_available_feeds() and feed_id not in self.get_trusted_feeds():
            last_master_event = self.database_handler.get_my_last_event()
            to_insert = self.factory.create_event_from_previous(last_master_event, "MASTER/Trust", {'feed_id': feed_id})
            self.import_event(to_insert) # TODO: makes sense to use import?
            return True


    def unsubscribe(self, feed_id):
        pass #TODO: Untrust is no thing in current BACNet

    def get_available_feeds(self):
        """
        Returns all Feeds that are known to exist (even if there are currently no events in the database)
        It therefore check the feeds of all known Masters
        Returns
        -------
        List of all available feed_ids
        """
        pass

    def get_all_stored_feeds(self):
        return self.database_handler.get_all_feed_ids()

    def get_owned_feeds(self):
        return self.database_handler.get_owned_feed_ids()

    def get_trusted_feeds(self):
        return self.database_handler.get_trusted(self.database_handler.get_host_master_id())

    def block(self, feed_id) -> bool:
        if not self.database_handler.is_owned(feed_id):
            self.database_handler.block(feed_id)
            return True
        else:
            return False

    def unblock(self, feed_id) -> bool:
        if not self.database_handler.is_owned(feed_id):
            self.database_handler.unblock(feed_id) #TODO: UNBLOCK A THING?
            return True
        else:
            return False

    def get_content(self, seq_num, feed_id):
        self.database_handler.get_event(feed_id, seq_num)

    def get_current_seq_num(self, feed_id):
        self.database_handler.get_current_seq_no(feed_id)

    def sync(self, just_masters=False):
        """
        Triggers the manual synchronization
        Parameters
        ----------
        just_masters

        Returns
        -------

        """
        if just_masters:
            self.com_link.sync_masters()
        else:
            self.com_link.sync_all()

    def set_sync_mode(self, mode):
        self.com_link.set_operation_mode(mode)

    def get_database_status(self):
        return dict()

    def _create_own_master(self):
        """
        This method checks whether an owned master feed exists and creates one if not.
        """
        if self.database_handler.get_host_master_id() is None:
            keypair = create_keys()  #TODO: store keys
            master_genesis = self.factory.create_first_event(keypair[0], "MASTER/MASTER", {})
            self.database_handler.import_event_dispatch(Event.from_cbor(master_genesis))
