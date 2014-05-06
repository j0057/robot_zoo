import time
import unittest

import mock

from robot_zoo import twitter
from robot_zoo.bot import msvlieland

class TestMsVlieland(unittest.TestCase):
    def setUp(self):
        self.data = mock.Mock()
        self.data.departures = {
            (2013,12,02): [(9,0),(14,15),(19,0)],
            (2013,12,03): [(9,0)]
        }

        self.api = mock.Mock()
        self.api.post_statuses_update.return_value = True

        self.msvlieland = msvlieland.MsVlieland('msvlieland', self.api, self.data)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_sound_horn_dynamic(self):
        self.msvlieland.sound_horn_dynamic(self._time('2013-12-02T09:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status=u'TOET TOET TOET')

        self.msvlieland.sound_horn_dynamic(self._time('2013-12-02T14:15:00Z'))
        self.api.post_statuses_update.assert_called_with(status=u'TOET TOET TOET\u2002')

        self.msvlieland.sound_horn_dynamic(self._time('2013-12-02T19:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status=u'TOET TOET TOET\u2002\u2002')

        self.msvlieland.sound_horn_dynamic(self._time('2013-12-03T09:00:00Z'))
        self.api.post_statuses_update.assert_called_with(status=u'TOET TOET TOET')

    def test_sound_horn_dynamic_wrong_date(self):
        self.msvlieland.sound_horn_dynamic(self._time('2013-12-01T09:00:00Z'))
        self.assertFalse(self.api.post_statuses_update.called)

    def test_sound_horn_dynamic_wrong_time(self):
        self.msvlieland.sound_horn_dynamic(self._time('2013-12-03T14:15:00Z'))
        self.assertFalse(self.api.post_statuses_update.called)

    def test_update_departures(self):
        self.msvlieland.update_departures(self._time('2013-12-03T00:00:00Z'))
        self.assertEqual(self.data.date, (2013, 12, 3))

    def test_update_departures_for_today(self):
        self.msvlieland.update_departures_for_today(self._time('2013-12-03T00:00:00Z'))
        self.data.update_today.assert_called_with(2013, 12, 3)

class TestMsVlielandData(unittest.TestCase):
    def setUp(self):
        self.get_patch = mock.patch('requests.get')
        self.get = self.get_patch.start()
        self.get.return_value.json.return_value = {
            "outwards": [
                { "departure_time": "2014-05-06 09:00:00", "other": "Veerdienst" },
                { "departure_time": "2014-05-06 14:15:00", "other": "Veerdienst" },
                { "departure_time": "2014-05-06 19:00:00", "other": "Veerdienst" } ],
            "retour": [] }

        self.data = msvlieland.MsVlielandData(log=mock.Mock())

    def tearDown(self):
        self.get_patch.stop()

    def test_get_data(self):
        result = self.data.get_data(2014, 5, 6)
        self.assertEqual(result, ((2014, 5, 6), [(9,0), (14,15), (19,0)]))

