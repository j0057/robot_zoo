#!/usr/bin/python

__version__ = '0.2'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

# Version history:
# 0.1    initial version with hourly beep and alarm
# 0.2    moved twitter code to module twitter.py

import time
import re
import datetime

import twitter

# FFFFFFFFFUUUUUUUUUUUU ###############################################################################################

def retry(action, exc_type, frequency=0.125):
    while True:
        try:
            return action()
        except exc_type as e:
            print '#', e.__class__.__name__, e.args
            time.sleep(frequency)
            frequency *= 2

# TIME ################################################################################################################

def local_to_tuple(loc_h, loc_m):
    return (int(loc_h), int(loc_m))

def local_to_tuple_am_pm(loc_h, loc_m, am_pm):
    offset = {'AM':0, 'PM':-12}[am_pm.upper()]
    return (int(loc_h)+offset, int(loc_m))

def local_to_utc(loc_h, loc_m, s, ofs_h, ofs_m): # it's orrible!
    loc_h = int(loc_h)
    loc_m = int(loc_m)
    ofs_h = int(ofs_h)
    ofs_m = int(ofs_m)
    sign = {'-':+1, '+':-1}[s]
    loc = (loc_h * 60 + loc_m)
    ofs = (ofs_h * 60 + ofs_m) * sign
    result = loc + ofs
    result += result <     0 and +1440 or 0
    result += result >= 1440 and -1440 or 0
    result = (result / 60, result % 60)
    return result

# ALARM CODE ##########################################################################################################

def gen_alarm(a_name):
    result = '@' + a_name
    s = ' BEEP BEEP!'
    while (len(result) + len(s)) < 140:
        result += s
    return result

def send_alarms(t):
    print 'send_alarms:', t
    tm = '{0:02}{1:02}'.format(*t)
    retry = 0.5
    for (a_id, a_name) in list(TWITTER.config['alarms'][tm].items()):
        try:
            TWITTER.post_statuses_update(status=gen_alarm(a_name), in_reply_to_status_id=a_id)
            del TWITTER.config['alarms'][s][a_id]
        except FailWhale as e:
            print 'send_alarms', type(e).__name__, ':', str(e)
            print 'waiting for', retry, 's'
            time.sleep(retry)
            retry *= 2
    if not TWITTER.config['alarms'][tm]:
        del TWITTER.config['alarms'][tm]

def save_alarm(t, a_id, a_name):
    print 'save_alarm:', t, a_id, a_name
    s = '{0:02}{1:02}'.format(*t)
    if s in TWITTER.config['alarms']:
        TWITTER.config['alarms'][s][a_id] = a_name
    else:
        TWITTER.config['alarms'][s] = {a_id: a_name}

def parse_alarms(new_alarms):
    sign = {'-':+1, '+':-1}
    if not new_alarms:
        return
    TWITTER.config['latest_mention'] = max(new_alarms.keys())
    for (a_id, (a_text, a_name, a_tz)) in new_alarms.items():
        print
        print 'MENTION:', a_id, repr(a_text), a_name, a_tz
        t = None
        for regex, parse in [
            ('alarm ([01]?[0-9]|2[0-3]):([0-5][0-9]) (\\+|-)([01][0-9]|2[0-3])([0-5][0-9])', local_to_utc),
            #'alarm ([01]?[0-9]|2[0-3]):([0-5][0-9]) (AM|PM) (\\+|-)([01][0-9]|2[0-3])([0-5][0-9])', local_to_utc_am_pm),
            ('alarm ([01]?[0-9]|2[0-3]):([0-5][0-9]) (AM|PM)', local_to_tuple_am_pm),
            ('alarm ([01]?[0-9]|2[0-3]):([0-5][0-9])', local_to_tuple) ]:
            m = re.search(regex, a_text, re.I)
            if m:
                t = parse(*m.groups())
                break
        if t:
            save_alarm(t, str(a_id), a_name)
    print

# PARSE STOPWATCH #####################################################################################################

def parse_stopwatch(new_stopwatches):
    if not new_stopwatches:
        return
    for (a_id, (a_text, a_name, a_tz)) in new_stopwatches.items():
        pass

# RETWEETING MENTIONS #################################################################################################

def retweet_mentions(new_mentions):
    for id in new_mentions:
        while True:
            try:
                TWITTER.post_statuses_retweet(id)
                break
            except twitter.FailWhale as fail:
                print 'FAIL WHALE:', fail

# MAIN LOOP ###########################################################################################################

CONFIG_FILE = 'casiof91w.json'

#TWITTER = twitter.TwitterAPI(CONFIG_FILE)

def check():
    try:
        TWITTER.get_account_verify_credentials()
        twitter.log("Account verification OK! We're good to go.")
    except twitter.FailWhale as fail:
        twitter.log('FAIL WHALE: {0}', fail.args)
        twitter.log('AAIIIIIIEEE! Mein Leben! Please check OAuth credentials and retry')
        sys.exit(1)

def main():
    twitter.log('CASIO F-91W starting at {0}', time.ctime())

    days = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    beeped = False

    while True:
        time.sleep(0.5)

        t = time.time()
        loc = time.localtime(t)

        if (loc.tm_min == 0):
            retry = 1./2
            while not beeped:
                try:
                    status = 'BEEP BEEP! {0} {1} {2:02}:{3:02}:00'.format(days[loc.tm_wday], loc.tm_mday, loc.tm_hour, loc.tm_min)
                    TWITTER.post_statuses_update(status=status)
                    beeped = True
                except twitter.FailWhale as fail:
                    print 'FAIL WHALE:', fail.args
                    print 'retrying in ', retry, 's'
                    time.sleep(retry)
                    retry *= 2

        if (loc.tm_min > 0):
            beeped = False

class CasioF91W(twitter.TwitterAPI):
    DAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    MSG = u'BEEP BEEP! {0} {1} {2:02}:{3:02}:00'

    R1 = re.compile(r'alarm ([01]?[0-9]|2[0-3]):([0-5][0-9]) ([+-])([01][0-9]|2[0-3])([0-5][0-9])')
    R2 = re.compile(r'alarm ([01]?[0-9]|2[0-3]):([0-5][0-9])')
    R3 = re.compile(r'alarm (0?[1-9]|1[0-2]):([0-5][0-9]) (AM|PM) ([+-])([01][0-9]|2[0-3])([0-5][0-9])')
    R4 = re.compile(r'alarm (0?[1-9]|1[0-2]):([0-5][0-9]) (AM|PM)')

    def send_beep(self, date):
        try:
            status = self.MSG.format(self.DAYS[date.tm_wday], date.tm_mday, date.tm_hour, date.tm_min)
            self.log('Posting status: {0} ({1})', repr(status), len(status))
            self.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            fail.log_error(self)
            return False

    def save_alarm(self, alarm, mention):
        key = '{0:02}:{1:02}'.format(*alarm)
        m_id, m_sn = mention['id'], mention['user']['screen_name']
        if key not in self.config['alarms']:
            self.config['alarms'][key] = {}
        self.config['alarms'][key][m_id] = m_sn

    def parse_tweet_for_alarm(self, tweet):
        id, screen_name, text = tweet['id'], tweet['user']['screen_name'], tweet['text']

        match = self.R1.search(text) # hh:mm <+|->hhmm
        if match:
            self.log('Alarm: #{0} from @{1}: {2} --> {3}', id, screen_name, repr(text), match.groups())
            th, tm, sign, zh, zm = match.groups()
            th, tm = int(th), int(tm)
            zh, zm = int(zh), int(zm)
            sign = +1 if sign == '+' else -1
            d = datetime.datetime.combine(
                datetime.date.today(),
                datetime.time(hour=th, minute=tm)) + sign * datetime.timedelta(hours=zh, minutes=zm)
            return ((d.hour, d.minute), tweet)
        
        match = self.R2.search(text) # hh:mm
        if match:
            self.log('Alarm: #{0} from @{1}: {2} --> {3}', id, screen_name, repr(text), match.groups())
            th, tm = int(th), int(tm)
            return ((th, tm), tweet)

        match = self.R3.search(text) # hh:mm <AM|PM> <+|->hhmm
        if match:
            th, tm, am_pm, sign, zh, zm = match.groups()
            th, tm = int(th), int(tm)
            zh, zm = int(zh), int(zm)
            sign = +1 if sign == '+' else -1
            if am_pm == 'AM' and th == 12: th -= 12
            if am_pm == 'PM' and th  < 12: th += 12
            d = datetime.datetime.combine(
                datetime.date.today(),
                datetime.time(hour=th, minute=tm)) + sign * datetime.timedelta(hours=zh, minutes=zm)
            return ((d.hour, d.minute), tweet)

        match = self.R4.search(text) # hh:mm <AM|PM>
        if match:
            th, tm, am_pm = match.groups()
            th, tm = int(th), int(tm)
            if am_pm == 'AM' and th == 12: th -= 12
            if am_pm == 'PM' and th  < 12: th += 12
            return ((th, tm), tweet)

        return (None, tweet)
            
    def get_mentions(self):
        last_mention = self.config['last_mention']
        if last_mention:
            mentions = self.get_statuses_mentions(count=200, since_id=last_mention)
        else:
            mentions = self.get_statuses_mentions(count=200)
        if mentions:
            self.config['last_mention'] = max(int(m['id']) for m in mentions)
        return mentions

    def handle_mentions(self, t):
        try:
            for m in self.get_mentions():
                alarm, mention = self.parse_tweet_for_alarm(m)
                if alarm:
                    self.save_alarm(alarm, mention)
            return True
        except twitter.FailWhale as fail:
            fail.log_error(self)
            return False

    def send_alarms(self, t):
        return True
