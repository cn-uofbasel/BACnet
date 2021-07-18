from ..storage.database_handler import DatabaseHandler, UnknownFeedError
from .crypto import check_signature, check_in_order, check_content_integrity
from ..interface.event import Event
from ...log import create_logger

logger = create_logger('Verification')


class Verification:
    """
    This class is used by the storage Controller to determine which feeds should be imported or exported.
    Thus, this class, especially the methods should_import() and should_export(), define the export/import rules.

    This class also has a method to validate an event on import -> check signature, hash, in-order.
    Since every imported event is verified, this does not have to be done on export.

    Feed Import rules:
    -------------
    - MASTER feeds are always imported
    - Trusted & not blocked feeds are imported
    - Feeds must be in defined radius(trust radius) Radius == 1 -> are your own feeds

    Feed Export rules:
    -------------
    - Own Master is always exported/proposed
    - trusted feeds that are not bocked are exported (NOTE: Master feeds from other Nodes can also be blocked!)
    
    Radius rules(defined by _check_in_radius()):
    ---------------------------------------------
     - Feed is in radius if it is trusted by a master you know in your social radius
     - One could for example add the rule that just non-blocked feeds are in radius
    """

    def __init__(self, db_handler: DatabaseHandler):
        self._dataConn = db_handler
        self._hostid = self._dataConn.get_host_master_id()

    def verify_event_import(self, event: Event) -> bool:
        """
        It uses should_import_feed to validate existence and import_rules! TODO: can be separate?
        This method verifies if an event is valid and thus can be imported into the database/a feed.
        It performs the following checks:
        - is sequence number correct? -> if it has prev event, check previous hash property
        - is the signature correct
        - if the event has a content is it integer

        Parameters
        ----------
        event   the event to be validated

        Returns
        -------
        bool whether verification has been successful.
        """
        feed_id = event.meta.feed_id
        # Check if feed exists and should be imported, then checks signature and integrity
        if self.should_import_feed(feed_id, event.content.identifier) and check_signature(event) and check_content_integrity(event):
            print("Policies fulfilled, signature valid, content hash ok!")
            try:
                curr_seq = self._dataConn.get_current_seq_no(event.meta.feed_id)
            except UnknownFeedError:
                curr_seq = -1

            if curr_seq >= 0:
                print("there is a previous event...")
                last_event = self._dataConn.get_event(event.meta.feed_id, curr_seq)
                return check_in_order(event, last_event)
            else:
                print("feed has not been seen before...")
                return check_in_order(event, last_event=None)
        else:
            return False

    def should_import_feed(self, feed_id, content_identifier):
        """
        This method takes a feed_id and name and checks whether the feed fulfills the import rules.
        Parameters
        ----------
        feed_id     id/pubkey of the feed to check the rules for
        feed_name   The name of the feed(= first part of content_id before /)

        Returns
        -------
        true/false whether the feed fulfills the import rules
        """
        if self._hostid is None:
            self._hostid = self._dataConn.get_host_master_id()
        # If the given feed is a master feed we will always accept it.
        if content_identifier.split("/")[0] == 'MASTER':
            return True
        else:
            if self._is_trusted(feed_id, self._hostid) and not self._is_blocked(feed_id, self._hostid):
                return True
            if self._dataConn.get_radius() == 1:
                return False
            else:
                return self._check_in_radius(feed_id)

    def should_export_feed(self, feed_id):
        """
        This method checks whether a feed in your database should be exported or proposed to others.
        Just trusted feeds, non-blocked feeds and masters are exported/proposed

        Parameters
        ----------
        feed_id Feed_ID to check exportability

        Returns
        -------
        true/false whether the events of a given feed_id fulfill the export-rules
        """
        if self._hostid is None:
            self._hostid = self._dataConn.get_host_master_id()
        if feed_id == self._hostid:
            return True
        return (not self._is_blocked(feed_id, self._hostid)) and \
               (self._is_trusted(feed_id, self._hostid) or self._is_known_master(feed_id))

    def _is_blocked(self, feed_id, by_host):
        return feed_id in set(self._dataConn.get_blocked(by_host))

    def _is_known_master(self, feed_id):
        return feed_id in set(self._dataConn.get_all_master_ids())

    def _is_trusted(self, feed_id, by_host):
        return feed_id in set(self._dataConn.get_trusted(by_host))

    def _check_in_radius(self, feed_id):
        """
        This method checks whether a feed is in your social radius (not the technical distance). It looks for masters
        within your radius and checks whether the given feed is in the trusted list of any master.
        
        In radius = a master feed you know trusts this feed
        
        Parameters
        ----------
        feed_id the feed_id/pubkey of the feed you want to check if its in radius

        Returns
        -------
        true/false whether feed_id is in radius or not
        """
        master_in_radius = self._dataConn.get_feed_ids_in_radius()
        if master_in_radius is None:
            return False
        # check if the feed_id is inside the social radius
        for master in master_in_radius:
            feed_ids = self._dataConn.get_trusted(master)
            if feed_ids is not None:
                return feed_id in feed_ids
        return False
