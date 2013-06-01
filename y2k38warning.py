
import twitter

# 2038-01-19 03:14:07 UTC

class Y2K38Warning(twitter.TwitterAPI):
    def _tweet_remaining(self, left, unit):
        message = "Only {0} {1} remaining until Y2K38!".format(left, unit)
        return self._tweet_message(message)

    def _tweet_message(self, message):
        try:
            self.log("Posting status: {0} ({1})", repr(message), len(message))
            self.post_statuses_update(status=message)
            return True
        except twitter.FailWhale as fail:
            self.log("FAIL WHALE: {0}", fail.args)
            return False

    def yearly(self, t): 
        left = 2038 - t.tm_year
        return self._tweet_remaining(left, 'years' if left != 1 else 'year')

    def monthly(self, t): 
        left = ((1 - t.tm_month) % 12) or 12
        return self._tweet_remaining(left, 'months' if left != 1 else 'month')

    def daily(self, t):
        left = ((19 - t.tm_day) % 31) or 31
        return self._tweet_remaining(left, 'days' if left != 1 else 'day')

    def hourly(self, t): 
        left = ((3 - t.tm_hour) % 24) or 24
        return self._tweet_remaining(left, 'hours' if left != 1 else 'hour')

    def every_minute(self, t):
        left = ((14 - t.tm_min) % 60) or 60
        return self._tweet_remaining(left, 'minutes' if left != 1 else 'minute')

    def every_second(self, t): 
        left = ((7 - t.tm_sec) % 60) or 60
        return self._tweet_remaining(left, 'seconds' if left != 1 else 'second')

    def zero(self, t):
        message = "Y2K38 is here! Watch out for falling airplanes!!!"
        return self._tweet_message(message)

        

