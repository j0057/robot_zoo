
import os
import time
import hashlib
import hmac
import urllib.request, urllib.parse, urllib.error
import base64

import requests

nonce = lambda n=36: base64.urlsafe_b64encode(os.urandom(n)).decode('ascii')
timestamp = lambda: str(int(time.time()))
urlencode = lambda s: urllib.parse.quote(s, safe='')
urlencode_dict = lambda d: '&'.join('{0}={1}'.format(urlencode(k), urlencode(d[k])) for k in sorted(d.keys()))

def hmac_sha1(key, s):
    h = hmac.new(key, digestmod=hashlib.sha1)
    h.update(s)
    return h.digest().encode('base64').strip()

class Oauth1(object):
    def __init__(self, config={}, nonce=nonce, timestamp=timestamp, stream=False):
        self.__dict__.update(config)

        self.nonce = nonce
        self.timestamp = timestamp

        self.session = requests.Session()
        self.stream = stream

        self.log_request = lambda request: None
        self.log_response = lambda response: None

    def _create_request(self, method, url, get, post, headers):
        desturl = (url + '?' + urlencode_dict(get)) if get else url
        request = requests.Request(method, desturl, headers=headers, data=(post if post else None))
        request = self.session.prepare_request(request)
        request.headers['Authorization'] = self._authorization(method, url, get, post)
        return request

    def request(self, method, url, get={}, post={}, headers={}):
        request = self._create_request(method, url, get, post, headers)
        self.log_request(request)
        response = self.session.send(request, stream=self.stream)
        self.log_response(response)
        return response

    def _get_oauth_params(self, get, post):
        oauth = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_nonce': self.nonce(),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': self.timestamp(),
            'oauth_token': self.token,
            'oauth_version': '1.0' }

        params = {}
        params.update(oauth)
        params.update(get)
        params.update(post)

        return oauth, params

    def _get_param_str(self, params):
        return '&'.join(urlencode(k) + '=' + urlencode(params[k]) for k in sorted(params.keys()))

    def _get_sig_str(self, method, url, param_str):
        return '&'.join([ method, urlencode(url), urlencode(param_str) ])

    def _get_sig_key(self):
        return '&'.join([ urlencode(self.consumer_secret), urlencode(self.token_secret) ])

    def _calc_sig(self, sig_key, sig_str):
        return hmac_sha1(sig_key, sig_str)

    def _authorization(self, method, url, get, post):
        oauth, params = self._get_oauth_params(get, post)
        param_str = self._get_param_str(params)
        sig_str = '&'.join([ method, urlencode(url), urlencode(param_str) ])
        sig_key = '&'.join([ urlencode(self.consumer_secret), urlencode(self.token_secret) ])
        oauth['oauth_signature'] = self._calc_sig(sig_key, sig_str)
        return 'OAuth ' + ', '.join('{0}="{1}"'.format(k, urlencode(oauth[k])) for k in sorted(oauth.keys()))

