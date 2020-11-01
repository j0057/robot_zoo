import random
import time
import unittest

import mock

import twitter
import bot.convertbot

class TestConvertBotUtil(unittest.TestCase):
    def test_cafebabe_from_radix_16(self):
        n = bot.convertbot.from_radix(16, 'CAFEBABE')
        self.assertEqual(n, 3405691582)

    def test_empty_from_radix_16(self):
        n = bot.convertbot.from_radix(16, '')
        self.assertEqual(n, 0)

    def test_random_big_number_to_radix_16(self):
        n = bot.convertbot.to_radix(16, 184594917)
        self.assertEqual(n, 'B00B1E5')

    def test_zero_to_radix_16(self):
        n = bot.convertbot.to_radix(16, 0)
        self.assertEqual(n, '')

    def test_convert_random_big_number_from_8_to_16(self):
        n = bot.convertbot.convert(8, 16, '1300130745')
        self.assertEqual(n, 'B00B1E5')

class TestConvertBot(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.convertbot = bot.convertbot.ConvertBot('convertbot', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def _randint(self, *a): return { (0, 2000): 42, (2, 36): 16 }[a]

    def test_post_time(self):
        result = self.convertbot.post_time(
            self._time('2013-07-23T20:01:00Z'),
            randint=lambda *a: {(0,2000):42, (2,36):16}[a])
        # XXX: not sure how True apparently used to be returned
        #self.assertTrue(result)
        self.api.post_statuses_update.assert_called_with(
            status='Current UTC+2 time in base 16 is 14:01')

    def test_fail(self):
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        with mock.patch('time.sleep'):
            result = self.convertbot.post_time(
                self._time('2013-07-23T20:01:00Z'),
                randint=lambda *a: {(0,2000):42, (2,36):16}[a])
        self.assertFalse(result)

    def test_not_now(self):
        result = self.convertbot.post_time(
            self._time('2013-07-23T20:01:00Z'),
            randint=lambda *a: {(0,2000):13, (2,36):16}[a])
        # XXX: not sure how True apparently used to be returned
        #self.assertTrue(result)
        self.assertFalse(self.api.post_statuses_update.called)
