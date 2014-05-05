import logging

import twitter

class Luchtalarm(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)

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

    @twitter.retry
    def tweede_paasdag_2013(self, t):
        status = "Vandaag als het goed is geen luchtalarm, vrolijk Pasen!"
        self.log.info('Posting status: %r (%d)', status, len(status))
        self.api.post_statuses_update(status=status)
        return True

    @twitter.retry
    def bevrijdingsdag_2014(self, t):
        status = u"\u2002"
        self.log.info('Posting status: %r (%d)', status, len(status))
        self.api.post_statuses_update(status=status)
        return True

    @twitter.retry 
    def sound_alarm(self, t):
        status = self.luchtalarm(t.tm_mon, t.tm_year)
        self.log.info('Posting status: %s (%d)', status, len(status))
        self.api.post_statuses_update(status=status)
        return True
