
import json
import urllib
import urllib2
import re
import time
import sys
import urllib2, base64, json, threading, Queue

import oauth2 as oauth

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

    def __log(self, level, message, *args):
        if level > self.LEVEL:
            return

        if args: 
            message = message.format(*args)

        t = time.asctime()

        for line in message.split('\n'):
            print "[{0}] {1}: {2}".format(time.asctime(), self.name, line)

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
        global client
        client = self.create_oauth_client()

        body = None
        headers = { 'Accept': 'application/json' }
        if (method == 'GET') and get_params:
            url += '?'
            url += urllib.urlencode(get_params)
        elif (method == 'POST') and get_params:
            body = urllib.urlencode(get_params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        self.debug('    < {0} {1}', method, url)

        for k in sorted(headers.keys()):
            self.debug('    < {0}: {1}', k.title(), headers[k])

        if body:
            self.debug('')
            self.debug(unicode(body))

        response, content = client.request(url, method=method, body=body, headers=headers, force_auth_header=True)

        for k in sorted(response.keys()):
            self.debug('    > {0}: {1}', k.title(), response[k])

        #if 'x-ratelimit-remaining' in response:
        #    self.log('    remaining API calls: {0}', response['x-ratelimit-remaining'])

        if response['content-type'] == 'application/json; charset=utf-8':
            content = json.JSONDecoder().decode(content.decode('utf8'))

        if response['content-type'] == 'application/json':
            content = json.JSONDecoder().decode(content)

        if 200 <= int(response['status']) < 300:
            status = response['status']
            if 'x-ratelimit-remaining' in response:
                status += ' (' + response['x-ratelimit-remaining'] + ' left)'
            return status, content
        else:
            #for h in response.keys():
            #    self.error('{1}: {1}', h, response[h])
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

        def generate_caller(method, path, obj):
            def caller(*pos_args, **get_args):
                pos_args = map(str, pos_args)
                get_args = { k: unicode(v).encode('utf8') for (k,v) in get_args.items() } 
                url = 'http://api.twitter.com/' + '/'.join(x for x in ['1'] + [path, obj] + pos_args if x) + '.json'

                self.debug('--> {0}', name)
                status, response = self.oauth_request(method, url, **get_args)
                self.debug('<-- {0}: {1}', name, status)

                return response
            return caller

        return generate_caller(method, path, obj)

    def check(self):
        result = self.get_account_verify_credentials()
        name = '@' + result['screen_name'].lower()
        assert self.name == name, 'Name according to self is "{0}", but "{1}" according to twitter'.format(self.name, name)

# compatibility with some old code

_TWITTER = TwitterAPI()

get_verify          = lambda     : _TWITTER.get_account_verify_credentials()
post_status         = lambda s   : _TWITTER.post_statuses_update(status=s)
post_reply_to       = lambda i, s: _TWITTER.post_statuses_update(status=s, in_reply_to_status_id=i)
get_follower_ids    = lambda     : _TWITTER.get_followers_ids() 
get_following_ids   = lambda     : _TWITTER.get_friends_ids()
post_follow_id      = lambda u   : _TWITTER.post_friendships_create(u)
post_retweet        = lambda i   : _TWITTER.post_statuses_retweet(i)

def get_new_mentions_(since_id=''):
    if since_id:
        result = _TWITTER.get_statuses_mentions(count=200, since_id=since_id)
    else:
        result = _TWITTER.get_statuses_mentions(count=200)
	return dict((m['id'], (m['text'], m['user']['screen_name'], m['user']['utc_offset'])) for m in result)

if __name__ == '__main__':
    LoggingObject.LEVEL = LoggingObject.LEVEL_DEBUG

    twtr = TwitterAPI('cfg/johndoeveloper.json')
    twtr.get_account_verify_credentials()

    def j(o):
        import json
        print json.dumps(o, sort_keys=True, indent=4)

