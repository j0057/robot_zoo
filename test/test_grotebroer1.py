import time
import unittest
import re
import queue

import mock

import twitter
import bot.grotebroer1

class TestGroteBroer1_UserStream(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.userstream = mock.Mock()
        self.aivd = bot.grotebroer1.UserStream('grotebroer1', api=self.api, userstream=self.userstream)

    def test_start(self):
        with mock.patch('threading.Thread', autospec=True) as thread_class:
            self.aivd.start()
            thread_class.assert_called_with(name='GroteBroer1-UserStream', target=self.aivd.run)
            self.assertTrue(thread_class.return_value.start.called)

    def test_stop(self):
        self.aivd.stop()
        self.assertFalse(self.aivd.running)

    def test_aborts_run(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '+verdacht',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]
        
        self.aivd.run()

        self.assertFalse(self.api.save.called)

    def test_dm_answer_query(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'something_else': {} },
            '',
            { 'direct_message': { 'id': '1',
                                  'text': '?',
                                  'sender_screen_name': 'j0057m',
                                  'sender': { 'screen_name': 'j0057m' } } },
            { 'direct_message': { 'id': '2',
                                  'text': 'who am i?',
                                  'sender_screen_name': 'not_an_admin',
                                  'sender': { 'screen_name': 'not_an_admin' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='test')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

    def test_dm_add_term(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '+verdacht',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Term added: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

        self.assertTrue(self.api.save.called)

        self.assertEqual(['test', 'verdacht'], self.api.config['terms'])

    def test_dm_add_existing_term(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '+test',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Term already in list: test')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

        self.assertFalse(self.api.save.called)

        self.assertEqual(['test'], self.api.config['terms'])

    def test_dm_del_term(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '-test',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Term removed: test')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

        self.assertEqual([], self.api.config['terms'])

    def test_dm_del_term_nonexisting(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '-verdacht',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Term not in list: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

        self.assertEqual(['test'], self.api.config['terms'])

    def test_dm_send_help(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': 'spam',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Usage: +term | -term | ?')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

    def test_dm_set_chance(self):
        self.api.config = { 
            'terms': ['test'],
            'admins': ['j0057m'],
            'chance': 13 }

        self.userstream.get_user.return_value = [
            { 'direct_message': { 'id': '1',
                                   'text': '42%',
                                   'sender_screen_name': 'j0057m',
                                   'sender': { 'screen_name': 'j0057m' } } } ]

        self.aivd.running = True
        self.aivd.run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name='j0057m',
            text='Retweet/follow chance is now 42%')
        self.api.post_direct_messages_destroy.assert_called_with(id='1')

        self.assertEqual(self.api.config['chance'], 42)

class TestGroteBroer1_Firehose(unittest.TestCase):
    def setUp(self):
        self.api_ = mock.Mock()
        self.stream = mock.Mock()
        self.queue = mock.Mock()
        self.aivd = bot.grotebroer1.Firehose('grotebroer1', api=self.api_, stream=self.stream, queue=self.queue)

    def test_start(self):
        with mock.patch('threading.Thread', autospec=True) as thread_class:
            self.aivd.start()
            thread_class.assert_called_with(name='GroteBroer1-Firehose', target=self.aivd.run)
            self.assertTrue(thread_class.return_value.start.called)

    def test_stop(self):
        self.aivd.stop()
        self.assertFalse(self.aivd.running)

    def test_aborts_run(self):
        self.stream.get_statuses_filter = lambda *a, **k: [
            '',
            { 'text': 'test',
              'id': '1',
              'user': { 'screen_name': 'test1' } } ]

        self.aivd.run()
        
        self.assertFalse(self.queue.put.called)

    def test_skip_no_update(self):
        self.stream.get_statuses_filter = lambda *a, **k: [
            '',
            { 'text': 'test',
              'id': '1',
              'user': { 'screen_name': 'test1' } } ]

        self.aivd.running = True
        self.aivd.run()
        
        self.assertTrue(self.queue.put.called)

class TestGroteBroer1_Inspector(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.api.config = {}
        self.queue = mock.MagicMock()
        self.aivd = bot.grotebroer1.Inspector('grotebroer1', api=self.api, queue=self.queue)

    def test_start(self):
        with mock.patch('threading.Thread', autospec=True) as thread_class:
            self.aivd.start(count=1)
            thread_class.assert_called_with(name='GroteBroer1-Inspector-0', target=self.aivd.run)
            self.assertTrue(thread_class.return_value.start.called)

    def test_stop(self):
        with mock.patch('threading.Thread', autospec=True) as thread_class:
            self.aivd.start()
            self.aivd.stop()
            self.queue.put.assert_called_with(None)

    def test_aborts_run(self):
        self.queue.get.return_value = None
        self.aivd.run()

    def test_search_match(self):
        self.api.config['chance'] = 100

        returns = [ { 'id': '1',
                      'text': 'test',
                      'user': { 'screen_name': 'test1' } },
                    None ]
        self.queue.get.side_effect = lambda: returns.pop(0)

        self.aivd.term_regex = r'\b(?:test)\b'
        self.aivd.terms = re.compile(self.aivd.term_regex)

        self.aivd.run()

        self.api.post_statuses_retweet.assert_called_with('1')
        self.api.post_friendships_create.assert_called_with(screen_name='test1')

    def test_search_no_match(self):
        self.api.config['chance'] = 100

        returns = [ { 'id': '1',
                      'text': 'text',
                      'user': { 'screen_name': 'test1' } },
                    None ]
        self.queue.get.side_effect = lambda: returns.pop(0)

        self.aivd.term_regex = r'\b(?:test)\b'
        self.aivd.terms = re.compile(self.aivd.term_regex)

        self.aivd.run()

        self.assertFalse(self.api.post_statuses_retweet.called)
        self.assertFalse(self.api.post_friendships_create.called)

    def test_bad_luck(self):
        self.api.config['chance'] = 0

        returns = [ { 'id': '1',
                      'text': 'test',
                      'user': { 'screen_name': 'test1' } },
                    None ]
        self.queue.get.side_effect = lambda: returns.pop(0)

        self.aivd.term_regex = r'\b(?:test)\b'
        self.aivd.terms = re.compile(self.aivd.term_regex)

        self.aivd.run()

        self.assertFalse(self.api.post_statuses_retweet.called)
        self.assertFalse(self.api.post_friendships_create.called)

    def test_update_regex(self):
        self.api.config = { 'terms': ['a', 'b'] }

        self.aivd.update(None)
        self.aivd.update(None)

        self.assertEqual(self.aivd.term_regex, r'\b(?:a|b)\b')

