import time
import unittest

import mock

import twitter

class TestRetry(unittest.TestCase):
    @twitter.retry
    def spam(self):
        return 42 

    @twitter.retry
    def albatross(self):
        raise twitter.FailWhale()

    @twitter.retry
    def spanish_inquisition(self):
        if self.i < 4:
            raise twitter.FailWhale()
        else:
            self.i += 1

    def setUp(self):
        self.i = 0
        self.api = mock.Mock()

    def test_retry(self):
        r = self.spam()
        self.assertEqual(r, 42)

    def test_fail(self):
        with mock.patch('time.sleep'):
            r = self.albatross()
        self.assertFalse(r)

    def test_ultimately_ok(self):
        with mock.patch('time.sleep'):
            self.spanish_inquisition()

class TestTwitterAPI(unittest.TestCase):
    def setUp(self):
        self.api = twitter.TwitterAPI('johndoeveloper')

    def test_wrong_name(self):
        with self.assertRaises(AttributeError):
            self.api.delete_spanish_inquisition()

    def test_post_tweet(self):
        with mock.patch('oauth1.Oauth1') as oauth1:
            self.api.post_statuses_update(status='test')

            oauth1.assert_called_with(config=mock.ANY, stream=False)
            oauth1.return_value.request.assert_called_with(
                'POST',
                'https://api.twitter.com/1.1/statuses/update.json',
                headers={'Accept': 'application/json'},
                post={'status': 'test'})
