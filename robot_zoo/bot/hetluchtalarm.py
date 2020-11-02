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
        return (bin(month)[2:].rjust(4, '0') + bin(year)[2:].rjust(4, '0')).replace('0', '\u0020').replace('1', '\u00ad') + '\u00ad'

    def luchtalarm(self, month, year):
        return ('Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
              + ' '
              + 'Hooooooooooooeeeeeeeeeeeeeeuuuuuuuuuuiiiiiiiiiii!'
              + self.stuffing(month, year))

    def feestdag(self, holiday):
        return f"{holiday} \u2014 vandaag geen luchtalarm"

    @twitter.retry
    def sound_alarm(self, t):
        self.holidays.year = t.tm_year
        status = self.feestdag(holiday) if (holiday := self.feestdag(t.tm_mon, t.tm_mday)) else self.luchtalarm(t.tm_mon, t.tm_year)
        self.log.info('Posting status: %r (%d)', status, len(status))
        self.api.post_statuses_update(status=status)
        return True
