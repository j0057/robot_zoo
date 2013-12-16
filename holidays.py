#!/usr/bin/env python2.7

import datetime

import dateutil.easter
import dateutil.relativedelta

class Holidays(object):
    def __init__(self, year, *rules):
        self.rules = rules
        self.year = year

    def __call__(self, month, day):
        for (result, test) in self.rules:
            if test(datetime.date(self.year, month, day)):
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

class NL(Holidays):
    def __init__(self, year):
        super(NL, self).__init__(year,
            ("Nieuwjaarsdag",                   lambda date: date == self.day(1, 1)),
            ("Eerste Paasdag",                  lambda date: date == self.easter(+0)),
            ("Tweede Paasdag",                  lambda date: date == self.easter(+1)),
            ("Koninginnedag",                   lambda date: date == self.day(4, 30) and (1949 <= date.year <= 2013)),
            ("Koningsdag",                      lambda date: date == self.day(4, 27) and (2014 <= date.year)),
            ("Dodenherdenking",                 lambda date: date == self.day(5, 4)),
            ("Bevrijdingsdag",                  lambda date: date == self.day(5, 5)),
            ("Hemelvaartsdag",                  lambda date: date == self.easter(+39)),
            ("Eerste Pinksterdag",              lambda date: date == self.easter(+49)),
            ("Tweede Pinksterdag",              lambda date: date == self.easter(+50)),
            ("Eerste Kerstdag",                 lambda date: date == self.day(12, 25)),
            ("Tweede Kerstdag",                 lambda date: date == self.day(12, 26)))
