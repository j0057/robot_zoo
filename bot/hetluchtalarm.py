import twitter

class Luchtalarm(object):
    def __init__(self, name, api=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)

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

    def tweede_paasdag_2013(self, t):
        status = "Vandaag als het goed is geen luchtalarm, vrolijk Pasen!"
        try:
            self.api.info('Posting status: {0} ({1})', repr(status), len(status))
            self.api.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            fail.log_error(self.api)
            return False
    
    def sound_alarm(self, t):
        status = self.luchtalarm(t.tm_mon, t.tm_year)
        try:
            self.api.info('Posting status: {0} ({1})', repr(status), len(status))
            self.api.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            fail.log_error(self.api)
            return False
