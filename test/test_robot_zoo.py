import time
import unittest

import mock

from robot_zoo import twitter
#twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_ERROR

import robot_zoo.__main__

class TestRobotZooUTC(unittest.TestCase):
    def setUp(self):
        self.executor = mock.Mock()
        self.cron_utc = robot_zoo.__main__.RobotZooUTC('cron_utc', self.executor)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_y2k38warning_yearly(self):
        t = self._time('2014-01-19T03:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.yearly])

    def test_y2k38warning_monthly(self):
        t = self._time('2037-01-19T03:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.monthly])

    def test_y2k38warning_daily(self):
        t = self._time('2037-12-19T03:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.daily])

    def test_y2k38warning_hourly(self):
        t = self._time('2038-01-18T03:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.hourly])

    def test_y2k38warning_every_minute(self):
        t = self._time('2038-01-19T02:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.every_minute])

    def test_y2k38warning_every_second(self):
        t = self._time('2038-01-19T03:13:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.every_minute])

    def test_y2k38warning_zero(self):
        t = self._time('2038-01-19T03:14:07Z')
        result = list(self.cron_utc.get_runnable_actions(t))
        self.assertEqual(result, [robot_zoo.__main__.y2k38warning.zero])
        
        
