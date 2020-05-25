# Tests for LogMerge.py
# Authors: Günes Aydin, Joey Zgraggen, Nikodem Kernbach
# VERSION: 1.0

import os
import unittest
import LogMerge


class LogMergeTests(unittest.TestCase):

    def setUp(self):
        self.lm = LogMerge.LogMerge()

    def test_something_1(self):
        pass

    def test_something_2(self):
        pass

    @classmethod
    def tearDownClass(cls):  # Deletes testing files
        (_, _, filenames) = next(os.walk(os.getcwd()))
        for filename in filenames:
            if filename.endswith('.key') or filename.endswith('.sqlite') or filename.endswith('.pcap'):
                os.remove(filename)


if __name__ == '__main__':
    # Run all tests from inside this file
    unittest.main()
