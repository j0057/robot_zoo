import logging

from .. import twitter

# 2038-01-19 03:14:07 UTC

class Y2K38Warning(object):
    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)

    def _tweet_message(self, message):
        self.log.info("Posting status: %r (%d)", message, len(message))
        self.api.post_statuses_update(status=message)
        return True

    def _tweet_remaining(self, left, unit):
        message = "Only {0} {1} remaining until Y2K38!".format(left, unit)
        return self._tweet_message(message)

    @twitter.retry
    def yearly(self, t): 
        left = 2038 - t.tm_year
        return self._tweet_remaining(left, 'years' if left != 1 else 'year')

    @twitter.retry
    def monthly(self, t): 
        left = ((1 - t.tm_mon) % 12) or 12
        return self._tweet_remaining(left, 'months' if left != 1 else 'month')

    @twitter.retry
    def daily(self, t):
        left = ((19 - t.tm_mday) % 31) or 31
        return self._tweet_remaining(left, 'days' if left != 1 else 'day')

    @twitter.retry
    def hourly(self, t): 
        left = ((3 - t.tm_hour) % 24) or 24
        return self._tweet_remaining(left, 'hours' if left != 1 else 'hour')

    @twitter.retry
    def every_minute(self, t):
        left = ((14 - t.tm_min) % 60) or 60
        return self._tweet_remaining(left, 'minutes' if left != 1 else 'minute')

    @twitter.retry
    def every_second(self, t): 
        left = ((7 - t.tm_sec) % 60) or 60
        return self._tweet_remaining(left, 'seconds' if left != 1 else 'second')

    @twitter.retry
    def zero(self, t):
        message = "Y2K38 is here! Watch out for falling airplanes!"
        return self._tweet_message(message)


