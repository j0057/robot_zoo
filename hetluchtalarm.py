#!/usr/bin/env python2.7

__version__ = '0.1'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

import sys, time
import twitter

class Luchtalarm(twitter.TwitterAPI):
    def stuffing(self, month, year):
        year -= 2012
        return (unicode(bin(month)[2:].rjust(4, '0')).replace('0', u'\u0020').replace('1', u'\u2002')
              + unicode(bin(year )[2:].rjust(4, '0')).replace('0', u'\u0020').replace('1', u'\u2002')
              + u'\u2002')

    def luchtalarm(self, month, year):
        return (u'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
              + u' '
              + u'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
              + self.stuffing(month, year))
    
    def sound_alarm(self, t):
        status = self.luchtalarm(t.tm_mon, t.tm_year)
        try:
            self.info('Posting status: {0} ({1})', repr(status), len(status))
            self.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            self.error('FAIL WHALE: {0}', fail.args)
            return False
