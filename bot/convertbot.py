import logging
import re
import random

import twitter

class ConvertBot(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)

    @twitter.retry
    def post_time(self, t, randint=random.randint):
        if randint(0, 2000) != 42:
            return

        base = randint(2, 36)
        text = 'Current {0} time in base {1} is {2}:{3}'.format(
            'UTC+2' if t.tm_isdst else 'UTC+1',
            base,
            to_radix(base, t.tm_hour).rjust(2, '0') or '00',
            to_radix(base, t.tm_min).rjust(2, '0') or '00')

        self.log.info('Posting status: %r (%d)', text, len(text))
        self.api.post_statuses_update(status=text)

def from_radix(r, s, d='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return 0 if not s else (d.find(s[-1]) + r * from_radix(r, s[:-1]))

def to_radix(r, n, d='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return '' if not n else (to_radix(r, n//r) + d[n%r])

def convert( f, t, s):
    return to_radix(t, from_radix(f, s))
