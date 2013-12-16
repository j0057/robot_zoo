import unittest

import holidays

class TestHoliday(unittest.TestCase):
    def setUp(self):
        self.nl = holidays.NL(2013)

    def test_nl_2013(self):
        assert self.nl( 1,  1) == "Nieuwjaarsdag"
        assert self.nl( 3, 31) == "Eerste Paasdag"
        assert self.nl( 4,  1) == "Tweede Paasdag"
        assert self.nl( 4, 30) == "Koninginnedag"
        assert self.nl( 4, 27) == None
        assert self.nl( 5,  4) == "Dodenherdenking"
        assert self.nl( 5,  5) == "Bevrijdingsdag"
        assert self.nl( 5,  9) == "Hemelvaartsdag"
        assert self.nl( 5, 19) == "Eerste Pinksterdag"
        assert self.nl( 5, 20) == "Tweede Pinksterdag"
        assert self.nl( 6,  9) == None
        assert self.nl(12, 25) == "Eerste Kerstdag"
        assert self.nl(12, 26) == "Tweede Kerstdag"

    def test_nl_2014(self):
        self.nl.year = 2014

        assert self.nl( 1,  1) == "Nieuwjaarsdag"
        assert self.nl( 4, 20) == "Eerste Paasdag"
        assert self.nl( 4, 21) == "Tweede Paasdag"
        assert self.nl( 4, 30) == None
        assert self.nl( 4, 27) == "Koningsdag"
        assert self.nl( 5,  4) == "Dodenherdenking"
        assert self.nl( 5,  5) == "Bevrijdingsdag"
        assert self.nl( 5, 29) == "Hemelvaartsdag"
        assert self.nl( 6,  8) == "Eerste Pinksterdag"
        assert self.nl( 6,  9) == "Tweede Pinksterdag"
        assert self.nl(12, 25) == "Eerste Kerstdag"
        assert self.nl(12, 26) == "Tweede Kerstdag"

