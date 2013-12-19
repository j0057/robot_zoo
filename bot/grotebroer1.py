__version__ = '0.1'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

import time
import urllib2, base64, json, threading, re
import random

import twitter

class UserStream(object):
    def __init__(self, name, api=None, userstream=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)
        self.userstream = userstream if userstream else twitter.UserStreamAPI(name)

    def userstream_run(self):
        try:
            self.userstream_running = True

            handlers = [
                (self.userstream_dm_cmd_answer_query,   re.compile(r'^\?$').match),
                (self.userstream_dm_cmd_add_term,       re.compile(r'^\+[a-z]+$').match),
                (self.userstream_dm_cmd_del_term,       re.compile(r'^-[a-z]+$').match),
                (self.userstream_dm_cmd_set_chance,     re.compile(r'(100|[1-9][0-9]?|)%').match),
                (self.userstream_dm_cmd_send_help,      lambda t: True) ]

            for item in self.userstream.get_user():
                if not self.userstream_running:
                    break
                if not item:
                    continue
                if 'direct_message' in item:
                    m = item['direct_message']
                    if m['sender']['screen_name'] not in self.api.config['admins']:
                        continue
                    self.userstream_dm_print(**m)
                    answer = next(handler 
                                  for (handler, cond) in handlers 
                                  if cond(m['text']))(**m)
                    self.userstream_dm_send_answer(answer, **m)
                    self.userstream_dm_delete(**m)
        finally:
            self.api.log('Userstream exiting')

    def userstream_start(self):
        self.api.log('Userstream starting')
        threading.Thread(target=self.userstream_run, name='GroteBroer1-UserStream').start()

    def userstream_stop(self):
        self.api.log('Userstream stopping')
        self.userstream_running = False

    def userstream_dm_print(self, text, sender_screen_name, id, **_):
        self.api.info('DM #{0} from {1}: {2} ({3})', id, sender_screen_name, repr(text), len(text))

    @twitter.retry
    def userstream_dm_send_answer(self, answer, sender_screen_name, id, **_):
        self.api.info('DM #{0} to {1}: {2} ({3})', id, sender_screen_name, repr(answer), len(answer))
        self.api.post_direct_messages_new(screen_name=sender_screen_name, text=answer)

    @twitter.retry
    def userstream_dm_delete(self, id, **_):
        self.api.info("DM #{0} delete", id)
        self.api.post_direct_messages_destroy(id=id)

    def userstream_dm_cmd_answer_query(self, text, sender_screen_name, id, **_):
        return u','.join(self.api.config['terms'])

    def userstream_dm_cmd_add_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        if term not in self.api.config['terms']:
            self.api.config['terms'].append(term)
            self.api.save()
            return u"Term added: " + term
        else:
            return u"Term already in list: " + term

    def userstream_dm_cmd_del_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        try:
            index = self.api.config['terms'].index(term)
            del self.api.config['terms'][index]
            self.api.save()
            return u"Term removed: " + term
        except ValueError:
            return u"Term not in list: " + term

    def userstream_dm_cmd_set_chance(self, text, sender_screen_name, id, **_):
        chance = int(text[:-1])
        self.api.config["chance"] = chance
        self.api.save()
        return u"Retweet/follow chance is now {0}%".format(chance)

    def userstream_dm_cmd_send_help(self, text, sender_screen_name, id, **_):
        return u"Usage: +term | -term | ?"

class Firehose(object):
    def __init__(self, name, api=None, stream=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)
        self.stream = stream if stream else twitter.StreamAPI(name)

    def firehose_run(self):
        try:
            for tweet in self.stream.get_statuses_filter(locations='3.27,51.35,7.25,53.6'):
                if not self.firehose_running:
                    break
                if not tweet:
                    continue
                if not self.firehose_regex:
                    continue
                if self.firehose_search(tweet):
                    self.firehose_handle_suspect(tweet)
        finally:
            self.api.info('Firehose exiting')

    def firehose_start(self):
        self.api.info('Firehose starting')
        self.firehose_running = True
        self.firehose_regex = ''
        threading.Thread(target=self.firehose_run, name='GroteBroer1-Firehose').start()

    def firehose_stop(self):
        self.api.info('Firehose stopping')
        self.firehose_running = False

    def firehose_search(self, tweet):
        if self.firehose_terms.search(tweet['text']):
            self.api.info('Firehose match: #{0} from {1}: {2!r}', tweet['id'], tweet['user']['screen_name'], tweet['text'])
            return True
  
    @twitter.retry 
    def firehose_retweet(self, tweet):
        self.api.info('Firehose retweeting #{0} from @{1}', tweet['id'], tweet['user']['screen_name'])
        self.api.post_statuses_retweet(tweet['id'])

    @twitter.retry
    def firehose_follow(self, tweet):
        self.api.info('Following user @{0}', tweet['user']['screen_name'])
        self.api.post_friendships_create(screen_name=tweet['user']['screen_name'])
 
    def firehose_handle_suspect(self, tweet, randint=random.randint):
        if randint(1, 100) <= self.api.config["chance"]:
            self.firehose_retweet(tweet)
            self.firehose_follow(tweet)

    def firehose_update(self, t):
        firehose_regex = r'\b(?:' + '|'.join(self.api.config['terms']) + r')\b'
        if self.firehose_regex != firehose_regex:
            self.api.info('Firehose new regex: {0!r}', firehose_regex)
            self.firehose_regex = firehose_regex
            self.firehose_terms = re.compile(firehose_regex)
        return True

class GroteBroer1(object):
    def __init__(self, name, api=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)
        self.firehose = Firehose(name, api=self.api)
        self.userstream = UserStream(name, api=self.api)
