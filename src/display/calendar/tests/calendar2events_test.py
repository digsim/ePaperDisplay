# -*- coding: utf-8 -*-
import pytz
from display.calendar.calendar2events import Calendar2Events
#from ..calendar2itc import Calendar2ITC
from datetime import datetime, timedelta
from unittest import TestCase, skip, skipIf
import os
import sys
import logging

class TestCalendar2Events(TestCase):
    """Tests the behavior of the calendar parsing"""

    def setUp(self):
        self.cwd =  os.path.dirname(os.path.abspath(__file__))
        self.calendarfile = os.path.join(self.cwd, 'resources/basic.ics')
        self.calendarfile2 = os.path.join(self.cwd, 'resources/noitc.ics')
        tz = pytz.timezone('Europe/Berlin')

        self.startdate1, self.enddate1 = self.getStartAndEndtime('20160926')
        # This date has one item, but also the before and the day after have one item
        self.startdate2 = self.startdate1+timedelta(days=1)
        self.enddate2 = self.enddate1+timedelta(days=1)
        # This date should contain a repeating item but is not the date, the entry was first defined
        self.startdate3 = self.startdate1 + timedelta(days=4)
        self.enddate3 = self.enddate1 + timedelta(days=4)
        # This date should not contain the repeating item anymore
        self.startdate4 = self.startdate1 + timedelta(days=11)
        self.enddate4 = self.enddate1 + timedelta(days=11)




    def testSimpleEventParsing(self):
        calendar = Calendar2Events(self.calendarfile, None, None, self.startdate2, self.enddate2, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        self.assertEqual(len(events), 1, 'There are differences in the number of calendar items found for the specified date range ('+self.startdate2.strftime('%Y-%m-%d')+','+self.enddate2.strftime('%Y-%m-%d')+')')

    #@skip("Recurring events are not yet supported")
    def testRecurringEventParsing(self):
        calendar = Calendar2Events(self.calendarfile, None, None, self.startdate3, self.enddate4, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        self.assertEqual(len(events), 4,
                         'There are differences in the number of calendar items found for the specified date range (' + self.startdate3.strftime('%Y-%m-%d') + ',' + self.enddate4.strftime('%Y-%m-%d') + ')')
        for ev in events:
            self.assertEqual('Daily Sync', ev.comment, 'Differences in comments')
            self.assertEqual('UBS STMP.Wave_25:meet_int', ev.contract, 'Differences in contract')

    def testNoEventsFoundParsing(self):
        calendar = Calendar2Events(self.calendarfile, None, None, self.startdate4, self.enddate4, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        self.assertEqual(len(events), 0, 'There are differences in the number of calendar items found for the specified date range (' + self.startdate4.strftime('%Y-%m-%d') + ',' + self.enddate4.strftime('%Y-%m-%d') + ')')

    def testRecurring(self):
        calendarfile = os.path.join(self.cwd, 'resources/recurring.ics')
        startdate, enddate = self.getStartAndEndtime('20161004')
        enddate = enddate #+ timedelta(days=1)
        calendar = Calendar2Events(calendarfile, None, None, startdate, enddate, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        self.assertEqual(len(events), 1,
                         'There are differences in the number of calendar items found for the specified date range')
        for ev in events:
            self.assertEqual('Scrum Sync', ev.comment, 'Differences in comments')
            self.assertEqual('UBS STMP.Wave_26:meet_int', ev.contract, 'Differences in contract')
            self.assertEqual('04-10-2016 14:00:00', ev.getStartDateTimeString(), 'Difference in start date')
            self.assertEqual('14:30', ev.getEndTimeString(), 'Difference in start date')


    def testRecurringExceptionLast(self):
        calendarfile = os.path.join(self.cwd, 'resources/recurring_exception_last.ics')
        startdate, enddate = self.getStartAndEndtime('20170103')
        enddate = enddate + timedelta(days=1)
        calendar = Calendar2Events(calendarfile, None, None, startdate, enddate, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        events.sort(key=lambda k: k.startdatetime)
        self.assertEqual(len(events), 2,
                         'There are differences in the number of calendar items found for the specified date range')

        self.assertEqual('03-01-2017 14:00:00', events[0].getStartDateTimeString(), 'Difference in start date (first)')
        self.assertEqual('14:30', events[0].getEndTimeString(), 'Difference in start date (first)')

        self.assertEqual('04-01-2017 14:15:00', events[1].getStartDateTimeString(), 'Difference in start date (second)')
        self.assertEqual('14:45', events[1].getEndTimeString(), 'Difference in start date (second)')


    def testRecurringExceptionFirst(self):
        calendarfile = os.path.join(self.cwd, 'resources/recurring_exception_first.ics')
        startdate, enddate = self.getStartAndEndtime('20170103')
        enddate = enddate  + timedelta(days=1)
        calendar = Calendar2Events(calendarfile, None, None, startdate, enddate, 'ADNOVUM')
        events = calendar.fetchCalendarEvents()
        events.sort(key=lambda k: k.startdatetime)
        self.assertEqual(len(events), 2,
                         'There are differences in the number of calendar items found for the specified date range')

        self.assertEqual('03-01-2017 14:00:00', events[0].getStartDateTimeString(), 'Difference in start date (first)')
        self.assertEqual('14:30', events[0].getEndTimeString(), 'Difference in start date (first)')




    def getStartAndEndtime(self, date):
        tz = pytz.timezone('Europe/Berlin')
        unlocalized = datetime.strptime(date, '%Y%m%d')
        localized = tz.localize(datetime.combine(unlocalized, datetime.min.time()))
        startdate = localized.astimezone(pytz.utc)
        localized = tz.localize(datetime.combine(unlocalized, datetime.max.time()))
        enddate = localized.astimezone(pytz.utc)
        return startdate, enddate