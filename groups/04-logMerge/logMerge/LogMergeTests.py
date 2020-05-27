# Tests for LogMerge.py
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import os
import shutil
import unittest
import EventCreationToolV14
import LogMerge
import PCAP
from logStore.transconn.database_connector import DatabaseConnector

TEST_FOLDER_RELATIVE_PATH = 'tmp_test_folder'  # Path for temporarily stored folder (used to keep testing key files)


class LogMergeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lm = LogMerge.LogMerge()
        cls.dc = DatabaseConnector()
        cls.master_feed_id = cls.dc.get_master_feed_id()
        if not os.path.exists(TEST_FOLDER_RELATIVE_PATH):
            os.mkdir(TEST_FOLDER_RELATIVE_PATH)

    def test_importing_master_feeds(self):
        ef = EventCreationToolV14.EventFactory()
        event_one = ef.next_event('MASTER/MASTER', {})
        event_two = ef.next_event('MASTER/Radius', {'radius': 2})
        event_three = ef.next_event('MASTER/Name', {'name': 'MICHAEL'})
        PCAP.PCAP.write_pcap(TEST_FOLDER_RELATIVE_PATH + '/okokok', [event_one, event_two, event_three])
        self.assertFalse(ef.get_feed_id() in self.lm.get_database_status())
        print(self.lm.get_database_status())
        self.lm.import_logs(TEST_FOLDER_RELATIVE_PATH)
        self.assertTrue(ef.get_feed_id() in self.lm.get_database_status())
        self.assertEqual(self.lm.get_database_status()[ef.get_feed_id()], 2)
        print(self.lm.get_database_status())

    def test_importing_trusted_feeds(self):
        pass

    def test_exporting_master_feeds(self):
        pass

    def test_exporting_trusted_feeds(self):
        pass

    def test_always_export_master_feeds(self):
        pass

    @classmethod
    def tearDownClass(cls):  # Deletes testing files
        (_, _, filenames) = next(os.walk(os.getcwd()))
        for filename in filenames:
            if filename.endswith('.key') or filename.endswith('.sqlite') or filename.endswith('.pcap'):
                os.remove(filename)
        shutil.rmtree(TEST_FOLDER_RELATIVE_PATH)


if __name__ == '__main__':
    # Run all tests from inside this file
    unittest.main()
