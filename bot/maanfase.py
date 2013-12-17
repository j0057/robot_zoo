#!/usr/bin/python

__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

from datetime import datetime

import ephem
import pytz

import twitter

TZ_UTC = pytz.utc
TZ_CET = pytz.timezone('Europe/Amsterdam')

PHASE_NAME = ['nieuwe maan', 
              'eerste kwartier', 
              'volle maan', 
              'laatste kwartier']

PHASE_FUNC = [ephem.next_new_moon,
              ephem.next_first_quarter_moon,
              ephem.next_full_moon,
              ephem.next_last_quarter_moon]

class MoonModel(object):
    def __init__(self, year=None):
        self.year = year

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year
        if year:
            dt = datetime(year, 1, 1, 0, 0, 0, tzinfo=TZ_CET).astimezone(TZ_UTC)
            time = ephem.Date(dt)
            phase = self._first_phase(time)
            self._phases = { (d.year, d.month, d.day, d.hour, d.minute): (d.hour, d.minute, d.second, phase)
                             for (phase, d) in self._calc_phases(time, phase) }
        else:
            self._phases = {} 

    def _first_phase(self, year):
        times = [ (i, f(year)) for (i, f) in enumerate(PHASE_FUNC) ]
        first = min(times, key=lambda t: t[1])
        return first[0]

    def _calc_phases(self, time, phase):
        while True:
            time = PHASE_FUNC[phase](time)
            if time.datetime().replace(tzinfo=TZ_UTC).astimezone(TZ_CET).year != self.year:
                break
            yield (phase, time.datetime().replace(tzinfo=TZ_UTC).astimezone(TZ_CET))
            phase = (phase + 1) % 4

    def __getitem__(self, key):
        return self._phases.get(key, None)

class Maanfase(object):
    def __init__(self, name, api=None):
        self.name = name
        self.api = api if api else twitter.TwitterAPI(name)
        self.moon = MoonModel()

    def post_phase(self, t):
        if self.moon.year != t.tm_year:
            self.api.log("Initializing for year {0}", t.tm_year)
            self.moon.year = t.tm_year

        result = self.moon[t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min]
        if not result:
            return True

        h, m, s, phase = result
        status = u"Om {0:02}:{1:02}:{2:02} is het {3}.".format(h, m, s, PHASE_NAME[phase])

        try:
            self.api.log("Posting status: {0} ({1})", repr(status), len(status))
            self.api.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            fail.log_error(self.api)
            return False

