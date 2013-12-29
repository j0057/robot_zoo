import array
import math
import os
import os.path
import threading
import Queue

import PIL
import PIL.Image

import twitter

class GeoTweets(object):
    def __init__(self, name, api=None, stream=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)
        self.stream = stream if stream else twitter.StreamAPI(name)
        self.queue = Queue.Queue()
        self.lock = threading.RLock()

        self.raw_name = 'nltweets-raw.png'
        self.viz_name = 'nltweets.png'

        self.create_raw()
        self.load_raw()
        
    @twitter.task(name='GeoTweets-Firehose-{0}')
    def firehose(self, cancel):
        self.api.info('{0} starting, #{1}', threading.current_thread().name, twitter.gettid())
        try:
            for tweet in self.stream.get_statuses_filter(locations='3.23,50.75,7.23,53.75'):
                if cancel: break
                if not tweet: continue
                if not tweet['geo']: continue
                (lat, lng) = tweet['geo']['coordinates']
                self.queue.put((lat,lng))
        finally:
            self.queue.put(None)
            self.api.info('{0} exiting', threading.current_thread().name)

    @twitter.task(name='GeoTweets-Processor-{0}')
    def process(self, _):
        self.api.info('{0} starting, #{1}', threading.current_thread().name, twitter.gettid())
        try:
            while True:
                coord = self.queue.get()
                if not coord: break
                (lat, lng) = coord
                x = int((lng- 3.23) * 256)
                y = int((lat-50.75) * 256)
                if not (0 <= x < 1024): continue
                if not (0 <= y <  768): continue
                y =  768 - y - 1
                i = 1024 * y + x
                with self.lock:
                    self.raw[i] += 1
        finally:
            self.api.info('{0} exiting', threading.current_thread().name)

    def create_raw(self):
        if os.path.isfile(self.raw_name):
            self.api.info('File exists: {0}', self.raw_name)
        else:
            self.api.info('Creating: {0}', self.raw_name)
            image = PIL.Image.new('RGBA', (1024, 768), (0, 0, 0, 0))
            image.save(self.raw_name)

    def load_raw(self):
        self.api.info('Loading raw data: {0}', self.raw_name)
        image = PIL.Image.open(self.raw_name)
        self.raw = array.array('I', image.tostring())
        self.viz = array.array('I', image.tostring())

    def save_raw(self, t=None):
        with self.lock:
            image = PIL.Image.frombuffer('RGBA', (1024, 768), self.raw, 'raw', 'RGBA', 0, 1)
            image.save(self.raw_name)
        return True

    def create_viz(self, t=None):
        cache = {}
        with self.lock:
            highest = max(self.raw)
            self.api.info('Max: {0}', highest)
            for (i, v) in enumerate(self.raw):
                try:
                    self.viz[i] = cache[v]
                except KeyError:
                    cache[v] = self.viz[i] = int(math.log(v+1) / math.log(highest+1) * 255) * 0x010101
        img = PIL.Image.frombuffer('RGBA', (1024, 768), self.viz, 'raw', 'RGBA', 0, 1)
        img = img.convert('RGB')
        img.save('_' + self.viz_name)
        os.rename('_' + self.viz_name, self.viz_name)
        self.api.info('Done')
        return True
