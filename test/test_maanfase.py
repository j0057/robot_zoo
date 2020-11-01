import time
import unittest

import mock

import twitter
import bot.maanfase

class TestMaanfaseModel(unittest.TestCase):
    def setUp(self):
        self.model = bot.maanfase.MoonModel()

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
        self.maanfase = bot.maanfase.Maanfase('maanfase', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_no_phase(self):
        result = self.maanfase.post_phase(self._time('2013-12-17T10:29:00Z'))
        self.assertTrue(result)
        self.assertFalse(self.api.post_statuses_update.called)

    def test_no_phase_year_already_set(self):
        self.maanfase.moon.year = 2013
        result = self.maanfase.post_phase(self._time('2013-12-17T10:29:00Z'))
        self.assertTrue(result)
        self.assertFalse(self.api.post_statuses_update.called)

    def test_last_full_moon_of_2013(self):
        result = self.maanfase.post_phase(self._time('2013-12-17T10:28:00Z'))
        self.assertTrue(result)
        self.assertTrue(self.api.post_statuses_update.called)
        self.api.post_statuses_update.assert_called_once_with(
            status='10:28:05 ― volle maan.')

    def test_failure(self):
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        with mock.patch('time.sleep'):
            result = self.maanfase.post_phase(self._time('2013-12-17T10:28:00Z'))
        self.assertFalse(result)
