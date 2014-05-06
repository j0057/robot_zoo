#!/usr/bin/env python2.7

import datetime

import dateutil.easter
import dateutil.relativedelta

class Holidays(object):
    def __init__(self, year, *rules):
        self.rules = rules
        self.year = year

    def __call__(self, month, day):
        d = datetime.date(self.year, month, day)
        for (result, test) in self.rules:
            if test(d):
                return result

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        self._year = value
        self.easter_date = dateutil.easter.easter(value)

    def day(self, month, day):
        return datetime.date(self.year, month, day)

    def easter(self, days):
        return self.easter_date + dateutil.relativedelta.relativedelta(days=days)

    def is_sunday(self, month, day):
        return datetime.date(self.year, month, day).weekday() == 6

class NL(Holidays):
    def __init__(self, year):
        super(NL, self).__init__(year,
            ("Nieuwjaarsdag",      lambda d: d == self.day(1, 1)),
            ("Eerste Paasdag",     lambda d: d == self.easter(+0)),
            ("Tweede Paasdag",     lambda d: d == self.easter(+1)),
            ("Koninginnedag",      lambda d: (1949 <= d.year <= 2013) 
                                   and (d == (self.is_sunday(4, 30) and self.day(4, 29) or self.day(4, 30)))),
            ("Koningsdag",         lambda d: (2014 <= d.year)
                                   and (d == (self.is_sunday(4, 27) and self.day(4, 26) or self.day(4, 27)))),
            ("Dodenherdenking",    lambda d: d == self.day(5, 4)),
            ("Bevrijdingsdag",     lambda d: d == self.day(5, 5)),
            ("Hemelvaartsdag",     lambda d: d == self.easter(+39)),
            ("Eerste Pinksterdag", lambda d: d == self.easter(+49)),
            ("Tweede Pinksterdag", lambda d: d == self.easter(+50)),
            ("Eerste Kerstdag",    lambda d: d == self.day(12, 25)),
            ("Tweede Kerstdag",    lambda d: d == self.day(12, 26)))
