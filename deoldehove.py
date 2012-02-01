#!/usr/bin/python

__version__ = '0.4'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

# version history:
# 0.1   initial version, sounds every hour
# 0.2   added sound at half hours
# 0.21  added hack to prevent duplicate status fail whale
# 0.3   moved twitter code to module twitter.py
# 0.4   converted to OOP code

import twitter

class DeOldehove(twitter.TwitterAPI):
    def post_status(self, t, sounds):
        sep = sounds['separator']
        snd = sounds['sound']

        stuffing = t.tm_hour if t.tm_min == 30 else 0
        times = 1 if t.tm_min == 30 else t.tm_hour
        if times > 12: times -= 12
        if times <  1: times += 12

        status = sep.join([snd] * times) + (u'\u2002' * stuffing)

        try:
            self.log('Posting status: {0} ({1})', repr(status), len(status))
            self.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            self.log('FAIL WHALE: {0}', fail.args)
            return False

    def sound_clock(self, t):
        return self.post_status(t, self.config['default'])

    def sound_clock_lwd_culinair(self, t):
        return self.post_status(t, self.config['ljouwert culinair 2010'])

    def sound_clock_into_the_grave(self, t):
        return self.post_status(t, self.config['metal'])



