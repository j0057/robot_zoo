import time
import unittest

import mock

import twitter
import bot.msvlieland

class TestMsVlieland(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.api.post_statuses_update.return_value = True

        self.msvlieland = bot.msvlieland.MsVlieland('msvlieland', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_noop(self):
        result = self.msvlieland._()
        self.assertTrue(result)

    def test_stuffing(self):
        self.msvlieland.sound_horn(self._time('2013-12-02T09:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status='TOET TOET TOET')

        self.msvlieland.sound_horn(self._time('2013-12-02T14:15:00Z'))
        self.api.post_statuses_update.assert_called_with(status='TOET TOET TOET\\u2002')

        self.msvlieland.sound_horn(self._time('2013-12-02T19:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status='TOET TOET TOET\\u2002\\u2002')

        self.msvlieland.sound_horn(self._time('2013-12-03T09:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status='TOET TOET TOET')

class TestMsVlieland_Fail(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.api.post_statuses_update.side_effect = twitter.FailWhale

        self.msvlieland = bot.msvlieland.MsVlieland('msvlieland', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_fail(self):
        result = self.msvlieland.sound_horn(self._time('2013-12-02T09:00:00Z'))
        self.assertFalse(result)
