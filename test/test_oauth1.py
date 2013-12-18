import unittest

import mock

import oauth1

class TestOauth1(unittest.TestCase):
    """
    Testcase from twitter:
    https://dev.twitter.com/docs/auth/authorizing-request
    https://dev.twitter.com/docs/auth/creating-signature
    """

    def setUp(self):
        self.method = 'POST'
        self.url = 'https://api.twitter.com/1/statuses/update.json'
        self.get = { 'include_entities': 'true' }
        self.post = { 'status': 'Hello Ladies + Gentlemen, a signed OAuth request!' }
        self.headers = { 'Accept': 'application/json' }

        self.oauth1 = oauth1.Oauth1(
            config={
                'consumer_key': 'xvz1evFS4wEEPTGEFPHBog',
                'consumer_secret': 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw',
                'token': '370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb',
                'token_secret': 'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'
            },
            nonce=lambda: 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg',
            timestamp=lambda: '1318622958')

    def test_oauth_params(self):
        oauth, params = self.oauth1._get_oauth_params(self.get, self.post)

        self.assertEqual(params, {
            'include_entities': 'true',
            'oauth_consumer_key': 'xvz1evFS4wEEPTGEFPHBog',
            'oauth_nonce': 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_token': '370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb',
            'oauth_timestamp': '1318622958',
            'oauth_version': '1.0',
            'status': 'Hello Ladies + Gentlemen, a signed OAuth request!'
        })

    def test_oauth_param_str(self):
        _, params = self.oauth1._get_oauth_params(self.get, self.post)
        param_str = self.oauth1._get_param_str(params)
        self.assertEqual(param_str, 'include_entities=true'
            '&oauth_consumer_key=xvz1evFS4wEEPTGEFPHBog'
            '&oauth_nonce=kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg'
            '&oauth_signature_method=HMAC-SHA1'
            '&oauth_timestamp=1318622958'
            '&oauth_token=370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb'
            '&oauth_version=1.0'
            '&status=Hello%20Ladies%20%2B%20Gentlemen%2C%20a%20signed%20OAuth%20request%21')

    def test_sig_str(self):
        _, params = self.oauth1._get_oauth_params(self.get, self.post)
        param_str = self.oauth1._get_param_str(params)
        sig_str = self.oauth1._get_sig_str(self.method, self.url, param_str)
        self.assertEqual(sig_str, 'POST'
            '&https%3A%2F%2Fapi.twitter.com%2F1%2Fstatuses%2Fupdate.json'
            '&include_entities%3Dtrue'
                '%26oauth_consumer_key%3Dxvz1evFS4wEEPTGEFPHBog'
                '%26oauth_nonce%3DkYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg'
                '%26oauth_signature_method%3DHMAC-SHA1'
                '%26oauth_timestamp%3D1318622958'
                '%26oauth_token%3D370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb'
                '%26oauth_version%3D1.0'
                '%26status%3DHello%2520Ladies%2520%252B%2520Gentlemen%252C%2520a%2520signed%2520OAuth%2520request%2521')

    def test_sig_key(self):
        sig_key = self.oauth1._get_sig_key()
        self.assertEqual(sig_key, 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw'
            '&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE')

    def test_calc_sig(self):
        _, params = self.oauth1._get_oauth_params(self.get, self.post)
        param_str = self.oauth1._get_param_str(params)
        sig_str = self.oauth1._get_sig_str(self.method, self.url, param_str)
        sig_key = self.oauth1._get_sig_key()
        sig = self.oauth1._calc_sig(sig_key, sig_str)
        self.assertEqual(sig, 'tnnArxj06cWHq44gCs1OSKk/jLY=')

    def test_authorization(self):
        authorization = self.oauth1._authorization(self.method, self.url, self.get, self.post)
        self.assertEqual(authorization, 'OAuth'
            ' oauth_consumer_key="xvz1evFS4wEEPTGEFPHBog",'
            ' oauth_nonce="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",'
            ' oauth_signature="tnnArxj06cWHq44gCs1OSKk%2FjLY%3D",'
            ' oauth_signature_method="HMAC-SHA1",'
            ' oauth_timestamp="1318622958",'
            ' oauth_token="370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",'
            ' oauth_version="1.0"')

    def test_create_request(self):
        request = self.oauth1._create_request(self.method, self.url, self.get, self.post, self.headers)
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url, 'https://api.twitter.com/1/statuses/update.json?include_entities=true')
        self.assertEqual(request.body, 'status=Hello+Ladies+%2B+Gentlemen%2C+a+signed+OAuth+request%21')
        self.assertEqual(request.headers['content-length'], '62')
        self.assertTrue('authorization' in request.headers)
        self.assertTrue('content-type' in request.headers)

    def test_request(self):
        request = self.oauth1._create_request(self.method, self.url, self.get, self.post, self.headers)
        self.oauth1.session = mock.Mock()
        self.oauth1.session.prepare_request.return_value = request
        response = self.oauth1.request(self.method, self.url, self.get, self.post, self.headers)
        self.assertTrue(self.oauth1.session.send.called)
       
    def test_timestamp(self):
        result = oauth1.timestamp()
        self.assertNotEqual(result, '')

    def test_nonce(self):
        result = oauth1.nonce()
        self.assertNotEqual(result, '') 
