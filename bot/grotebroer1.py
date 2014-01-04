import logging
import time
import threading
import re
import random
import Queue 

import unidecode

import twitter

class UserStream(object):
    def __init__(self, name, api=None, userstream=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.userstream = userstream if userstream else twitter.UserStreamAPI(name)

    @twitter.task('GroteBroer1-UserStream-{0}')
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
        return u','.join(self.api.config['terms'])

    def dm_cmd_add_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        if term not in self.api.config['terms']:
            self.api.config['terms'].append(term)
            self.api.save()
            return u"Term added: " + term
        else:
            return u"Term already in list: " + term

    def dm_cmd_del_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        try:
            index = self.api.config['terms'].index(term)
            del self.api.config['terms'][index]
            self.api.save()
            return u"Term removed: " + term
        except ValueError:
            return u"Term not in list: " + term

    def dm_cmd_set_chance(self, text, sender_screen_name, id, **_):
        chance = int(text[:-1])
        self.api.config["chance"] = chance
        self.api.save()
        return u"Retweet/follow chance is now {0}%".format(chance)

    def dm_cmd_send_help(self, text, sender_screen_name, id, **_):
        return u"Usage: +term | -term | ?"

class Firehose(object):
    def __init__(self, name, api=None, stream=None, queue=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.stream = stream if stream else twitter.StreamAPI(name)
        self.queue = queue if queue else Queue.Queue()
        self.stat_tweets = 0

    @twitter.task('GroteBroer1-Firehose-{0}')
    def run(self, cancel):
        try:
            for tweet in self.stream.get_statuses_filter(locations='3.27,51.35,7.25,53.6'):
                if cancel:
                    break
                if not tweet:
                    continue
                self.queue.put(tweet)
                self.stat_tweets += 1
        finally:
            target_len = self.queue.qsize() + 10
            while self.queue.qsize() < target_len:
                self.queue.put(None)
                time.sleep(0.2)

class Inspector(object):
    def __init__(self, name, api=None, queue=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.queue = queue if queue else Queue.Queue()
        self.term_regex = None
        self.stat_matched = 0
        self.stat_matched_lock = threading.Lock()
        self.stat_handled = 0
        self.stat_handled_lock = threading.Lock()

    @twitter.task('GroteBroer1-Inspector-{0}')
    def run(self, cancel):
        while True:
            tweet = self.queue.get()
            if tweet is None:
                break
            if not self.term_regex:
                continue
            if self.search(tweet):
                with self.stat_matched_lock:
                    self.stat_matched += 1
                if self.handle_suspect(tweet):
                    with self.stat_handled_lock:
                        self.stat_handled += 1

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
        if randint(1, 100) <= self.api.config["chance"]:
            self.retweet(tweet)
            self.follow(tweet)
            return True
        return False

class GroteBroer1(object):
    STATS_FILENAME = 'grotebroer1-stats.log'
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.firehose = Firehose(name, api=self.api, queue=Queue.Queue())
        self.inspector = Inspector(name, api=self.api, queue=self.firehose.queue)
        self.userstream = UserStream(name, api=self.api)
        self.stats_lock = threading.Lock()

        self.truncate_stats()

    def update_regex(self, t):
        term_regex = r'\b(?:' + '|'.join(self.api.config['terms']) + r')\b'
        if self.inspector.term_regex != term_regex:
            self.log.info('Firehose new regex: %r', term_regex)
            self.inspector.terms = re.compile(term_regex)
            self.inspector.term_regex = term_regex
        return True

    def truncate_stats(self, t=None):
        with self.stats_lock:
            with open(self.STATS_FILENAME, 'w') as f:
                f.truncate()
        return True

    def log_stats(self, t=None):
        with self.stats_lock:
            message = 'tweets={0} matched={1} handled={2} qsize={3}\n'.format(
                self.firehose.stat_tweets, 
                self.inspector.stat_matched, 
                self.inspector.stat_handled,
                self.firehose.queue.qsize())
        with open(self.STATS_FILENAME, 'a') as f:
            f.write(message)
        return True
