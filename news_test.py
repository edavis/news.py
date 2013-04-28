import unittest
import datetime

import news
import utils

class TestUtils(unittest.TestCase):
    def test_format_timestamp(self):
        # specific datetime
        now = datetime.datetime(2013, 4, 28, 10, 0, 0)
        self.assertEqual(utils.format_timestamp(now),
                         "20130428 100000")

        # timedelta
        now -= datetime.timedelta(seconds=30)
        self.assertEqual(utils.format_timestamp(now),
                         "20130428 095930")

        # string
        self.assertEqual(utils.format_timestamp("20130428 095930"),
                         "20130428 095930")

    def test_split_timestamp(self):
        now = datetime.datetime(2013, 4, 28, 10, 0, 0)
        self.assertEqual(utils.split_timestamp(now),
                         ("20130428", "100000"))
