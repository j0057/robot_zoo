
import ctypes
import json
import urllib
import urllib2
import re
import time
import sys
import threading
import urllib2, base64, json, threading, Queue

import requests 

import oauth1

# LoggingObject
#     |
#     |        Configuration
#     \           |
#      \         /
#       \       /
#       TwitterAPI

class FailWhale(Exception):
    def log_error(self, obj):
        obj.error('FAIL WHALE: {0}', str(self))

def retry(f):
    def retry(self, *a, **k):
        t = 1
        i = 1
        while t < 32:
            try:
                if i > 1:
                    self.api.log('Attempt {0}, t={1}', i, t)
                return f(self, *a, **k)
            except FailWhale as fail:
                fail.log_error(self.api)
                time.sleep(t)
                t *= 2
                i += 1
        return False
    return retry

class Cancellation(object):
    canceled = False
    def __nonzero__(self):
        return self.canceled
    def cancel(self):
        self.canceled = True

def task(name):
    def task(f):
        def task(self):
            cancel = Cancellation()
            thread = threading.Thread(name=name.format(task.i), target=f, args=[self, cancel])
            thread.start()
            task.i += 1
            return cancel.cancel
        task.i = 0
        return task
    return task

def gettid():
    return ctypes.CDLL('libc.so.6').syscall(186)

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

class Configuration(object):
    def __init__(self, config_file=None):
        self.config = None
        self.config_file = config_file
        self.load()

    def load(self):
        if self.config_file:
            self.log('Loading {0}', self.config_file)
            with open(self.config_file, 'rb') as f:
                self.config = json.load(f)

    def save(self):
        if self.config_file:
            self.log('Saving {0}', self.config_file)
            with open(self.config_file, 'wb') as f:
                json.dump(self.config, f, indent=4)

class TwitterAPI(Configuration, LoggingObject):
    API_VERSION = '1.1'
    API_HOST = 'api.twitter.com'
    API_STREAM = False

    API_REGEX = r'^(get|post|put|delete)_(statuses|search|direct_messages|followers|friendships|friends|users|favorites|lists|account|saved_searches|trends|geo|blocks|notifications)(.*)'
    API_REGEX = re.compile(API_REGEX)

    def __init__(self, name):
        self.name = '@{0}'.format(name)
        config_file = 'cfg/{0}.json'.format(name)
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
                try:
                    self.debug('--> {0}: {1}', name, url)
                    client = oauth1.Oauth1(config=self.config['oauth'], stream=self.API_STREAM)
                    client.log_request = self.log_request
                    client.log_response = self.log_response
                    if method == "POST":
                        response = client.request(method, url, post=kwargs, headers={'Accept': 'application/json'})
                    else:
                        response = client.request(method, url, get=kwargs, headers={'Accept': 'application/json'})
                    self.debug('<-- {0}: {1}', name, response.status_code)

                    content = None
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
        msg = '\n'
        msg += '\n< {0} {1}'.format(request.method, request.url)
        for k in sorted(request.headers.keys()):
            msg += '\n< {0}: {1}'.format(k.capitalize(), request.headers[k])
        self.debug(msg)

    def log_response(self, response):
        msg = '\n'
        msg += '\n> {0}'.format(response.status_code)
        for k in sorted(response.headers.keys()):
            msg += '\n> {0}: {1}'.format(k.capitalize(), response.headers[k])
        self.debug(msg)

    def check(self):
        self.info('Checking account')
        result = self.get_account_verify_credentials()
        name = '@' + result['screen_name'].lower()
        #assert self.name == name, 'Name according to self is "{0}", but "{1}" according to twitter'.format(self.name, name)
        if self.name != name:
            self.error('Name according to self is {0!r}, but {1!r} according to twitter',
                name, self.name)
        return True

class StreamAPI(TwitterAPI):
    API_HOST = 'stream.twitter.com'
    API_STREAM = True

    API_REGEX = r'^(get|post)_(user|statuses)(.*)$'
    API_REGEX = re.compile(API_REGEX)

class UserStreamAPI(StreamAPI):
    API_HOST = 'userstream.twitter.com'

# TwitterAPI('grotebroer1').create_oauth.client().request('https://stream.twitter.com/1.1/statuses/filter.json?locations=3.27,51.35,7.25,53.6', method='GET', headers={'Accept': 'application/json'})

