# Tests for LogMerge.py
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import os
import shutil
import unittest
import Event
import EventCreationToolV14
import LogMerge
import PCAP
from logStore.transconn.database_connector import DatabaseConnector
from logStore.verific.verify_insertion import Verification

TEST_FOLDERS_RELATIVE_PATHS = ['tmp_test_folder', 'tmp_test_folder_2', 'tmp_test_folder_3', 'tmp_test_folder_4']
# Paths for temporarily stored folders (used to keep testing files)


class LogMergeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lm = LogMerge.LogMerge()
        cls.dc = DatabaseConnector()
        cls.vf = Verification()
        cls.master_feed_id = cls.dc.get_master_feed_id()
        for folder_path in TEST_FOLDERS_RELATIVE_PATHS:
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

    def test_importing_master_feeds(self):
        ef = EventCreationToolV14.EventFactory()
        event_one = ef.next_event('MASTER/MASTER', {})
        event_two = ef.next_event('MASTER/Radius', {'radius': 2})
        event_three = ef.next_event('MASTER/Name', {'name': 'MICHAEL'})
        PCAP.PCAP.write_pcap(TEST_FOLDERS_RELATIVE_PATHS[0] + '/okokok', [event_one, event_two, event_three])
        self.assertFalse(ef.get_feed_id() in self.lm.get_database_status())
        self.lm.import_logs(TEST_FOLDERS_RELATIVE_PATHS[0])
        self.assertTrue(ef.get_feed_id() in self.lm.get_database_status())
        self.assertEqual(self.lm.get_database_status()[ef.get_feed_id()], 2)

    def test_importing_trusted_feeds(self):
        ef = EventCreationToolV14.EventFactory()
        master_event_one = ef.next_event('MASTER/MASTER', {})
        master_event_two = ef.next_event('MASTER/Radius', {'radius': 2})
        master_event_three = ef.next_event('MASTER/Name', {'name': 'MICHAEL'})

        ef2 = EventCreationToolV14.EventFactory()
        event_one = ef2.next_event('chat/MASTER', ef.get_feed_id())
        event_two = ef2.next_event('chat/okletsgo', {'messagekey': 759432, 'timestampkey': 2345, 'chat_id': 745})
        event_three = ef2.next_event('chat/okletsgo', {'messagekey': 3422, 'timestampkey': 4354, 'chat_id': 54332})

        master_event_four = ef.next_event('MASTER/NewFeed', {'feed_id': ef2.get_feed_id(), 'app_name': 'chat'})

        PCAP.PCAP.write_pcap(TEST_FOLDERS_RELATIVE_PATHS[1] + '/okokok',
                             [master_event_one, master_event_two, master_event_three, master_event_four,
                              event_one, event_two, event_three])
        self.lm.import_logs(TEST_FOLDERS_RELATIVE_PATHS[1])

        self.assertFalse(ef2.get_feed_id() in self.lm.get_database_status())

        own_master_event = self.dc.get_current_event(self.dc.get_master_feed_id())

        ef3 = EventCreationToolV14.EventFactory(own_master_event)
        trust_event = ef3.next_event('MASTER/Trust', {'feed_id': ef2.get_feed_id()})
        self.dc.add_event(trust_event)
        self.lm.import_logs(TEST_FOLDERS_RELATIVE_PATHS[1])

        self.assertTrue(ef2.get_feed_id() in self.lm.get_database_status())

    def test_exporting_master_feed(self):
        own_master_event = self.dc.get_current_event(self.master_feed_id)
        ef = EventCreationToolV14.EventFactory(own_master_event)
        next_event = ef.next_event('MASTER/Name', {'name': 'ThisIsAValidName'})
        self.dc.add_event(next_event)

        self.lm.export_logs(TEST_FOLDERS_RELATIVE_PATHS[2], {})

        events_list = PCAP.PCAP.read_pcap(os.path.join(TEST_FOLDERS_RELATIVE_PATHS[2],
                                                       self.master_feed_id.hex() + '_v.pcap'))
        for event in events_list:
            self.assertTrue(Event.Event.from_cbor(event).meta.feed_id == self.master_feed_id)
        self.assertGreater(len(events_list), 3)

    def test_exporting_trusted_feeds(self):
        ef = EventCreationToolV14.EventFactory()
        master_event_one = ef.next_event('MASTER/MASTER', {})
        master_event_two = ef.next_event('MASTER/Radius', {'radius': 2})
        master_event_three = ef.next_event('MASTER/Name', {'name': 'NORBERT'})

        ef2 = EventCreationToolV14.EventFactory()
        event_one = ef2.next_event('chat/MASTER', ef.get_feed_id())
        event_two = ef2.next_event('chat/okletsgo', {'messagekey': 5435, 'timestampkey': 6543, 'chat_id': 45634})
        event_three = ef2.next_event('chat/okletsgo', {'messagekey': 4356, 'timestampkey': 45643, 'chat_id': 66546})

        master_event_four = ef.next_event('MASTER/NewFeed', {'feed_id': ef2.get_feed_id(), 'app_name': 'chat'})

        own_master_event = self.dc.get_current_event(self.dc.get_master_feed_id())
        ef3 = EventCreationToolV14.EventFactory(own_master_event)
        trust_event = ef3.next_event('MASTER/Trust', {'feed_id': ef2.get_feed_id()})
        self.dc.add_event(trust_event)

        self.dc.add_event(master_event_one)
        self.dc.add_event(master_event_two)
        self.dc.add_event(master_event_three)
        self.dc.add_event(master_event_four)
        self.dc.add_event(event_one)
        self.dc.add_event(event_two)
        self.dc.add_event(event_three)

        self.lm.export_logs(TEST_FOLDERS_RELATIVE_PATHS[3], {ef2.get_feed_id(): -1})

        events_list = PCAP.PCAP.read_pcap(os.path.join(TEST_FOLDERS_RELATIVE_PATHS[3],
                                                       ef2.get_feed_id().hex() + '_v.pcap'))
        for event in events_list:
            self.assertTrue(Event.Event.from_cbor(event).meta.feed_id == ef2.get_feed_id())
        self.assertEqual(len(events_list), 3)

    @classmethod
    def tearDownClass(cls):  # Deletes testing files
        (_, _, filenames) = next(os.walk(os.getcwd()))
        for filename in filenames:
            if filename.endswith('.key') or filename.endswith('.sqlite') or filename.endswith('.pcap'):
                os.remove(filename)
        for folder_path in TEST_FOLDERS_RELATIVE_PATHS:
            shutil.rmtree(folder_path)


if __name__ == '__main__':
    # Run all tests from inside this file
    unittest.main()
