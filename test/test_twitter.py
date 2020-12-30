import time
import unittest

import mock

from robot_zoo import twitter
from robot_zoo import oauth1

class TestRetry(unittest.TestCase):
    @twitter.retry
    def spam(self):
        return 42

    @twitter.retry
    def albatross(self):
        raise twitter.FailWhale()

    @twitter.retry
    def spanish_inquisition(self):
        self.i += 1
        if self.i < 4:
            raise twitter.FailWhale("Shit's fucked!")
        return self.i

    def setUp(self):
        self.i = 0
        self.log = mock.Mock()

    def test_retry(self):
        r = self.spam()
        self.assertEqual(r, 42)

    def test_fail(self):
        with mock.patch('time.sleep'):
            r = self.albatross()
        self.assertFalse(r)
        self.assertTrue(self.log.info.called)

    def test_ultimately_ok(self):
        with mock.patch('time.sleep'):
            r = self.spanish_inquisition()
        self.assertEqual(r, 4)
        self.assertTrue(self.log.error.called)

class TestTwitterAPI(unittest.TestCase):
    def setUp(self):
        self.api = twitter.TwitterAPI('johndoeveloper')

    def test_wrong_name(self):
        with self.assertRaises(AttributeError):
            self.api.delete_spanish_inquisition()

    def test_post_tweet(self):
        with mock.patch('robot_zoo.oauth1.Oauth1') as Oauth1:
            self.api.post_statuses_update(status='test')

            Oauth1.assert_called_with(config=mock.ANY, stream=False)
            Oauth1.return_value.request.assert_called_with(
                'POST',
                'https://api.twitter.com/1.1/statuses/update.json',
                headers={'Accept': 'application/json'},
                post={'status': b'test'})
