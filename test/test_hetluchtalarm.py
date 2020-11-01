import time
import unittest

import mock

import twitter
import bot.hetluchtalarm

class TestHetLuchtalarm(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.luchtalarm = bot.hetluchtalarm.Luchtalarm('hetluchtalarm', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_hoeuiii(self):
        result = self.luchtalarm.sound_alarm(self._time('2013-12-03T12:00:00Z'))
        self.assertTrue(result)
        self.api.post_statuses_update.assert_called_with(
            status='Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + ' '
                 + 'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + '1100'.replace('0', '\u0020').replace('1', '\u2002') # month
                 + '0001'.replace('0', '\u0020').replace('1', '\u2002') # year-2012
                 + '\u2002')

    def test_oei(self):
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        with mock.patch('time.sleep'):
            result = self.luchtalarm.sound_alarm(self._time('2013-12-03T12:00:00Z'))
        self.assertFalse(result)

    def test_pasen_2013(self):
        result = self.luchtalarm.tweede_paasdag_2013(self._time('2013-12-03T12:00:00Z'))
        self.assertTrue(result)
        self.api.post_statuses_update.assert_called_with(
            status='Vandaag als het goed is geen luchtalarm, vrolijk Pasen!')

    def test_paasfaal_2013(self):
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        with mock.patch('time.sleep'):
            result = self.luchtalarm.tweede_paasdag_2013(self._time('2013-12-03T12:00:00Z'))
        self.assertFalse(result)
