import time
import unittest

import mock

from robot_zoo import twitter
from robot_zoo.bot import deoldehove

class TestDeOldehove(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.api.log.return_value = None
        self.api.config = { 
            'default': {
                'separator': ' ',
                'sound' : 'BOING!'
            },
            'ljouwert culinair 2010': {
                'separator': ' ',
                'sound': 'HAP'
            },
            'metal': {
                'separator': ' ',
                'sound': 'METAL!'
            }
        }
        self.api.post_statuses_update.return_value = True

        self.deoldehove = deoldehove.DeOldehove('deoldehove', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_23_00(self):
        t = self._time('2013-12-15T23:00:00Z')
        self.deoldehove.sound_clock(t)
        self.api.post_statuses_update.assert_called_once_with(
            status=' '.join([u'BOING!']*11))

    def test_00_00(self):
        t = self._time('2013-12-16T00:00:00Z')
        self.deoldehove.sound_clock(t)
        self.api.post_statuses_update.assert_called_once_with(
            status=' '.join([u'BOING!']*12))

    def test_half_hours(self):
        t1 = self._time('2013-12-15T01:30:00Z')
        t2 = self._time('2013-12-15T02:30:00Z')
        t3 = self._time('2013-12-15T03:30:00Z')
        t4 = self._time('2013-12-15T04:30:00Z')

        self.deoldehove.sound_clock(t1)
        self.api.post_statuses_update.assert_called_with(status=u'BOING!\u2002')

        self.deoldehove.sound_clock(t2)
        self.api.post_statuses_update.assert_called_with(status=u'BOING!\u2002\u2002')

        self.deoldehove.sound_clock(t3)
        self.api.post_statuses_update.assert_called_with(status=u'BOING!\u2002\u2002\u2002')

        self.deoldehove.sound_clock(t4)
        self.api.post_statuses_update.assert_called_with(status=u'BOING!\u2002\u2002\u2002\u2002')

    def test_01_00_lwd_culinair(self):
        t = self._time('2013-06-09T14:00:00Z')
        self.deoldehove.sound_clock_lwd_culinair(t)
        self.api.post_statuses_update.assert_called_once_with(status=u'HAP HAP')

    def test_01_00_into_the_grave(self):
        t = self._time('2013-06-09T14:00:00Z')
        self.deoldehove.sound_clock_into_the_grave(t)
        self.api.post_statuses_update.assert_called_once_with(status=u'METAL! METAL!')
