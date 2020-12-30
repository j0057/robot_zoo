import time
import unittest

import mock

from robot_zoo import twitter
from robot_zoo.bot import hetluchtalarm

class TestHetLuchtalarm(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.luchtalarm = hetluchtalarm.Luchtalarm('hetluchtalarm', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_hoeuiii(self):
        result = self.luchtalarm.sound_alarm(self._time('2013-12-03T12:00:00Z'))
        self.assertTrue(result)
        self.api.post_statuses_update.assert_called_with(
            status='Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + ' '
                 + 'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + '1100'.replace('0', '\x20').replace('1', '\xad') # month
                 + '0001'.replace('0', '\x20').replace('1', '\xad') # year-2012
                 + '\xad')

    def test_oei(self):
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        with mock.patch('time.sleep'):
            result = self.luchtalarm.sound_alarm(self._time('2013-12-03T12:00:00Z'))
        self.assertFalse(result)

    def test_bevrijdingsdag_2014(self):
        self.luchtalarm.sound_alarm(self._time('2014-05-05T12:00:00Z'))
        self.api.post_statuses_update.assert_called_with(
            status=u"Bevrijdingsdag \u2014 vandaag geen luchtalarm")
