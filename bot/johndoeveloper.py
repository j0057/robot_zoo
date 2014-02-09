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
            for tweet in self.stream.get_statuses_filter(locations=self.locations):
                if cancel: 
                    break
                if not tweet: 
                    continue
                self.enqueue(tweet)
        finally:
            self.enqueue(None)

