# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import requests
import tempfile
import pytz
import datetime
import codecs
import sys
import itertools
import operator
from .calendarEvent import CalendarEvent
from dateutil import rrule
from icalendar import Calendar
from pprint import pprint
from progressbar import Bar, ProgressBar, SimpleProgress


class Calendar2Events(object):
    """This is the class fetching a calendar and for each entry creats a corresponding itc entry"""

    def __init__(self, calendarurl, username, password, start, end, verifySSL=True):
        """Constructor"""
        self.__log = logging.getLogger('Tube4Droid')
        self.__calendarurl = calendarurl
        self.__username = username
        self.__password = password
        self.__start = start
        self.__end = end
        self.__verifySSL = verifySSL
        #self.__proxies = {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080',}
        self.__proxies = {}

    def fetchCalendarEvents(self):
        """
        Downloads the ical file and parses it for events.

        :return: a list of events
        """
        if self.__calendarurl.startswith('http'):
            self.__log.debug('Verify SSL is %s',str(self.__verifySSL))
            response = requests.get(self.__calendarurl, auth=(self.__username, self.__password), stream=True, verify=self.__verifySSL, proxies=self.__proxies)
            if not response.ok:
                self.__log.error('Something went terribly wrong: %s %s', response.status_code, response.reason)
                sys.exit(3)
            with tempfile.NamedTemporaryFile('w+b') as tmp:
                self.__log.debug('Saving calendar to file %s', tmp.name)
                tmp.write(response.content)
                tmp.seek(0)
                a = tmp.read()
                #a = a.decode('utf-8', 'ignore')
                cal = Calendar.from_ical(a)
        else:
            #with open(self.__calendarurl, 'r', encoding='utf8') as calfile: #works with python3 but not with python2
            with codecs.open(self.__calendarurl, 'r', encoding='utf-8', errors='ignore') as calfile:
                cal = Calendar.from_ical(calfile.read())

        events = self.prepareWorkingUnits(cal)
        return events

    def prepareWorkingUnits(self, cal):
        """
        for a given calendar (ics file), walks over the <code>vevent</code> in this file and create for each one
        an <code>CalendarEvent</code>.

        :param cal: the <code>Calendar</code> to parse
        :return: a list of <code>CalendarEvents</code>
        """
        itcEvents = []
        exceptions = {}
        totalCalendarItem = len(cal.subcomponents)
        treatedCalendarItems = 0
        widgets = ['Scanning ical File: ', SimpleProgress(), ' ', Bar('>')]

        pbar = ProgressBar(widgets=widgets, max_value=totalCalendarItem).start()
        for event in cal.walk('vevent'):
            evts = []
            excep = {}
            try:
                treatedCalendarItems += 1
                pbar.update(treatedCalendarItems)
                evts, excep = self.__parseEvent(event)
            except Exception as e:
                self.__log.error(e)
                self.__log.debug('Found non parseable Event %i', treatedCalendarItems)
            itcEvents.extend(evts)
            for k,v in excep.items():
                if k in exceptions:
                    exceptions[k].extend(v)
                else:
                    exceptions[k] = v

        pbar.finish()

        event_list = self.filterRecurrenceEvents(itcEvents, exceptions)
        return event_list

        #pprint(itcEvents)

    def __parseEvent(self, event):
        """
        Parses the information contained in an event.

        :param event: the event to parse
        :return: a CalendarEvent representing the event.
        """
        foundEvents = []
        foundExceptions = {}
        hasItcInformation = False

        start = event['DTSTART'].dt
        # Ignore Fullday events
        fulldayevent = not isinstance(start, datetime.datetime)
        if fulldayevent:
            return foundEvents
        origtzinfo = start.tzinfo
        # start = start.astimezone(pytz.utc)
        end = event['DTEND'].dt

        calEvent = CalendarEvent()
        calEvent.startdatetime = start
        calEvent.enddatetime = end
        if 'SUMMARY' in event:
            calEvent.comment = event['SUMMARY']

        calEvent.UUID = event['UID']

        # Parse recurring events
        # There is some explanation on https://nylas.com/blog/rrules/
        # explaining recurring events (cancelled ocurrences, modified ocurrences)
        if 'RRULE' in event:
            naivestart = self.__start.astimezone(origtzinfo)
            naivestart = naivestart.replace(tzinfo=None)
            naiveend = self.__end.astimezone(origtzinfo)
            naiveend = naiveend.replace(tzinfo=None)
            rules = self.__parse_rrule(event, start)
            rEvents = rules.between(naivestart, naiveend)
            if 'DESCRIPTION' in event:
                calEvent.remarks = event['DESCRIPTION']
            for ev in rEvents:
                calEvent.startdatetime = pytz.timezone(origtzinfo.zone).localize(ev)
                calEvent.enddatetime = calEvent.startdatetime + (end - start)
                foundEvents.append(calEvent)
                calEvent = calEvent.copy()

        # Parse normal events
        else:
            # First, record if the event is an exception to a recurring event
            if 'RECURRENCE-ID' in event:
                calEvent.recurrenceId = event['RECURRENCE-ID'].dt
                if calEvent.UUID in foundEvents:
                    foundExceptions[calEvent.UUID].append(calEvent.recurrenceId)
                else:
                    ex = [calEvent.recurrenceId]
                    foundExceptions[calEvent.UUID] = ex
            if self.__start <= start <= self.__end:
                if 'DESCRIPTION' in event:
                    calEvent.remarks = event['DESCRIPTION']
                    hasItcInformation = True
                foundEvents.append(calEvent)

        return foundEvents, foundExceptions

    def filterRecurrenceEvents(self, events, exceptions):
        """
        Special care needs to be taken for recurring events.
        See also https://nylas.com/blog/rrules/ for an explanation on how modified recurring events work. In short,
        if on event in a series gets deletes RRULE already handles this, as this information is written in the EXDATE
        field. However, when one event in a series is modified then the original event does not get an EXDATE. Instead,
        the modified event gets the same UID and its RECURRENCE-ID points to the original recurring events which is
        overwritten.

        Therefore, this function first groups the events by UID and then for each group check whether some of the events
        overwrite one of the computed recurrence events. If so the computed ones are removed in favor of the exceptional
        ones.

        :param events: list of events to filter for modified recurrence
        :param exceptions Dictionary of Lists containing for each UUID a list of dates. These dates correspond to exceptions for recuuring events.
        :return: list of events where duplictes are filtered out.
        """
        cleanedEvents = []
        for ev in events:
            # we are only interested in recurring events
            if ev.recurrenceId is None and ev.UUID is not None:
                if ev.UUID in exceptions and ev.startdatetime in exceptions[ev.UUID]:
                    continue
                else:
                    cleanedEvents.append(ev)
            # all other events are fine
            else:
                cleanedEvents.append(ev)

        return cleanedEvents

    def __parse_rrule(self, event, start):
        # taken from http://codereview.stackexchange.com/questions/137985/parse-rrule-icalendar-entries
        rules_text = '\n'.join([line for line in event.content_lines() if line.startswith('RRULE')])
        rules = rrule.rruleset()
        start = start.replace(tzinfo=None)
        rule = rrule.rrulestr(rules_text, dtstart=start)
        # in some entries, tzinfo is missing so we assume UTC
        if rule._until and rule._until.tzinfo is not None:
            rule._until = rule._until.replace(tzinfo=None)
        rules.rrule(rule)

        excludedDates = event.get('exdate')
        if not isinstance(excludedDates, list):  # apparently this isn't a list when
            excludedDates = [excludedDates]  # there is only one EXDATE
        for exdate in excludedDates:
            try:
                rules.exdate(exdate.dts[0].dt.replace(tzinfo=None))
            except AttributeError:  # sometimes there is a None entry here
                pass
        return rules

