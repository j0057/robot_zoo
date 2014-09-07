import logging
import os
import time
import threading
import re
import random
import Queue 

import unidecode

from .. import twitter

DEFAULT_CONFIG = lambda: {
    'terms': [],
    'chance': 0
}

class UserStream(object):
    def __init__(self, name, api=None, userstream=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.userstream = userstream if userstream else twitter.UserStreamAPI(name)
        self.state = twitter.Configuration(
            config_file=os.environ.get('ROBOT_ZOO_LIB', '.') + '/' + name + '.json',
            default=DEFAULT_CONFIG)
            

    @twitter.task('GB1-User-{0}')
    def run(self, cancel):
        handlers = [
            (self.dm_cmd_answer_query,   re.compile(r'^\?$').match),
            (self.dm_cmd_add_term,       re.compile(r'^\+[a-z]+$').match),
            (self.dm_cmd_del_term,       re.compile(r'^-[a-z]+$').match),
            (self.dm_cmd_set_chance,     re.compile(r'(100|[1-9][0-9]?|)%').match),
            (self.dm_cmd_send_help,      lambda t: True) ]

        for item in self.userstream.get_user():
            if cancel:
                break
            if not item:
                continue
            if 'direct_message' in item:
                m = item['direct_message']
                if m['sender']['screen_name'] not in self.api.config['admins']:
                    self.dm_print(**m)
                    continue
                self.dm_print(**m)
                answer = next(handler 
                              for (handler, cond) in handlers 
                              if cond(m['text']))(**m)
                self.dm_send_answer(answer, **m)
                self.dm_delete(**m)

    def dm_print(self, text, sender_screen_name, id, **_):
        self.log.info('DM #%s from @%s: %r (%d)', id, sender_screen_name, text, len(text))

    @twitter.retry
    def dm_send_answer(self, answer, sender_screen_name, id, **_):
        self.log.info('DM #%s to @%s: %r (%d)', id, sender_screen_name, answer, len(answer))
        self.api.post_direct_messages_new(screen_name=sender_screen_name, text=answer)

    @twitter.retry
    def dm_delete(self, id, **_):
        self.log.info('DM #%s delete', id)
        self.api.post_direct_messages_destroy(id=id)

    def dm_cmd_answer_query(self, text, sender_screen_name, id, **_):
        return u','.join(self.state.config['terms'])

    def dm_cmd_add_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        if term not in self.state.config['terms']:
            self.state.config['terms'].append(term)
            self.state.save()
            return u"Term added: " + term
        else:
            return u"Term already in list: " + term

    def dm_cmd_del_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        try:
            index = self.state.config['terms'].index(term)
            del self.state.config['terms'][index]
            self.state.save()
            return u"Term removed: " + term
        except ValueError:
            return u"Term not in list: " + term

    def dm_cmd_set_chance(self, text, sender_screen_name, id, **_):
        chance = int(text[:-1])
        self.state.config["chance"] = chance
        self.state.save()
        return u"Retweet/follow chance is now {0}%".format(chance)

    def dm_cmd_send_help(self, text, sender_screen_name, id, **_):
        return u"Usage: +term | -term | ?"

class Inspector(object):
    def __init__(self, name, api=None, queue=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.queue = queue if queue else Queue.Queue()
        self.term_regex = None
        self.state = twitter.Configuration(
            config_file=os.environ.get('ROBOT_ZOO_LIB', '.') + '/' + name + '.json',
            default=DEFAULT_CONFIG)

    @twitter.task('GB1-Inspect-{0}')
    def run(self, cancel):
        while True:
            tweet = self.queue.get()
            if tweet is None:
                break
            if not self.term_regex:
                continue
            if self.search(tweet):
                self.handle_suspect(tweet)

    def search(self, tweet):
        text = unidecode.unidecode(tweet['text']).lower()
        if self.terms.search(text):
            self.log.info('Match: #%s from @%s: %r', tweet['id'], tweet['user']['screen_name'], tweet['text'])
            return True
        return False
  
    @twitter.retry 
    def retweet(self, tweet):
        self.log.info('Retweeting #%s from @%s', tweet['id'], tweet['user']['screen_name'])
        self.api.post_statuses_retweet(tweet['id'])

    @twitter.retry
    def follow(self, tweet):
        self.log.info('Following user @%s', tweet['user']['screen_name'])
        self.api.post_friendships_create(screen_name=tweet['user']['screen_name'])
 
    def handle_suspect(self, tweet, randint=random.randint):
        if randint(1, 100) <= self.state.config["chance"]:
            self.retweet(tweet)
            self.follow(tweet)
            return True
        return False

class GroteBroer1(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.inspector = Inspector(name, api=self.api, queue=Queue.Queue())
        self.userstream = UserStream(name, api=self.api)
        self.state = twitter.Configuration(
            config_file=os.environ.get('ROBOT_ZOO_LIB', '.') + '/' + name + '.json',
            default=DEFAULT_CONFIG)

    def update_regex(self, t):
        term_regex = r'\b(?:' + '|'.join(self.state.config['terms']) + r')\b'
        if self.inspector.term_regex != term_regex:
            self.log.info('Firehose new regex: %r', term_regex)
            self.inspector.terms = re.compile(term_regex)
            self.inspector.term_regex = term_regex
        return True
