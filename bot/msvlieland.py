import datetime
import logging

import requests

import twitter

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

    def get_data(self, y, m, d):
        self.log.info('Getting departures for %s', (y, m, d))
        response = requests.get(
            'http://m.rederij-doeksen.nl/api/departures', 
            params={
                'departure_date': '{0:04}-{1:02}-{2:02}'.format(y, m, d),
                'departure_port': 'H',
                'arrival_port': 'V',
                'pax[V]': '1',
                'route': '2'},
            headers={
                'User-Agent': requests.utils.default_user_agent() + ' (robot_zoo.py; j.j.molenaar@gmail.com namens https://twitter.com/msvlieland)' })
        response.raise_for_status()
        json = response.json()
        times = [ tuple(map(int, departure['departure_time'].split(' ')[1].split(':')[0:2]))
                  for departure in json['outwards'] 
                  if departure['other'] == 'Veerdienst' ]
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
        self.departures.update(self.get_data(*day)
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
    def sound_horn_dynamic(self, t):
        date = (t.tm_year, t.tm_mon, t.tm_mday)
        time = (t.tm_hour, t.tm_min)

        self.data.date = date

        if date not in self.data.departures: return True
        if time not in self.data.departures[date]: return True

        status = u'TOET TOET TOET' + (u'\u2002' * self.prevent_dupe)
        self.prevent_dupe = (self.prevent_dupe + 1) % 3
        self.log.info("Posting status: {0} ({1})", repr(status), len(status))
        self.api.post_statuses_update(status=status)
        return True

if __name__ == '__main__':
    from pprint import pprint
    d = MsVlielandData()
    d.date = (2014, 2, 5)
    pprint(d.departures)
    d.date = (2014, 2, 6)
    pprint(d.departures)
