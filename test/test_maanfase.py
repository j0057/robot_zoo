import time
import unittest

import mock

from robot_zoo import twitter
from robot_zoo.bot import maanfase

class TestMaanfaseModel(unittest.TestCase):
    def setUp(self):
        self.model = maanfase.MoonModel()

    def test_last_full_moon_of_2013(self):
        self.model.year = 2013

        h, m, s, p = self.model[2013, 12, 17, 10, 28]

        self.assertEqual(h, 10)
        self.assertEqual(m, 28)
        self.assertEqual(s, 5)
        self.assertEqual(p, 2)

    def test_no_phase(self):
        self.model.year = 2013

        result = self.model[2013, 12, 17, 10, 29]

        self.assertEqual(result, None)

class TestMaanfase(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.maanfase = maanfase.Maanfase('maanfase', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_no_phase(self):
        self.maanfase.post_phase(self._time('2013-12-17T10:29:00Z'))
        self.assertFalse(self.api.post_statuses_update.called)

    def test_no_phase_year_already_set(self):
        self.maanfase.moon.year = 2013
        self.maanfase.post_phase(self._time('2013-12-17T10:29:00Z'))
        self.assertFalse(self.api.post_statuses_update.called)

    def test_last_full_moon_of_2013(self):
        self.maanfase.post_phase(self._time('2013-12-17T10:28:00Z'))
        self.assertTrue(self.api.post_statuses_update.called)
        self.api.post_statuses_update.assert_called_once_with(
            status=u'Om 10:28:05 is het volle maan.')
        
    #def test_failure(self):
    #   self.api.post_statuses_update.side_effect = twitter.FailWhale
    #   result = self.maanfase.post_phase(self._time('2013-12-17T10:28:00Z'))
    #   self.assertFalse(result)
