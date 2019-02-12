# -*- coding: utf-8 -*-

from unittest import TestCase
import icalendar
import os

class TestEncoding(TestCase):

    def test_apple_xlocation(self):
        directory = os.path.dirname(__file__)
        data = open(os.path.join(directory, 'resources/x_location.ics'), 'rb').read()
        cal = icalendar.Calendar.from_ical(data)