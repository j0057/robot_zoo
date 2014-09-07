import array
import logging
import math
import os
import os.path
import threading
import Queue

import PIL
import PIL.Image

from .. import twitter

class GeoTweets(object):
    def __init__(self, name, api=None, stream=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.stream = stream if stream else twitter.StreamAPI(name, self.log)
        self.queue = Queue.Queue()
        self.lock = threading.RLock()

        lib_path = os.environ.get('ROBOT_ZOO_LIB', '.')

        self.raw_name = lib_path + '/' + 'nltweets-raw.png'
        self.viz_name = lib_path + '/' + 'nltweets.png'

        self.create_raw()
        self.load_raw()
        
    @twitter.task(name='GeoTweets-{0}')
    def process(self, _):
        while True:
            tweet = self.queue.get()
            if not tweet: break
            if not tweet['geo']: continue
            (lat, lng) = tweet['geo']['coordinates']
            x = int((lng- 3.23) * 256)
            y = int((lat-50.75) * 256)
            if not (0 <= x < 1024): continue
            if not (0 <= y <  768): continue
            y =  768 - y - 1
            i = 1024 * y + x
            with self.lock:
                self.raw[i] += 1

    def create_raw(self):
        if os.path.isfile(self.raw_name):
            self.log.info('%s - File exists: %s', self.name, self.raw_name)
        else:
            self.log.info('%s - Creating: %s', self.name, self.raw_name)
            image = PIL.Image.new('RGBA', (1024, 768), (0, 0, 0, 0))
            image.save(self.raw_name)

    def load_raw(self):
        self.log.info('%s - Loading raw data: %s', self.name, self.raw_name)
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
            for (i, v) in enumerate(self.raw):
                try:
                    self.viz[i] = cache[v]
                except KeyError:
                    cache[v] = self.viz[i] = int(math.log(v+1) / math.log(highest+1) * 255) * 0x010101
        img = PIL.Image.frombuffer('RGBA', (1024, 768), self.viz, 'raw', 'RGBA', 0, 1)
        img = img.convert('RGB')
        img.save('_' + self.viz_name)
        os.rename('_' + self.viz_name, self.viz_name)
        #raise Exception("BANGK!")
