import datetime
import logging
import pprint
import time

import requests

import twitter

# When starting the service, prefetch departures for 7 days.
# Every day at 00:00, update for that day and get any missing departures for the next 7 days --
# should normally only fetch one day (7 days into the future).
# If the API returns an error for some reason, retry after 2 seconds, then 4, then 8, then 16.
# If it still fails then, leave it -- the data should already have been prefetched.

def slow(sleep, call):
    time.sleep(sleep)
    return call()

class MsVlielandData(object):
    def __init__(self, log=None):
        self.log = log or logging.getLogger(__name__)
        self.departures= {}
        self._date = None

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if self._date != value:
            self.log.info('Setting current day to %s', value)
            self.update_today(*value)
            self.prefetch_week(*value)
            self.delete_old(*value)
            self._date = value
            self.log_departures()

    def log_departures(self):
        for line in pprint.pformat(self.departures).split('\n'):
            self.log.info(line)

    def get_data(self, y, m, d):
        self.log.info('Getting departures for %s', (y, m, d))
        response = requests.get(
            'http://m.rederij-doeksen.nl/api/departures', 
            params={
                'route': '2',
                'departure_date': '{0:04}-{1:02}-{2:02}'.format(y, m, d),
                'departure_port': 'H',
                'arrival_port': 'V',
                #expiry[date(3i)]': '01',
                #pax[K]': '0',
                #pax[K4]': '0',
                'pax[V]': '1',
                #pax[V65]': '0',
                #pax[S]': '0',
                #pax[SSN]': '0',
                #pax[ip]': '0',
                #pax[pax]': '0',
                #retour_journey': '1',
                #return_date': '{0:04}-{1:02}-{2:02}'.format(y, m, d),
                #ticket_type': 'twoway',
                #only_available': '0'
            },
            headers={
                'User-Agent': requests.utils.default_user_agent() + ' (robot_zoo.py; j.j.molenaar@gmail.com namens https://twitter.com/msvlieland)' })
        response.raise_for_status()
        json = response.json()
        self.log.debug(pprint.pformat(json))
        times = sorted(tuple(map(int, departure['departure_time'].split(' ')[1].split(':')[0:2]))
                       for departure in json['outwards'] 
                       if departure['other'] == 'Veerdienst Ms. Vlieland')
        return ((y,m,d), times)

    def delete_old(self, y, m, d):
        for k in self.departures.keys():
            if k < (y,m,d):
                self.log.info('Deleting old departure %s', k)
                del self.departures[k]

    def prefetch_week(self, y, m, d):
        today = datetime.date(y, m, d)
        dates = (today + datetime.timedelta(days=n) for n in xrange(1, 7))
        days = ((date.year, date.month, date.day) for date in dates)
        self.departures.update(slow(5, lambda: self.get_data(*day))
                               for day in days
                               if day not in self.departures)

    def update_today(self, y, m, d):
        k, v = self.get_data(y, m, d)
        self.departures[k] = v

class MsVlieland(object):
    prevent_dupe = 0

    def __init__(self, name, api=None):
        self.name = name
        self.log = logging.getLogger(__name__)
        self.api = api if api else twitter.TwitterAPI(name, self.log)
        self.data = MsVlielandData(log=self.log)

    @twitter.retry
    def update_departures(self, t):
        self.data.date = (t.tm_year, t.tm_mon, t.tm_mday)

    @twitter.retry
    def update_departures_for_today(self, t):
        self.data.update_today(t.tm_year, t.tm_mon, t.tm_mday)
        self.data.log_departures()

    @twitter.retry
    def sound_horn_dynamic(self, t):
        date = (t.tm_year, t.tm_mon, t.tm_mday)
        time = (t.tm_hour, t.tm_min)

        if not self.data.date: self.update_departures(t)
        if date not in self.data.departures: return True
        if time not in self.data.departures[date]: return True

        status = u'TOET TOET TOET' + (u'\u2002' * self.prevent_dupe)
        self.prevent_dupe = (self.prevent_dupe + 1) % 3
        self.log.info("Posting status: %r (%s)", status, len(status))
        self.api.post_statuses_update(status=status)
        return True

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print 'hoi'
    d = MsVlielandData()
    d.date = (2014, 8, 27)
    pprint.pprint(d.departures)
    d.date = (2014, 8, 28)
    pprint.pprint(d.departures)
