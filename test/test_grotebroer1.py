import time
import unittest

import mock

import twitter
import bot.grotebroer1

class TestGroteBroer1(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()

        self.aivd = bot.grotebroer1.GroteBroer1('grotebroer1', self.api)

    def test_dm_fail(self):
        self.api.get_direct_messages.side_effect = twitter.FailWhale
        result = self.aivd.check_dm()
        self.assertFalse(result)

    def test_dm_answer_query(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'?',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'test')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')
            
    def test_dm_add_term(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'+verdacht',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term added: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')

        self.assertTrue(self.api.save.called)

        self.assertEqual([u'test', u'verdacht'], self.api.config[u'terms'])

    def test_dm_add_existing_term(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'+test',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term already in list: test')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')

        self.assertFalse(self.api.save.called)

        self.assertEqual([u'test'], self.api.config[u'terms'])

    def test_dm_del_term(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'-test',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term removed: test')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')

        self.assertEqual([], self.api.config[u'terms'])

    def test_dm_del_term_nonexisting(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'-verdacht',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term not in list: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')

        self.assertEqual([u'test'], self.api.config[u'terms'])

    def test_dm_send_help(self):
        self.api.get_direct_messages.return_value = [
            { u'id': u'1',
              u'text': u'whatevs',
              u'sender_screen_name': u'j0057m' } ]
        self.api.config = { u'terms': [u'test'] }

        self.aivd.check_dm()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Usage: +term | -term | ?')
        self.api.post_direct_messages_destroy.assert_called_with(u'1')

