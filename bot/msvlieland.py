import logging

import twitter

class MsVlieland(object):
    prevent_dupe = 0

    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)

    @twitter.retry
    def sound_horn(self, t=None):
        status = u'TOET TOET TOET' + (u'\u2002' * self.prevent_dupe)
        self.prevent_dupe = (self.prevent_dupe + 1) % 3
        self.log.info("Posting status: {0} ({1})", repr(status), len(status))
        self.api.post_statuses_update(status=status)
        return True

    @twitter.retry
    def _(self, t=None):
        return True # succesvol niets doen

