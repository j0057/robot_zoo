import unittest

from robot_zoo import holidays

class TestHoliday2013(unittest.TestCase):
    def setUp(self):
        self.nl = holidays.NL(2013)

    def test_nl(self):
        assert self.nl( 1,  1) == "Nieuwjaarsdag"
        assert self.nl( 3, 31) == "Eerste Paasdag"
        assert self.nl( 4,  1) == "Tweede Paasdag"
        assert self.nl( 4, 30) == "Koninginnedag"
        assert self.nl( 4, 26) == None
        assert self.nl( 4, 27) == None
        assert self.nl( 5,  4) == "Dodenherdenking"
        assert self.nl( 5,  5) == "Bevrijdingsdag"
        assert self.nl( 5,  9) == "Hemelvaartsdag"
        assert self.nl( 5, 19) == "Eerste Pinksterdag"
        assert self.nl( 5, 20) == "Tweede Pinksterdag"
        assert self.nl( 6,  9) == None
        assert self.nl(12, 25) == "Eerste Kerstdag"
        assert self.nl(12, 26) == "Tweede Kerstdag"

class TestHoliday2014(unittest.TestCase):
    def setUp(self):
        self.nl = holidays.NL(2014)

    def test_nl(self):
        assert self.nl( 1,  1) == "Nieuwjaarsdag"
        assert self.nl( 4, 20) == "Eerste Paasdag"
        assert self.nl( 4, 21) == "Tweede Paasdag"
        assert self.nl( 4, 30) == None
        assert self.nl( 4, 26) == "Koningsdag"
        assert self.nl( 4, 27) == None
        assert self.nl( 5,  4) == "Dodenherdenking"
        assert self.nl( 5,  5) == "Bevrijdingsdag"
        assert self.nl( 5, 29) == "Hemelvaartsdag"
        assert self.nl( 6,  8) == "Eerste Pinksterdag"
        assert self.nl( 6,  9) == "Tweede Pinksterdag"
        assert self.nl(12, 25) == "Eerste Kerstdag"
        assert self.nl(12, 26) == "Tweede Kerstdag"

class TestHoliday2015(unittest.TestCase):
    def setUp(self):
        self.nl = holidays.NL(2015)

    def test_nl(self):
        assert self.nl( 1,  1) == "Nieuwjaarsdag"
        assert self.nl( 4,  5) == "Eerste Paasdag"
        assert self.nl( 4,  6) == "Tweede Paasdag"
        assert self.nl( 4, 30) == None
        assert self.nl( 4, 26) == None
        assert self.nl( 4, 27) == "Koningsdag"
        assert self.nl( 5,  4) == "Dodenherdenking"
        assert self.nl( 5,  5) == "Bevrijdingsdag"
        assert self.nl( 5, 14) == "Hemelvaartsdag"
        assert self.nl( 5, 24) == "Eerste Pinksterdag"
        assert self.nl( 5, 25) == "Tweede Pinksterdag"
        assert self.nl(12, 25) == "Eerste Kerstdag"
        assert self.nl(12, 26) == "Tweede Kerstdag"

class TestHolidayNone(unittest.TestCase):
    def setUp(self):
        self.nl = holidays.NL(None)

    def test_set_year(self):
        self.nl.year = 2014
        assert self.nl(6, 9) == "Tweede Pinksterdag"
