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
        self.luchtalarm.sound_alarm(self._time('2013-12-03T12:00:00Z'))
        self.api.post_statuses_update.assert_called_with(
            status=u'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + u' '
                 + u'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
                 + u'1100'.replace('0', u'\u0020').replace('1', u'\u2002') # month
                 + u'0001'.replace('0', u'\u0020').replace('1', u'\u2002') # year-2012
                 + u'\u2002')

    def test_pasen_2013(self):
        self.luchtalarm.tweede_paasdag_2013(self._time('2013-12-03T12:00:00Z'))
        self.api.post_statuses_update.assert_called_with(
            status='Vandaag als het goed is geen luchtalarm, vrolijk Pasen!')

