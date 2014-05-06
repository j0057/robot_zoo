import logging

from .. import twitter

class DeOldehove(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)

    @twitter.retry
    def post_status(self, t, sounds):
        sep = sounds['separator']
        snd = sounds['sound']

        stuffing = (t.tm_hour or 24) if t.tm_min == 30 else 0

        times = 1 if t.tm_min == 30 else t.tm_hour
        if times > 12: 
            times -= 12
        if times <  1: 
            times += 12

        status = sep.join([snd] * times) + (u'\u2002' * stuffing)

        self.log.info('Posting status: %r (%d)', status, len(status))
        self.api.post_statuses_update(status=status)

        return True

    def sound_clock(self, t):
        return self.post_status(t, self.api.config['default'])

    def sound_clock_lwd_culinair(self, t):
        return self.post_status(t, self.api.config['ljouwert culinair 2010'])

    def sound_clock_into_the_grave(self, t):
        return self.post_status(t, self.api.config['metal'])



