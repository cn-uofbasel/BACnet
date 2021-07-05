from ..event import Event
from .EventFactory import EventFactory
from .sql_alchemy_connector import SQLITE, Database

class DatabaseHandler:
    """Database handler gets each created by the database connector as well as the function connector.

    It has the private fields of an byte array handler as well as an event handler to access the two databases
    accordingly.
    """

    def __init__(self, complete_path="NodeBase.sqlite", new_or_overwrite=True):
        self.__Connector = Database(SQLITE, complete_path)
        if new_or_overwrite:
            self.__Connector.create_cbor_db_tables()
            self.__Connector.create_master_table()

    def insert_master_event(self, seq_no, feed_id, content, cont_ident, event_as_cbor):
        event = cont_ident[1]
        if event == 'MASTER':
            self.__Connector.insert_master_event(True, feed_id, None, None, seq_no, None, None, 0,
                                                           event_as_cbor, None)
        elif event == 'Trust':
            self.__Connector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, True,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Block':
            self.__Connector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, False,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Name':
            self.__Connector.insert_master_event(False, feed_id, None, None, seq_no, None,
                                                           content[1]['name'], None, event_as_cbor, None)
        elif event == 'NewFeed':
            self.__Connector.insert_master_event(False, feed_id, content[1]['feed_id'], None, seq_no, True,
                                                           None, None, event_as_cbor, content[1]['app_name'])
        elif event == 'Radius':
            self.__Connector.insert_master_event(False, feed_id, None, None, seq_no,
                                                           None, None, content[1]['radius'], event_as_cbor, None)
        else:
            raise InvalidApplicationError('Invalid action called %s' % event)

    def insert_normal_event(self, event: Event) -> bool:
        self.__Connector.insert_event()

    def query_master_events(self, feedid, seqnum, content_filter):
        pass

    def query_normal_events(self, ):
        pass

    def add_to_db(self, event_as_cbor, app):
        """"Add a cbor event to the two databases.

        Calls each the byte array handler as well as the event handler to insert the event in both databases
        accordingly. Gets called both by database connector as well as the function connector. Returns 1 if successful,
        otherwise -1 if any error occurred.

        If a new feed is created for an app, the first event has to contain appname/MASTER and data as {'master_feed': master_feed_id}
        """
        if app:
            event = Event.from_cbor(event_as_cbor)
            feed_id = event.meta.feed_id
            content = event.content.content
            cont_ident = content[0].split('/')
            application = cont_ident[0]
            if application != 'MASTER':
                orig_master = self.get_master_id_from_feed(feed_id)
                if orig_master is None:
                    try:
                        master_feed = content[1]['master_feed']
                    except KeyError as e:
                        logger.error(e)
                        return
                    orig_master_feed = self.__eventHandler.get_host_master_id()
                    if master_feed == orig_master_feed or orig_master_feed is None:
                        last_event = self.__eventHandler.get_my_last_event()
                        cont_ident = content[0].split('/')[0]
                        ecf = EventFactory(last_event)
                        event = ecf.next_event('MASTER/NewFeed', {'feed_id': feed_id, 'app_name': cont_ident})
                        self.add_to_db(event, False)
                        event = ecf.next_event('MASTER/Trust', {'feed_id': feed_id})
                        self.add_to_db(event, False)
                    else:
                        return -1
        self.__byteArrayHandler.insert_event(event_as_cbor)
        try:
            event = Event.from_cbor(event_as_cbor)
            content = event.content.content
            cont_ident = content[0].split('/')
            application = cont_ident[0]
            if application != 'ratchet':
                self.__eventHandler.add_event(event_as_cbor)
        except InvalidApplicationError as e:
            logger.error(e)
            return -1
        return 1

    def get_current_seq_no(self, feed_id):
        """"Return the current sequence number of a given feed_id, returns an integer with the currently largest
                sequence number for the given feed. Returns -1 if there is no such feed_id in the database."""
        return self.__byteArrayHandler.get_current_seq_no(feed_id)

    def get_event(self, feed_id, seq_no):
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
                there is no such entry."""
        return self.__byteArrayHandler.get_event(feed_id, seq_no)

    def get_current_event_as_cbor(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
                there is no such feed_id in the database."""
        return self.__byteArrayHandler.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids(self):
        """"Return all current feed ids in the database."""
        return self.__byteArrayHandler.get_all_feed_ids()

    """Follwing are the feed control methods to be used from feed_ctrl_connection:"""

    def get_all_entries_by_feed_id(self, feed_id):
        return self.__eventHandler.get_all_entries_by_feed_id(feed_id)

    def get_trusted(self, master_id):
        return self.__eventHandler.get_trusted(master_id)

    def get_blocked(self, master_id):
        return self.__eventHandler.get_blocked(master_id)

    def get_all_master_ids(self):
        return self.__eventHandler.get_all_master_ids()

    def get_all_master_ids_feed_ids(self, master_id):
        return self.__eventHandler.get_all_master_ids_feed_ids(master_id)

    def get_username(self, master_id):
        return self.__eventHandler.get_username(master_id)

    def get_my_last_event(self):
        return self.__eventHandler.get_my_last_event()

    def get_host_master_id(self):
        return self.__eventHandler.get_host_master_id()

    def get_radius(self):
        return self.__eventHandler.get_radius()

    def get_master_id_from_feed(self, feed_id):
        return self.__eventHandler.get_master_id_from_feed(feed_id)

    def get_application_name(self, feed_id):
        return self.__eventHandler.get_application_name(feed_id)

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        return self.__eventHandler.get_feed_ids_from_application_in_master_id(master_id, application_name)

    def get_feed_ids_in_radius(self):
        return self.__eventHandler.get_feed_ids_in_radius()

    def set_feed_ids_radius(self, feed_id, radius):
        return self.__eventHandler.set_feed_ids_radius(feed_id, radius)

    def get_all_saved_events(self, chat_id):
        return self.__byteArrayHandler.get_all_saved_events(chat_id)

"""----------------------------------------------- from CBOR HAndler"""

    def insert_byte_array(self, event_as_cbor):
        """"Insert a new event into the database. For this we extract the sequence number and feed_id and store the
        exact cbor event with those values as keys."""
        event = Event.from_cbor(event_as_cbor)
        seq_no = event.meta.seq_no
        feed_id = event.meta.feed_id
        self.__sqlAlchemyConnector.insert_event(feed_id, seq_no, event_as_cbor)

    def get_current_seq_no(self, feed_id):
        """"Return the current sequence number of a given feed_id, returns an integer with the currently largest
        sequence number for the given feed. Returns -1 if there is no such feed_id in the database."""
        return self.__sqlAlchemyConnector.get_current_seq_no(feed_id)

    def get_event(self, feed_id, seq_no):
        """"Return a specific cbor event to the callee with the input feed_id and sequence number. Returns None if
        there is no such entry."""
        return self.__sqlAlchemyConnector.get_event(feed_id, seq_no)

    def get_current_event_as_cbor(self, feed_id):
        """"Return the newest (the one with the highest sequence number) cbor event for a feed_id. Returns None if
        there is no such feed_id in the database."""
        return self.__sqlAlchemyConnector.get_current_event_as_cbor(feed_id)

    def get_all_feed_ids(self):
        """"Return all current feed ids in the database."""
        return self.__sqlAlchemyConnector.get_all_feed_ids()

    def get_all_saved_events(self, chat_id):
        return self.__sqlAlchemyConnector.get_all_saved_events(chat_id)
    
    class InvalidSequenceNumber(Exception):
        def __init__(self, message):
            super(InvalidSequenceNumber, self).__init__(message)

    """------------------------------- From Eventhandler"""

    def add_event(self, event_as_cbor):
        try:
            event = Event.from_cbor(event_as_cbor)
            seq_no = event.meta.seq_no
            feed_id = event.meta.feed_id
            content = event.content.content

            cont_ident = content[0].split('/')
            application = cont_ident[0]
            application_action = cont_ident[1]

            if application == 'chat':
                if application_action == 'MASTER':
                    return
                chatMsg = content[1]['messagekey']
                chat_id = content[1]['chat_id']
                timestamp = content[1]['timestampkey']

                self.__sqlAlchemyConnector.insert_event(feed_id=feed_id, seq_no=seq_no, application=application,
                                                        chat_id=chat_id,
                                                        timestamp=timestamp, data=chatMsg)
            elif application == 'MASTER':
                self.master_handler(seq_no, feed_id, content, cont_ident, event_as_cbor)

            else:
                raise InvalidApplicationError('Invalid application called %s' % application)
        except KeyError as e:
            logger.error(e)
            return -1

    def get_all_entries_by_feed_id(self, feed_id):
        return self.__sqlAlchemyConnector.get_all_entries_by_feed_id(feed_id)

    """"Structure of insert_master_event:
    insert_master_event(self, master, feed_id, app_feed_id, trust_feed_id, seq_no, trust, name, radius, event_as_cbor, app_name)"""

    def master_handler(self, seq_no, feed_id, content, cont_ident, event_as_cbor):
        """Handle master events and insert the events corresponding to their definition:"""
        event = cont_ident[1]
        if event == 'MASTER':
            self.__sqlAlchemyConnector.insert_master_event(True, feed_id, None, None, seq_no, None, None, 0,
                                                           event_as_cbor, None)
        elif event == 'Trust':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, True,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Block':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, content[1]['feed_id'], seq_no, False,
                                                           None, None, event_as_cbor, None)
            from feedCtrl.radius import Radius
            r = Radius()
            r.calculate_radius()
        elif event == 'Name':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no, None,
                                                           content[1]['name'], None, event_as_cbor, None)
        elif event == 'NewFeed':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, content[1]['feed_id'], None, seq_no, True,
                                                           None, None, event_as_cbor, content[1]['app_name'])
        elif event == 'Radius':
            self.__sqlAlchemyConnector.insert_master_event(False, feed_id, None, None, seq_no,
                                                           None, None, content[1]['radius'], event_as_cbor, None)
        else:
            raise InvalidApplicationError('Invalid action called %s' % event)

    """"Following come the feed control mechanisms used by database_handler:"""

    def get_trusted(self, master_id):
        return self.__sqlAlchemyConnector.get_trusted(master_id)

    def get_blocked(self, master_id):
        return self.__sqlAlchemyConnector.get_blocked(master_id)

    def get_all_master_ids(self):
        return self.__sqlAlchemyConnector.get_all_master_ids()

    def get_all_master_ids_feed_ids(self, master_id):
        return self.__sqlAlchemyConnector.get_all_master_ids_feed_ids(master_id)

    def get_username(self, master_id):
        return self.__sqlAlchemyConnector.get_username(master_id)

    def get_my_last_event(self):
        return self.__sqlAlchemyConnector.get_my_last_event()

    def get_host_master_id(self):
        return self.__sqlAlchemyConnector.get_host_master_id()

    def get_radius(self):
        return self.__sqlAlchemyConnector.get_radius()

    def get_master_id_from_feed(self, feed_id):
        return self.__sqlAlchemyConnector.get_master_id_from_feed(feed_id)

    def get_application_name(self, feed_id):
        return self.__sqlAlchemyConnector.get_application_name(feed_id)

    def get_feed_ids_from_application_in_master_id(self, master_id, application_name):
        return self.__sqlAlchemyConnector.get_feed_ids_from_application_in_master_id(master_id, application_name)

    def get_feed_ids_in_radius(self):
        return self.__sqlAlchemyConnector.get_feed_ids_in_radius()

    def set_feed_ids_radius(self, feed_id, radius):
        return self.__sqlAlchemyConnector.set_feed_ids_radius(feed_id, radius)


class InvalidApplicationError(Exception):
    def __init__(self, message):
        super(InvalidApplicationError, self).__init__(message)