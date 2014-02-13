#!/usr/bin/env python

import logging

import twitter

class Firehose(object):
    def __init__(self, name, locations, api=None, stream=None):
        self.name = name
        self.locations = locations or '3.23,50.75,7.23,53.75'
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.stream = stream if stream else twitter.StreamAPI(name, self.log)
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def enqueue(self, tweet):
        for listener in self.listeners:
            listener.queue.put(tweet)

    @twitter.task(name='Firehose-{0}')
    def run(self, cancel):
        try:
            firehose = self.stream.get_statuses_filter(locations=self.locations, stall_warnings=True)
            for tweet in firehose:
                if cancel: 
                    break
                if not tweet: 
                    continue
                if 'warning' in tweet:
                    warning = tweet['warning']
                    self.log.info('%s: %s (%d)', warning['code'], warning['message'], warning['percent_full'])
                    continue
                self.enqueue(tweet)
        except Exception as e:
            self.log.exception('WTF: %s', e)
        finally:
            self.enqueue(None)

