
import ctypes
import json
import urllib
import urllib2
import re
import time
import sys
import threading
import urllib2, base64, json, threading, Queue
import functools
import logging
import platform
import os

import prctl
import requests 

import oauth1

class FailWhale(Exception):
    def log_error(self, obj):
        obj.error('FAIL WHALE: {0}', str(self))

def retry(f):
    @functools.wraps(f)
    def retry(self, *a, **k):
        t = 1
        i = 1
        while t < 32:
            try:
                if i > 1:
                    self.log.info('Attempt %d, t=%d', i, t)
                return f(self, *a, **k)
            except FailWhale as e:
                self.log.info("Retry caught %s - %r", type(e).__name__, e)
                time.sleep(t)
                t *= 2
                i += 1
    return retry

class Cancellation(object):
    canceled = False
    def __nonzero__(self):
        return self.canceled
    def cancel(self):
        self.canceled = True

def task(name):
    def task(f):
        @functools.wraps(f)
        def task(self, count=1):
            def run():
                try:
                    prctl.set_name(threading.current_thread().name)
                    logging.getLogger(__name__).info('Starting, #%d', gettid())
                    f(self, cancel)
                finally:
                    logging.getLogger(__name__).info('Exiting')
            cancel = Cancellation()
            for _ in range(count):
                threadname = name.format(task.i)
                thread = threading.Thread(name=threadname, target=run)
                thread.start()
                task.i += 1
            return cancel.cancel
        task.i = 0
        return task
    return task

def gettid():
    if platform.system() != 'Linux':
        return -1
    gettid = { 'armv6l': 224, 'x86_64': 186 }
    machine = platform.machine()
    if machine not in gettid:
        return -1
    return ctypes.CDLL('libc.so.6').syscall(gettid[machine])

"""
class LoggingObject(object):
    LEVEL_DEBUG = 2
    LEVEL_INFO = 1
    LEVEL_ERROR = 0

    LEVEL = LEVEL_INFO
    #EVEL = LEVEL_DEBUG

    OUTPUT_LOCK = threading.Lock()

    def __log(self, level, message, *args):
        if level > self.LEVEL:
            return

        if args: 
            message = message.format(*args)

        t = time.localtime()

        with self.OUTPUT_LOCK:
            for line in message.split('\n'):
                print "{0:04}-{1:02}-{2:02} {3:02}:{4:02}:{5:02} [{6}] {7}".format(
                    t.tm_year, t.tm_mon, t.tm_mday,
                    t.tm_hour, t.tm_min, t.tm_sec,
                    self.name,
                    line)

            sys.stdout.flush()

    _name = None

    @property
    def name(self):
        return self._name or type(self).__name__

    @name.setter
    def name(self, name):
        self._name = name

    def info(self, message, *args):
        self.__log(LoggingObject.LEVEL_INFO, message, *args)

    def error(self, message, *args):
        self.__log(LoggingObject.LEVEL_ERROR, message, *args)

    def debug(self, message, *args):
        self.__log(LoggingObject.LEVEL_DEBUG, message, *args)

    log = info
"""

class Configuration(object):
    def __init__(self, config_file=None):
        self.config = None
        self.config_file = config_file
        self.load()

    def load(self):
        if self.config_file:
            self.log.info('Loading %s', self.config_file)
            with open(self.config_file, 'rb') as f:
                self.config = json.load(f)

    def save(self):
        if self.config_file:
            self.log.info('Saving %s', self.config_file)
            with open(self.config_file, 'wb') as f:
                json.dump(self.config, f, indent=4)

class TwitterAPI(Configuration):
    API_VERSION = '1.1'
    API_HOST = 'api.twitter.com'
    API_STREAM = False

    API_REGEX = r'^(get|post|put|delete)_(statuses|search|direct_messages|followers|friendships|friends|users|favorites|lists|account|saved_searches|trends|geo|blocks|notifications)(.*)'
    API_REGEX = re.compile(API_REGEX)

    def __init__(self, name, log=None):
        self.name = '@{0}'.format(name)
        self.log = log if log else logging.getLogger(__name__)
        config_file = '{0}/{1}.json'.format(os.environ.get('ROBOT_ZOO_CONFIG', 'cfg'), name)
        super(TwitterAPI, self).__init__(config_file)

    def __getattr__(self, name):
        match = self.API_REGEX.match(name)
        if not match:
            raise AttributeError(name)

        method, path, obj = match.groups()
        method = method.upper()

        obj = obj[1:] 

        def generate_caller(method, path, obj):
            def caller(*args, **kwargs):
                args = map(str, args)
                kwargs = { k: unicode(v).encode('utf8') for (k, v) in kwargs.items() }
                url = ('https://'
                    + self.API_HOST
                    + '/'
                    + '/'.join(item for item in ([self.API_VERSION] + [path, obj] + args) if item)
                    + '.json')
                content = None
                try:
                    self.log.debug('--> %s: %s', name, url)
                    client = oauth1.Oauth1(config=self.config['oauth'], stream=self.API_STREAM)
                    client.log_request = self.log_request
                    client.log_response = self.log_response
                    if method == "POST":
                        response = client.request(method, url, post=kwargs, headers={'Accept': 'application/json'})
                    else:
                        response = client.request(method, url, get=kwargs, headers={'Accept': 'application/json'})
                    self.log.debug('<-- %s: %s', name, response.status_code)

                    if self.API_STREAM:
                        content = (self.try_json_decode(message) for message in response.iter_lines(chunk_size=1))
                    else:
                        content = response.json()
                    response.raise_for_status()
                    return content
                except Exception as e:
                    raise FailWhale(content, e)
            caller.name = name
            return caller

        return generate_caller(method, path, obj)

    def try_json_decode(self, s):
        try:
            return json.loads(s)
        except ValueError:
            return s

    def log_request(self, request):
        with logging.root.handlers[0].lock:
            self.log.debug('< %s %s', request.method, request.url)
            for k in sorted(request.headers.keys()):
                self.log.debug('< %s %s', k.capitalize(), request.headers[k])

    def log_response(self, response):
        msg = '\n'
        msg += '\n> {0}'.format(response.status_code)
        for k in sorted(response.headers.keys()):
            msg += '\n> {0}: {1}'.format(k.capitalize(), response.headers[k])
        self.log.debug(msg)

    def check(self):
        self.log.info('Checking account: %s', self.name)
        result = self.get_account_verify_credentials()
        name = '@' + result['screen_name'].lower()
        assert self.name == name, 'Name according to self is "{0}", but "{1}" according to twitter'.format(self.name, name)

class StreamAPI(TwitterAPI):
    API_HOST = 'stream.twitter.com'
    API_STREAM = True

    API_REGEX = r'^(get|post)_(user|statuses)(.*)$'
    API_REGEX = re.compile(API_REGEX)

class UserStreamAPI(StreamAPI):
    API_HOST = 'userstream.twitter.com'


