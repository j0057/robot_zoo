
TwitterAPI
==========

TwitterAPI allows me to connect to twitter with a minimum of code. It also has a cron-style
task scheduler.

CronRunner
----------

CronRunner in the module pycron.py is a basic crontab-style task scheduler. It has a little
more resolution than your average cron; you can plan down to the second and up to the year.
Basically it looks like this:

    def some_periodic_function(t):
        # t is the time.struct_time with the current date/time info
        pass

    cron = CronRunner(
        ('*        00-59/30 *        *        *        *        *        ', some_periodic_function))
    cron.run_local()


TwitterAPI
----------

TwitterAPI makes it really easy to do stuff against Twitter's REST API. Refer to http://dev.twitter.com
for documentation about the API itself.

Example:  http://dev.twitter.com/docs/api/1/post/statuses/update

    twtr = twitter.TwitterAPI('johndoeveloper')
    twtr.post_statuses_update(status='My first tweet from Python!')

Example: http://dev.twitter.com/docs/api/1/post/statuses/retweet/%3Aid

    tweet_id = <some id>

    twtr = twitter.TwitterAPI('johndoeveloper')
    twtr.post_statuses_retweet(tweet_id)
   
So keyword arguments are converted to GET parameters, and positional parameters are converted to elements
in the URL's path.
 
