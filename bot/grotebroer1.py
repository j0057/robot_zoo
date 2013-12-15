#!/usr/bin/env python2.7

__version__ = '0.1'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

import time
import urllib2, base64, json, threading, re
import random

import twitter

class GroteBroer1(twitter.TwitterAPI, twitter.StreamAPI):
    def get_stream_auth(self):
        return self.config['login']['username'], self.config['login']['password']

    def start_firehose(self):
        def executor():
            for tweet in self.open_stream('statuses', 'filter', locations='3.27,51.35,7.25,53.6'):
                if self.firehose is None:
                    self.log('Firehose exiting')
                    break
                #ith self.lock:
                if 1:
                    self.firehose.append(tweet)

        self.lock = threading.Lock()
        self.firehose = []
        threading.Thread(target=executor).start()
        self.log('Started firehose')

    def stop_firehose(self):
        self.firehose = None
        self.log('Stopped firehose')

    def get_firehose(self):
        #ith self.lock:
        if 1:
            result, self.firehose = self.firehose, []
        return result

    def handle_suspect(self, tweet):
        screen_name, id = tweet['user']['screen_name'], tweet['id']
        self.config['suspects'][screen_name] = id
        self.save()

    WORDS_REGEX = re.compile(r'[^\w]')
    def search_firehose(self, t):
        c,r=0,0
        for tweet in self.get_firehose():
            if tweet['entities']['urls']:
                continue # don't want to help spammers by RT'ing links to bad places
            c += 1
            text = tweet['text']
            words = [ w.lower() for w in self.WORDS_REGEX.split(text) ]
            for term in self.config['terms']:
                if term.lower() in words:
                    r += 1
                    self.info('#{0} from @{1}: {2}', tweet['id'], tweet['user']['screen_name'], repr(tweet['text']))
                    self.handle_suspect(tweet)
                    break
        self.debug('Firehose: {0}/{1}', c, r)
        return True

    def dm_print(self, text, sender_screen_name, id, **_):
        self.info('DM #{0} from {1}: {2} ({3})', id, sender_screen_name, repr(text), len(text))

    def dm_answer_query(self, text, sender_screen_name, id, **_):
        return u','.join(self.config['terms'])

    def dm_add_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        if term not in self.config['terms']:
            self.config['terms'].append(term)
            self.save()
            return u"Term added: " + term
        else:
            return u"Term already in list: " + term

    def dm_del_term(self, text, sender_screen_name, id, **_):
        term = text[1:].lower()
        try:
            index = self.config['terms'].index(term)
            del self.config['terms'][index]
            self.save()
            return u"Term removed: " + term
        except ValueError:
            return u"Term not in list: " + term

    def dm_send_help(self, text, sender_screen_name, id, **_):
        return u"Usage: +term | -term | ?"

    def dm_send_answer(self, answer, sender_screen_name, id, **_):
        self.info('DM #{0} to {1}: {2} ({3})', id, sender_screen_name, repr(answer), len(answer))
        self.post_direct_messages_new(screen_name=sender_screen_name, text=answer)

        self.log("DM #{0} delete", id)
        self.post_direct_messages_destroy(id)

    def dm(self):
        handlers = [
            (self.dm_answer_query,  lambda t: t == '?'),
            (self.dm_add_term,      lambda t: t.startswith('+')),
            (self.dm_del_term,      lambda t: t.startswith('-')),
            (self.dm_send_help,     lambda t: True) ]

        for m in self.get_direct_messages():
            self.dm_print(**m)
            answer = next(handler for (handler, cond) in handlers if cond(m['text']))(**m)
            self.dm_send_answer(answer, **m)

    def check_dm(self, t):
        try:
            self.dm()
            return True
        except twitter.FailWhale as fail:
            self.log('FAIL WHALE: {0}', fail.args)
            return False

    def follow_suspects(self, t):
        for screen_name, id in list(self.config['suspects'].items()):
            if random.randint(0, 10) < 1:
                try:
                    self.info('Retweeting #{0} from @{1}', id, screen_name)
                    self.post_statuses_retweet(id)
                except twitter.FailWhale as fail:
                    fail.log_error(self)

                try:
                    self.info('Following user @{0}', screen_name)
                    self.post_friendships_create(screen_name=screen_name)
                except twitter.FailWhale as fail:
                    fail.log_error(self)

            del self.config['suspects'][screen_name]
            self.save()
        return True

                

