
import json
import urllib
import urllib2
import re
import time
import sys
import threading
import urllib2, base64, json, threading, Queue

import oauth1

import oauth2 as oauth

# LoggingObject
#     |
# OauthClient
#     |        Configuration
#     \           |
#      \         /
#       \       /
#       TwitterAPI

class FailWhale(Exception):
    def __init__(self, *args):
        Exception.__init__(self, args)
    def log_error(self, obj):
        obj.error('FAIL WHALE: {0} {1}', str(self), self.args)

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

class OauthClient(LoggingObject):
    def oauth_client(self, consumer_key, consumer_secret, token_key, token_secret):
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth.Token(key=token_key, secret=token_secret)
        client = oauth.Client(consumer, token)
        client.timeout = 30
        return client

    def oauth_request(self, method, url, **get_params):
        client = self.create_oauth_client()

        # add parameters
        body = ''
        headers = { 'Accept': 'application/json' }
        if (method == 'GET') and get_params:
            url += '?'
            url += urllib.urlencode(get_params)
        elif (method == 'POST') and get_params:
            body = urllib.urlencode(get_params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        # print debug messages for request
        debug = u''
        debug += u'\n    < {0} {1}'.format(method, url)
        for k in sorted(headers.keys()):
            debug += u'\n    < {0}: {1}'.format(k.title(), headers[k])
        if body:
            debug += u'\n'
            debug += u'\n' + unicode(body)

        # send request
        response, content = client.request(url, method=method, body=body, headers=headers)

        # print debug messages for response
        for k in sorted(response.keys()):
            debug += u'\n    > {0}: {1}'.format(k.title(), response[k])
        self.debug(debug)

        # parse JSON
        if re.match('application/json(; ?charset=utf-8)?', response['content-type'], re.IGNORECASE):
            content = json.JSONDecoder().decode(content.decode('utf8'))

        # return response content
        if 200 <= int(response['status']) < 300:
            status = response['status']
            if 'x-ratelimit-remaining' in response:
                status += ' (' + response['x-ratelimit-remaining'] + ' left)'
            return status, content
        # raise error
        else:
            for line in str(content).split('\n'):
                self.error(line)
            raise FailWhale(response['status'], response['content-type'], content)

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

class StreamAPI(object):
    def open_stream(self, *obj, **args):
        username, password = self.get_stream_auth()
        url = 'https://stream.twitter.com/{0}.json?{1}'.format('/'.join(['1'] + list(obj)), urllib.urlencode(args))
        req = urllib2.Request(url)
        req.add_header('Authorization', 'Basic: ' + base64.encodestring(username + ':' + password)[:-1])
        for line in urllib2.urlopen(req):
            try:
                yield json.loads(line)
            except ValueError:
                self.error(repr(line))


class TwitterAPI(Configuration, OauthClient):
    def create_oauth_client(self):
        return self.oauth_client(self.config['oauth']['consumer_key'], 
                                 self.config['oauth']['consumer_secret'],
                                 self.config['oauth']['token'],
                                 self.config['oauth']['token_secret'])

    API_VERSION = '1.1'
    API_HOST = 'api.twitter.com'

    API_REGEX = r'^(get|post|put|delete)_(statuses|search|direct_messages|followers|friendships|friends|users|favorites|lists|account|saved_searches|trends|geo|blocks|notifications)(.*)'
    API_REGEX = re.compile(API_REGEX)

    def __init__(self, name=None):
        if name:
            self.name = '@{0}'.format(name)
            config_file = 'cfg/{0}.json'.format(name)
            super(TwitterAPI, self).__init__(config_file)
        else:
            super(TwitterAPI, self).__init__()

    def __getattr__(self, name):
        match = self.API_REGEX.match(name)
        if not match:
            raise AttributeError(name)

        method, path, obj = match.groups()
        method = method.upper()

        obj = obj[1:] 

        #def generate_caller(method, path, obj):
            #def caller(*pos_args, **get_args):
                #pos_args = map(str, pos_args)
                #get_args = { k: unicode(v).encode('utf8') for (k,v) in get_args.items() } 
                #url = 'http://api.twitter.com/' + '/'.join(x for x in ['1.1'] + [path, obj] + pos_args if x) + '.json'
                #self.debug('--> {0}', name)
                #status, response = self.oauth_request(method, url, **get_args)
                #self.debug('<-- {0}: {1}', name, status)
                #return response
            #return caller

        def generate_caller(method, path, obj):
            def caller(*args, **kwargs):
                args = map(str, args)
                kwargs = { k: unicode(v).encode('utf8') for (k, v) in kwargs.items() }
                url = ('https://'
                    + TwitterAPI.API_HOST
                    + '/'
                    + '/'.join([TwitterAPI.API_VERSION] + [path, obj] + args)
                    + '.json')
                self.debug('--> {0}', name)
                client = oauth1.Oauth1(config=self.config['oauth'])
                if method == "POST":
                    response = client.request(method, url, post=kwargs, headers={'Accept': 'application/json'})
                else:
                    response = client.request(method, url, get=kwargs, headers={'Accept': 'application/json'})
                self.debug('<-- {0}: {1}', name, response.status_code)
                response.raise_for_status()
                return response.json()
            return caller

        return generate_caller(method, path, obj)

    def check(self):
        result = self.get_account_verify_credentials()
        name = '@' + result['screen_name'].lower()
        assert self.name == name, 'Name according to self is "{0}", but "{1}" according to twitter'.format(self.name, name)

# TwitterAPI('grotebroer1').create_oauth.client().request('https://stream.twitter.com/1.1/statuses/filter.json?locations=3.27,51.35,7.25,53.6', method='GET', headers={'Accept': 'application/json'})

