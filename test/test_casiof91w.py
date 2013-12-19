import time
import unittest

import mock

import twitter
import bot.casio_f91w

class TestCasioF91W_OK(unittest.TestCase):
    mentions = [
        {'id':'1',
         'user': {'screen_name':'test1'},
         'text': u'BLA'},

        {'id':'2',
         'user': {'screen_name':'test2'},
         'text': u'@casio_f91w alarm 20:00 +0100'},

        {'id':'3',
         'user': {'screen_name':'test3'},
         'text': u'@casio_f91w alarm 08:00 PM +0100'},

        {'id':'4',
         'user': {'screen_name':'test4'},
         'text': u'@casio_f91w alarm 08:00 PM'},

        {'id':'5',
         'user': {'screen_name':'test5'},
         'text': u'@casio_f91w alarm 20:00'},

        {'id':'6',
         'user': {'screen_name':'test6'},
         'text': u'@casio_f91w alarm 03:00 PM -0400'},

        {'id':'7',
         'user': {'screen_name':'test7'},
         'text': u'@casio_f91w alarm 02:00 AM -0400'},

        {'id':'8',
         'user': {'screen_name':'test8'},
         'text': u'@casio_f91w alarm 12:00 AM'}
    ]

    def setUp(self):
        self.api = mock.Mock()

        def get_mentions(count=200, since_id=None):
            if not since_id:
                return [TestCasioF91W_OK.mentions[0]]
            else:
                return [ m for m in TestCasioF91W_OK.mentions
                         if int(m['id']) > int(since_id) ]

        config = {
            'last_mention': '',
            'alarms': {}
        }

        self.api.log.return_value = None
        self.api.post_statuses_update.return_value = True
        self.api.get_statuses_mentions_timeline = get_mentions
        self.api.config.__getitem__ = lambda s, i: config.__getitem__(i)
        self.api.config.__setitem__ = lambda s, i, v: config.__setitem__(i, v)

        self.casiof91w = bot.casio_f91w.CasioF91W('casiof91w', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_send_beep(self):
        t = self._time('2012-07-23T20:00:00Z')
        result = self.casiof91w.send_beep(t)
        self.assertTrue(result)
        self.api.post_statuses_update.assert_called_once_with(
            status='BEEP BEEP! MO 23 20:00:00')

    def test_get_mentions(self):
        result = self.casiof91w.get_mentions()
        self.assertEquals(1, len(list(result)))
        self.assertEquals('1', self.api.config['last_mention'])
        result = self.casiof91w.get_mentions()
        self.assertEquals(7, len(list(result)))
        self.assertEquals('8', self.api.config['last_mention'])
        result = self.casiof91w.get_mentions()
        self.assertEquals(0, len(list(result)))
        self.assertEquals('8', self.api.config['last_mention'])

    def test_parse_tweet_for_alarm_1(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[0])
        self.assertEquals((None, self.mentions[0]), result)

    def test_parse_tweet_for_alarm_2(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[1])
        self.assertEquals(((20, 0), self.mentions[1]), result)

    def test_parse_tweet_for_alarm_3(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[2])
        self.assertEquals(((20, 0), self.mentions[2]), result)

    def test_parse_tweet_for_alarm_4(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[3])
        self.assertEquals(((20, 0), self.mentions[3]), result)

    def test_parse_tweet_for_alarm_5(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[4])
        self.assertEquals(((20, 0), self.mentions[4]), result)

    def test_parse_tweet_for_alarm_6_ast(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[5])
        self.assertEquals(((20, 0), self.mentions[5]), result)

    def test_parse_tweet_for_alarm_7_am(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[6])
        self.assertEquals(((7, 0), self.mentions[6]), result)

    def test_parse_tweet_for_alarm_8_noon(self):
        result = self.casiof91w.parse_tweet_for_alarm(self.mentions[7])
        self.assertEquals(((0, 0), self.mentions[7]), result)

    def test_save_alarm(self):
        self.casiof91w.save_alarm((20, 0), self.mentions[1])
        self.assertEqual('', self.api.config['last_mention'])
        self.assertEqual({
            '20:00': {
                '2': 'test2'
            }
        }, self.api.config['alarms'])

    def test_handle_mentions(self):
        result = self.casiof91w.handle_mentions(self._time('2012-07-23T20:00:00Z'))
        
        self.assertTrue(result)
        self.assertEqual(0, len(self.api.config['alarms']))
        self.assertEqual('1', self.api.config['last_mention'])

        result = self.casiof91w.handle_mentions(self._time('2012-07-23T20:00:00Z'))
        
        self.assertTrue(result)
        self.assertEqual(3, len(self.api.config['alarms']))
        self.assertEqual('8', self.api.config['last_mention'])

        self.assertEqual({
            '00:00': {
                '8': 'test8'
            },
            '07:00': {
                '7': 'test7'
            },
            '20:00': {
                '2': 'test2',
                '3': 'test3',
                '4': 'test4',
                '5': 'test5',
                '6': 'test6'
            }
        }, self.api.config['alarms'])

        self.assertTrue(self.api.save.called)

    def test_send_alarms(self):
        self.casiof91w.handle_mentions(self._time('2012-07-23T20:00:00Z'))
        self.casiof91w.handle_mentions(self._time('2012-07-23T20:00:05Z'))

        result = self.casiof91w.send_alarms(self._time('2012-07-24T20:00:00Z'))

        self.assertTrue(result)

        self.api.post_statuses_update.assert_any_call(
            in_reply_to_status_id='2',
            status=u'@test2 BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP!')

        self.api.post_statuses_update.assert_any_call(
            in_reply_to_status_id='3',
            status=u'@test3 BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP!')

        self.api.post_statuses_update.assert_any_call(
            in_reply_to_status_id='4',
            status=u'@test4 BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP!')

        self.api.post_statuses_update.assert_any_call(
            in_reply_to_status_id='5',
            status=u'@test5 BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP!')

        self.api.post_statuses_update.assert_any_call(
            in_reply_to_status_id='6',
            status=u'@test6 BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP! BEEP BEEP!')

        self.api.save.assert_any_call()

        self.assertEqual({
            '00:00': {
                '8': 'test8'
            },
            '07:00': {
                '7': 'test7'
            }
        }, self.api.config['alarms'])

    def test_send_no_alarms(self):
        self.casiof91w.handle_mentions(self._time('2012-07-23T18:00:00Z'))
        self.casiof91w.handle_mentions(self._time('2012-07-23T18:00:05Z'))

        result = self.casiof91w.send_alarms(self._time('2012-07-24T19:00:00Z'))

        self.assertTrue(result)
        self.assertTrue(not self.api.post_statuses_update.called)
        

class TestCasioF91W_Fail(unittest.TestCase):
    def setUp(self):
        config = {
            'last_mention': '',
            'alarms': {
                '20:00': {'42': '@j0057m'}
            }
        }

        self.api = mock.Mock()
        self.api.log.return_value = None
        self.api.post_statuses_update.side_effect = twitter.FailWhale
        self.api.get_statuses_mentions_timeline.side_effect = twitter.FailWhale
        self.api.config.__getitem__ = lambda s, i: config.__getitem__(i)
        self.casiof91w = bot.casio_f91w.CasioF91W('casiof91w', self.api)

    def _time(self, s):
        return time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

    def test_send_beep(self):
        t = self._time('2012-07-23T20:00:00Z')
        result = self.casiof91w.send_beep(t)
        self.assertFalse(result)
        self.api.post_statuses_update.assert_called_once_with(status='BEEP BEEP! MO 23 20:00:00')
        self.api.error.assert_called_once_with('FAIL WHALE: {0}', '()')

    def test_send_alarms(self):
        t = self._time('2012-07-23T20:00:00Z')
        result = self.casiof91w.send_alarms(t)
        self.assertTrue(result)

    def test_handle_mentions(self):
        t = self._time('2012-07-23T20:00:00Z')
        result = self.casiof91w.handle_mentions(t)
        self.assertFalse(result)

    
