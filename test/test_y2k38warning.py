
import time
import unittest

import mock

import twitter
import bot.y2k38warning

class TestY2K38Warning(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.api.log.return_value = None
        self.api.post_statuses_update.return_value = True

        self.y2k38warning = bot.y2k38warning.Y2K38Warning('y2k38warning', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_yearly_24(self):
        self.y2k38warning.yearly(self._time('2014-01-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 24 years remaining until Y2K38!')

    def test_yearly_1(self):
        self.y2k38warning.yearly(self._time('2037-01-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 year remaining until Y2K38!')

    def test_monthly_12(self):
        self.y2k38warning.monthly(self._time('2037-01-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 12 months remaining until Y2K38!')

    def test_monthly_1(self):
        self.y2k38warning.monthly(self._time('2037-12-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 month remaining until Y2K38!')
   
    def test_daily_31(self): 
        self.y2k38warning.daily(self._time('2037-12-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 31 days remaining until Y2K38!')

    def test_daily_1(self):
        self.y2k38warning.daily(self._time('2038-01-18T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 day remaining until Y2K38!')

    def test_hourly_24(self):
        self.y2k38warning.hourly(self._time('2038-01-18T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 24 hours remaining until Y2K38!')

    def test_hourly_1(self):
        self.y2k38warning.hourly(self._time('2038-01-19T02:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 hour remaining until Y2K38!')

    def test_every_minute_60(self):
        self.y2k38warning.every_minute(self._time('2038-01-19T02:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 60 minutes remaining until Y2K38!')

    def test_every_minute_1(self):
        self.y2k38warning.every_minute(self._time('2038-01-19T03:13:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 minute remaining until Y2K38!')

    def test_every_second_60(self):
        self.y2k38warning.every_second(self._time('2038-01-19T03:13:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 60 seconds remaining until Y2K38!')

    def test_every_second_1(self):
        self.y2k38warning.every_second(self._time('2038-01-19T03:14:06Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Only 1 second remaining until Y2K38!')

    def test_zero(self):
        self.y2k38warning.zero(self._time('2038-01-19T03:14:07Z'))
        self.api.post_statuses_update.assert_called_once_with(
            status='Y2K38 is here! Watch out for falling airplanes!')

class Y2K38WarningFail(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.api.log.return_value = None
        self.api.post_statuses_update.side_effect = twitter.FailWhale

        self.y2k38warning = bot.y2k38warning.Y2K38Warning('y2k38warning', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_fail_whale(self):
        self.y2k38warning.every_second(self._time('2038-01-19T03:14:06Z'))
        self.api.log.assert_called_with('FAIL WHALE: {0}', ())
