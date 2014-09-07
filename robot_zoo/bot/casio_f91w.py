import time
import re
import datetime
import logging

import pytz

today = datetime.date.today

from .. import twitter

CET = pytz.timezone('Europe/Amsterdam')
UTC = pytz.utc

class CasioF91W(object):
    DAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    MSG = u'BEEP BEEP! {0} {1} {2:02}:{3:02}:00'

    R1 = re.compile(r'alarm ([01]?[0-9]|2[0-3]):([0-5][0-9]) ([+-])([01][0-9]|2[0-3])([0-5][0-9])')
    R2 = re.compile(r'alarm (0?[1-9]|1[0-2]):([0-5][0-9]) (AM|PM) ([+-])([01][0-9]|2[0-3])([0-5][0-9])')
    R3 = re.compile(r'alarm (0?[1-9]|1[0-2]):([0-5][0-9]) (AM|PM)')
    R4 = re.compile(r'alarm ([01]?[0-9]|2[0-3]):([0-5][0-9])')

    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.state = twitter.Configuration(
            config_file=os.environ.get('ROBOT_ZOO_LIB', '.') + '/' + self.name + '.json',
            default=lambda: {
                'alarms': {},
                'last_mention': None })

    @twitter.retry
    def send_beep(self, t):
        status = self.MSG.format(self.DAYS[t.tm_wday], t.tm_mday, t.tm_hour, t.tm_min)
        self.log.info('Posting status: %s (%d)', repr(status), len(status))
        self.api.post_statuses_update(status=status)
        return True

    def save_alarm(self, alarm, mention):
        key = '{0:02}:{1:02}'.format(*alarm)
        m_id, m_sn = mention['id'], mention['user']['screen_name']
        if key not in self.state.config['alarms']:
            self.state.config['alarms'][key] = {}
        self.state.config['alarms'][key][m_id] = m_sn

    def parse_tweet_for_alarm(self, tweet):
        id, screen_name, text = tweet['id'], tweet['user']['screen_name'], tweet['text']

        match = self.R1.search(text) # hh:mm <+|->hhmm
        if match:
            self.log.info('Alarm: #%d from @%s: %s --> %r', id, screen_name, repr(text), match.groups())
            th, tm, sign, zh, zm = match.groups()
            th, tm = int(th), int(tm)
            zh, zm = int(zh), int(zm)
            sign = +1 if sign == '+' else -1
            base = datetime.datetime.combine(today(), datetime.time(hour=th, minute=tm)).replace(tzinfo=UTC)
            offset = sign * datetime.timedelta(hours=zh, minutes=zm)
            d = (base - offset).astimezone(CET)
            return ((d.hour, d.minute), tweet)
        
        match = self.R2.search(text) # hh:mm <AM|PM> <+|->hhmm
        if match:
            self.log.info('Alarm: #%d from @%s: %s --> %r', id, screen_name, repr(text), match.groups())
            th, tm, am_pm, sign, zh, zm = match.groups()
            th, tm = int(th), int(tm)
            zh, zm = int(zh), int(zm)
            sign = +1 if sign == '+' else -1
            if am_pm == 'AM' and th == 12: th -= 12
            if am_pm == 'PM' and th  < 12: th += 12
            base = datetime.datetime.combine(today(), datetime.time(hour=th, minute=tm)).replace(tzinfo=UTC)
            offset = sign * datetime.timedelta(hours=zh, minutes=zm)
            d = (base - offset).astimezone(CET)
            return ((d.hour, d.minute), tweet)

        match = self.R3.search(text) # hh:mm <AM|PM>
        if match:
            self.log.info('Alarm: #%d from @%s: %s --> %r', id, screen_name, repr(text), match.groups())
            th, tm, am_pm = match.groups()
            th, tm = int(th), int(tm)
            if am_pm == 'AM' and th == 12: th -= 12
            if am_pm == 'PM' and th  < 12: th += 12
            return ((th, tm), tweet)

        match = self.R4.search(text) # hh:mm
        if match:
            self.log.info('Alarm: #%d from @%s: %s --> %r', id, screen_name, repr(text), match.groups())
            th, tm = match.groups()
            th, tm = int(th), int(tm)
            return ((th, tm), tweet)

        return (None, tweet)
            
    def get_mentions(self):
        last_mention = self.state.config['last_mention']
        if last_mention:
            mentions = self.api.get_statuses_mentions_timeline(count=200, since_id=last_mention)
        else:
            mentions = self.api.get_statuses_mentions_timeline(count=200)
        if mentions:
            self.state.config['last_mention'] = str(max(int(m['id']) for m in mentions))
        return mentions

    @twitter.retry
    def handle_mentions(self, t):
        dirty = False
        for m in self.get_mentions():
            alarm, mention = self.parse_tweet_for_alarm(m)
            if alarm:
                self.save_alarm(alarm, mention)
                dirty = True
        if dirty:
            self.state.save()
        return True

    @twitter.retry
    def send_alarms(self, t):
        key = '{0:02}:{1:02}'.format(t.tm_hour, t.tm_min)
        if key in self.state.config['alarms']:
            for (tid, screen_name) in self.state.config['alarms'][key].items():
                status = u'@{0}'.format(screen_name)
                while len(status) < 130:
                    status += u' BEEP BEEP!'
                self.log.info('Posting status: %s (%r)', repr(status), len(status))
                self.api.post_statuses_update(status=status, in_reply_to_status_id=tid)
                del self.state.config['alarms'][key][tid]
                if not self.state.config['alarms'][key]:
                    del self.state.config['alarms'][key]
            self.state.save()
        return True
