#!/usr/bin/python

__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

from datetime import datetime

import ephem
from dateutil import tz

import twitter

TZ_UTC = tz.gettz('UTC')
TZ_CET = tz.gettz('Europe/Amsterdam')

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
        self.year = None
        if year is not None:
            self.initialize(year)

    def initialize(self, year):
        time = ephem.Date(datetime(year, 1, 1, 0, 0, 0, tzinfo=TZ_CET).astimezone(TZ_UTC))
        phase = self.first_phase(time)
        self.year = year 
        self.phases = { (d.year, d.month, d.day, d.hour, d.minute): (d.hour, d.minute, d.second, phase)
                        for (phase, d) in self.calc_phases(time, phase) }

    def first_phase(self, year):
        times = [ (i, f(year)) for (i, f) in enumerate(PHASE_FUNC) ]
        first = min(times, key=lambda t: t[1])
        return first[0]

    def calc_phases(self, time, phase):
        while True:
            time = PHASE_FUNC[phase](time)
            if time.datetime().replace(tzinfo=TZ_UTC).astimezone(TZ_CET).year != self.year:
                break
            yield (phase, time.datetime().replace(tzinfo=TZ_UTC).astimezone(TZ_CET))
            phase = (phase + 1) % 4

    def get(self, key):
        return self.phases.get(key, None)

class Maanfase(twitter.TwitterAPI):
    def __init__(self, name):
        super(Maanfase, self).__init__(name)
        self.moon_model = MoonModel()

    def post_phase(self, t):
        if self.moon_model.year != t.tm_year:
            self.log("Initializing for year {0}", t.tm_year)
            self.moon_model.initialize(t.tm_year)

        result = self.moon_model.get((t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min))
        if not result:
            return True

        h, m, s, phase = result
        status = u"Om {0}:{1}:{2} is het {3}.".format(h, m, s, PHASE_NAME[phase])

        try:
            self.log("Posting status: {0} ({1})", repr(status), len(status))
            self.post_statuses_update(status=status)
            return True
        except twitter.FailWhale as fail:
            self.log("FAIL WHALE: {0}", repr(self.args))
            return False

if __name__ == '__main__':
    mm = MoonModel(2013)
    ph = mm.first_phase(2013)
    print ph
    for x in mm.calc_phases(2013, ph):
        print x

    from pprint import pprint
    pprint(mm.phases)

