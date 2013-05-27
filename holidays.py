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

class BE(Holidays):
    def __init__(self, year):
        super(BE, self).__init__(year,
            ("Nieuwjaar",                       lambda date: date == self.day(1, 1)),
            ("Pasen",                           lambda date: date == self.easter(+0)),
            ("Paasmaandag",                     lambda date: date == self.easter(+1)),
            ("Dag van de Arbeid",               lambda date: date == self.day(5, 1)),
            ("Hemelvaart",                      lambda date: date == self.easter(+40)),
            ("Pinksteren",                      lambda date: date == self.easter(+49)),
            ("Pinkstermaandag",                 lambda date: date == self.easter(+50)),
            ("Belgische Nationale Feestdag",    lambda date: date == self.day(7, 21)),
            ("O.L.Vrouw Hemelvaart",            lambda date: date == self.day(8, 15)),
            ("Allerheiligen",                   lambda date: date == self.day(11, 1)),
            ("Wapenstilstand",                  lambda date: date == self.day(11, 11)),
            ("Kerstmis",                        lambda date: date == self.day(12, 25)))

if __name__ == "__main__":

    nl = NL(2013)

    assert nl( 1,  1) == "Nieuwjaarsdag"
    assert nl( 3, 31) == "Eerste Paasdag"
    assert nl( 4,  1) == "Tweede Paasdag"
    assert nl( 4, 30) == "Koninginnedag"
    assert nl( 4, 27) == None
    assert nl( 5,  4) == "Dodenherdenking"
    assert nl( 5,  5) == "Bevrijdingsdag"
    assert nl( 5,  9) == "Hemelvaartsdag"
    assert nl( 5, 19) == "Eerste Pinksterdag"
    assert nl( 5, 20) == "Tweede Pinksterdag"
    assert nl( 6,  9) == None
    assert nl(12, 25) == "Eerste Kerstdag"
    assert nl(12, 26) == "Tweede Kerstdag"

    nl.year = 2014

    assert nl( 1,  1) == "Nieuwjaarsdag"
    assert nl( 4, 20) == "Eerste Paasdag"
    assert nl( 4, 21) == "Tweede Paasdag"
    assert nl( 4, 30) == None
    assert nl( 4, 27) == "Koningsdag"
    assert nl( 5,  4) == "Dodenherdenking"
    assert nl( 5,  5) == "Bevrijdingsdag"
    assert nl( 5, 29) == "Hemelvaartsdag"
    assert nl( 6,  8) == "Eerste Pinksterdag"
    assert nl( 6,  9) == "Tweede Pinksterdag"
    assert nl(12, 25) == "Eerste Kerstdag"
    assert nl(12, 26) == "Tweede Kerstdag"

