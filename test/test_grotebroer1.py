import time
import unittest

import mock

import twitter
import bot.grotebroer1

class TestGroteBroer1_UserStream(unittest.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.userstream = mock.Mock()
        self.aivd = bot.grotebroer1.UserStream('grotebroer1', api=self.api, userstream=self.userstream)

    def test_dm_answer_query(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { 'direct_message': { u'id': u'1',
                                  u'text': u'?',
                                  u'sender_screen_name': u'j0057m',
                                  u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'test')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')
            
    def test_dm_add_term(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { u'direct_message': { u'id': u'1',
                                   u'text': u'+verdacht',
                                   u'sender_screen_name': u'j0057m',
                                   u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term added: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')

        self.assertTrue(self.api.save.called)

        self.assertEqual([u'test', u'verdacht'], self.api.config[u'terms'])

    def test_dm_add_existing_term(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { u'direct_message': { u'id': u'1',
                                   u'text': u'+test',
                                   u'sender_screen_name': u'j0057m',
                                   u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term already in list: test')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')

        self.assertFalse(self.api.save.called)

        self.assertEqual([u'test'], self.api.config[u'terms'])

    def test_dm_del_term(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { u'direct_message': { u'id': u'1',
                                   u'text': u'-test',
                                   u'sender_screen_name': u'j0057m',
                                   u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term removed: test')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')

        self.assertEqual([], self.api.config[u'terms'])

    def test_dm_del_term_nonexisting(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { u'direct_message': { u'id': u'1',
                                   u'text': u'-verdacht',
                                   u'sender_screen_name': u'j0057m',
                                   u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Term not in list: verdacht')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')

        self.assertEqual([u'test'], self.api.config[u'terms'])

    def test_dm_send_help(self):
        self.api.config = { 
            u'terms': [u'test'],
            u'admins': ['j0057m'] }

        self.userstream.get_user.return_value = [
            { u'direct_message': { u'id': u'1',
                                   u'text': u'spam',
                                   u'sender_screen_name': u'j0057m',
                                   u'sender': { u'screen_name': u'j0057m' } } } ]

        self.aivd.userstream_run()

        self.api.post_direct_messages_new.assert_called_with(
            screen_name=u'j0057m',
            text=u'Usage: +term | -term | ?')
        self.api.post_direct_messages_destroy.assert_called_with(id=u'1')

