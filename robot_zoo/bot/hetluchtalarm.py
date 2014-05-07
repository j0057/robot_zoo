import logging

from .. import twitter
from .. import holidays

class Luchtalarm(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.holidays = holidays.NL(None)

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

    def feestdag(self, holiday):
        return u"({0} \u2014 vandaag geen luchtalarm)".format(holiday)

    @twitter.retry 
    def sound_alarm(self, t):
        self.holidays.year = t.tm_year
        holiday = self.holidays(t.tm_mon, t.tm_mday)
        status = (self.feestdag(holiday)
                  if holiday
                  else self.luchtalarm(t.tm_mon, t.tm_year))
        self.log.info('Posting status: %r (%d)', status, len(status))
        self.api.post_statuses_update(status=status)
        return True
