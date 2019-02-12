# -*- coding: utf-8 -*-
import json
import logging
import sys
import re
from tzlocal import get_localzone
if float(sys.version[:3])<3.0:
    import ConfigParser
    from StringIO import StringIO
else:
    import configparser as ConfigParser
    from io import StringIO


class CalendarEvent(object):
    """This class holds the structure of an ical event"""

    def __init__(self):
        """Constructor"""
        self.__log = logging.getLogger('Tube4Droid')
        self.comment=None
        self.startdatetime=None
        self.enddatetime=None
        self.remarks = ''
        self.UUID = ''
        self.recurrenceId = None

    def toString(self):
        return  '"startTime" : "{}", "duration" : {}, "note" : "{}", "remarks" : "{}"'.format(self.getStartDateTimeString(), self.duration(), self.comment, self.remarks)

    def to_Dict(self):
        elementsDic = dict(zip(('startTime', 'duration',  'note', 'remarks'),
                 (self.getStartDateTimeString(), self.duration(), self.comment, self.remarks)))

        return self.cleandict(elementsDic)

    def to_JSON(self):
        return json.dumps(self.to_Dict())

    def cleandict(self,d):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.
        http://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization

        :return: cleaned up dictionary
        """
        if not isinstance(d, dict):
            return d
        cleaneddict = dict((k, self.cleandict(v)) for k, v in d.items() if v is not None)
        if 'ticketId' not in cleaneddict:
            cleaneddict.pop('ticketEnvKey', None)
        return cleaneddict

    def copy(self):
        """
        Creates a copy of this object.

        :return: a copy of this object
        """
        calEvent = CalendarEvent()

        calEvent.comment = self.comment
        calEvent.startdatetime = self.startdatetime
        calEvent.enddatetime = self.enddatetime
        calEvent.remarks = self.remarks
        calEvent.UUID = self.UUID
        calEvent.recurrenceId = self.recurrenceId
        return calEvent

    def duration(self):
        """Computes the duration in minutes of an event.

        :return: event duration
        """
        deltatime = self.enddatetime - self.startdatetime
        #minutesSecondsDiv = divmod(deltatime.days * 86400 + deltatime.seconds, 60)
        deltaMinutes = deltatime.days * 86400 + deltatime.seconds/60
        return float('{0:.2f}'.format(deltaMinutes))

    def getStartDateTimeString(self):
        """
        Format the start time in %d-%m-%Y %H:%M:%S.

        :return: formatted string of the start datetime
        """
        return self.getFormattedDateString(self.startdatetime, '%d-%m-%Y %H:%M:%S')

    def getStartTimeString(self):
        """
        Format the start datetime in %H:%M:%S

        :return: formatted string of the start time
        """
        return self.getFormattedDateString(self.startdatetime, '%H:%M')

    def getEndTimeString(self):
        """
        Format the end datetime in %H:%M:%S

        :return: formatted string of the end time
        """
        return self.getFormattedDateString(self.enddatetime, '%H:%M')

    def getFormattedDateString(self, datetime, format):
        """
        Format the given datetime in the given format

        :return: formatted string of the  datetime
        """
        localTZ = get_localzone()
        startdate = datetime.astimezone(localTZ)
        return startdate.strftime(format)