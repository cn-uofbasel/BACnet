import os
import sys
from datetime import datetime
from logic.file_handler import DIR_MAIN, make_dirs
from pathlib import Path

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../dependencies/07-14-logCtrl/src')
sys.path.append(folderG7)

from logStore.database.database_handler import DatabaseHandler
from logStore.transconn.database_connector import DatabaseConnector
#from testfixtures import LogCapture
from logStore.funcs.event import Event, Meta, Content
from logStore.funcs.EventCreationTool import EventCreationTool, EventFactory
from logStore.appconn.chat_connection import ChatFunction
from logStore.appconn.feed_ctrl_connection import FeedCtrlConnection
from feedCtrl.uiFunctionsHandler import UiFunctionHandler
from logStore.transconn.database_connector import DatabaseConnector
from feedCtrl.eventCreationWrapper import EventCreationWrapper

folderG7 = os.path.join(dirname, '../../dependencies/04-logMerge/logMerge')
sys.path.append(folderG7)
from LogMerge import LogMerge

class BACCore:

    def __init__(self):
        self.pickle_file_names = ['personList.pkl', 'username.pkl']  # use to reset user or create new one
        self.switch = ["", "", ""]

    # checks if there is already an existing database by checking if there exists a masterfeed ID
    def exists_db(self):
        self._fcc = FeedCtrlConnection()
        master_feed_id = self._fcc.get_host_master_id()
        if master_feed_id is not None:
            return 1
        return 0

    # creates a new database and its first three masterfeed events, if there isn't already one.
    # otherwise it doesn't create a new one
    def setup_db(self, user_name=''):
        mas_id = self._fcc.get_host_master_id()
        if mas_id is not None:
            self.master_feed_id = self._fcc.get_host_master_id()
            self.db_connector = DatabaseConnector()
            self.user_name = self.get_user_name()
        else:
            make_dirs()
            self._ecf = EventFactory(None, DIR_MAIN + '/' + 'Keys', False)
            self._eventCreationWrapper = EventCreationWrapper(self._ecf)
            _firstEvent = self._eventCreationWrapper.create_MASTER()
            _secondEvent = self._eventCreationWrapper.create_radius(1)
            _thirdEvent = self._eventCreationWrapper.create_name(user_name)
            self._fcc.add_event(_firstEvent)
            self._fcc.add_event(_secondEvent)
            self._fcc.add_event(_thirdEvent)
            self.master_feed_id = self._fcc.get_host_master_id()
            self.db_connector = DatabaseConnector()
            self.user_name = user_name

    # creates a new feed (adds 2 events to the master feed and creates the first and second event of the new feed)
    def create_feed(self, article_feed_name):
        fcc = FeedCtrlConnection()
        ect = EventCreationTool()
        ect.set_path_to_keys(DIR_MAIN + '/' + 'Keys', False)

        event = self.db_connector.get_current_event(self.master_feed_id)
        ecf_master = EventFactory(event, DIR_MAIN + '/' + 'Keys', False)
        eventCreationWrapper = EventCreationWrapper(ecf_master)

        public_key = ect.generate_feed()
        new_feed_event = eventCreationWrapper.create_newFeed(public_key, 'bac_news')
        trust_feed_event = eventCreationWrapper.create_trust(public_key)
        first_event = ect.create_first_event(public_key, 'bac_news/new_article', {'master_feed': self.master_feed_id}) 

        fcc.add_event(new_feed_event)
        fcc.add_event(trust_feed_event)
        fcc.add_event(first_event)      

        # creates event containing list name, host name and creation date (second event of the newly created feed)
        ect = EventCreationTool()
        ect.set_path_to_keys(DIR_MAIN + '/' + 'Keys', False)
        dictionary = {  'host' : self.get_event_content(self.master_feed_id, 2)[1]['name'],
                        'list_name' : article_feed_name,
                        'date' : datetime.now().isoformat() }
        second_event = ect.create_event_from_previous(first_event, 'bac_news/new_article', dictionary)
        fcc.add_event(second_event)

    # creates an event, that is appended at the given feed (given with the feedname) with the content given as json file
    def create_event(self, feed_name, json_file):
        feed_id = self.get_id_from_feed_name(feed_name)
        event = self.db_connector.get_current_event(feed_id)

        ect = EventCreationTool()
        ect.set_path_to_keys(DIR_MAIN + '/' + 'Keys', False)
        new_event = ect.create_event_from_previous(event, 'bac_news/new_article', {'json': json_file})
        fcc = FeedCtrlConnection()
        fcc.add_event(new_event)

    # exports the content of the database to the given path as one or more pcap files
    def export_db_to_pcap(self, path):
        dictionary = {}
        feed_ids = self.get_all_feed_ids()
        for f_id in feed_ids:
            dictionary[f_id] = -1
        lm = LogMerge()
        lm.export_logs(path, dictionary)

    # imports pcap files from the given path to the database
    def import_from_pcap_to_db(self, path):
        lm = LogMerge()
        lm.import_logs(path)
        
    def get_all_feed_ids(self):
        return self.db_connector.get_all_feed_ids()

    def get_all_feed_name_host_tuples(self):
        feed_names = list()
        feed_ids = self.get_all_feed_ids()
        for feed_id in feed_ids:
            if self.get_event_content(feed_id, 0)[0] == "MASTER/MASTER":
                continue
            host = self.get_host_from_feed(feed_id)
            feed_names.append((self.get_feedname_from_id(feed_id), host))
        return feed_names

    def get_event_content(self, feed_id, seq_no):
        cbor_event = self.db_connector.get_event(feed_id, seq_no)
        event = Event.from_cbor(cbor_event)
        return event.content.content

    def get_feednames_from_host(self):
        feed_names = list()
        feed_ids = self.get_all_feed_ids()
        for feed_id in feed_ids:
            if self.get_event_content(feed_id, 0)[0] == "MASTER/MASTER":
                continue
            host = self.get_host_from_feed(feed_id)
            if host == self.user_name: #host of this feed is also host of this app
                feed_names.append(self.get_feedname_from_id(feed_id))
        return feed_names   
    
    def get_feedname_from_id(self, feed_id):
        return self.get_event_content(feed_id, 1)[1]["list_name"]

    def get_host_from_feed(self, feed_id):
        return self.get_event_content(feed_id, 1)[1]["host"]

    def get_id_from_feed_name(self, feed_name): #for own feed_ids
        feed_ids = self.get_all_feed_ids()
        for feed_id in feed_ids:
            if self.get_event_content(feed_id, 0)[0] == "MASTER/MASTER": # still need to do this, because master feed of other user could be in front of new feed in db of own host after import.
                continue
            host = self.get_host_from_feed(feed_id)
            if host == self.user_name:
                if feed_name == self.get_feedname_from_id(feed_id):
                    return feed_id
        return None

    def get_id_from_feed_name_and_host(self, feedname_host):
        feed_name = feedname_host[0]
        host = feedname_host[1]
        feed_ids = self.get_all_feed_ids()
        for feed_id in feed_ids:
            if self.get_event_content(feed_id, 0)[0] == "MASTER/MASTER":
                continue
            feed_host = self.get_host_from_feed(feed_id)
            if host == feed_host:
                if feed_name == self.get_feedname_from_id(feed_id):
                    return feed_id
        return None

    def get_json_files_from_feed(self, feedname_host):  #feedname_host = tuple with feed_name and its host
        json_files = list()
        feed_name = feedname_host[0]
        host = feedname_host[1]
        feed_id = self.get_id_from_feed_name_and_host((feed_name, host))
        max_seq_no = self.db_connector.get_current_seq_no(feed_id)
        if max_seq_no is None:
            max_seq_no = -1
        for i in range(2, max_seq_no + 1):
            json_files.append(self.get_json_from_event(feed_id, i))
        return json_files  

    def get_json_from_event(self, feed_id, seq_no):
        return self.get_event_content(feed_id, seq_no)[1]['json']
    
    def get_user_name(self):
        return(self.get_event_content(self.master_feed_id, 2)[1]["name"])