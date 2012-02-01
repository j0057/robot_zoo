#!/usr/bin/python

__version__ = '0.2'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

# 0.1 initial version
# 0.2 OOP rewrite

import twitter

class MsVlieland(twitter.TwitterAPI):
    prevent_dupe = 0

    def sound_horn(self, t=None):
        status = u'TOET TOET TOET' + (u'\u2002' * self.prevent_dupe)
        self.prevent_dupe = (self.prevent_dupe + 1) % 3
        try:
            self.log("Posting status: {0} ({1})", repr(status), len(status))
            self.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            self.log('FAIL WHALE: {0}', fail.args)
            return False

