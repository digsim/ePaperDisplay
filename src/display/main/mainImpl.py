# -*- coding: utf-8 -*-
import argparse
import getpass
import logging
import pytz
import sys
from display.calendar.display import Display
from datetime import datetime, date, timedelta
from colorama import Fore, Back, Style
from .main import Main
from display.calendar.calendar2events import Calendar2Events
from display.utils import utilities
if sys.version_info[0:2] <= (2, 6):
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class MainImpl(Main):

    def __init__(self):
        """Constructor"""
        self.__configDirName = "epaper_display"
        self.__configName = 'epaper.conf'
        self.__logFileName = 'epaper.log'

        super(MainImpl, self).__init__(self.__configDirName, self.__configName, self.__logFileName)
        self.__log = logging.getLogger('Tube4Droid')

        self.__itcurl = self.config.get('ITC', 'url')
        self.__itcuser = self.config.get('ITC', 'user')
        self.__itcpass = None
        self.__useBulk = False
        self.__verifySSL = True
        self.__version = 1
        self.__command = ''
        if self.config.has_option('Config', 'usebulk'):
            self.__useBulk = self.config.getboolean('Config', 'usebulk')
        if self.config.has_option('Config', 'verifyssl'):
            self.__verifySSL = self.config.getboolean('Config', 'verifyssl')
        if self.config.has_option('Config', 'version'):
            self.__version = self.config.getint('Config', 'version')

        self.__tz = pytz.timezone('Europe/Berlin')
        today = datetime.now(self.__tz).date()
        self.startdate = self.__tz.localize(datetime.combine(today, datetime.min.time()))
        self.startdate = self.startdate.astimezone(pytz.utc)
        self.enddate = self.__tz.localize(datetime.combine(today, datetime.max.time()))
        self.enddate = self.enddate.astimezone(pytz.utc)

        self.dryrun = False
        self.clearDisplay = True

    def getArguments(self, argv):
        """
        Parses the command line arguments.

        :param argv: array of command line arguments
        :return: void
        """
        
        self._checkPythonVersion()
        defaultstart = self.startdate.astimezone(self.__tz)
        defaultend = self.enddate.astimezone(self.__tz)
        defaultstart = defaultstart.strftime('%Y/%m/%d - %H:%M:%S')
        defaultend = defaultend.strftime('%Y/%m/%d - %H:%M:%S')
        parser = argparse.ArgumentParser(prog='displayCalendar',
                                         description='Downloads calendar ics files and Displays the entries of the specified date on an e-Paper display',
                                         epilog='%(prog)s {command} -h for help on individual commands')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s '+self.version)

        subparsers = parser.add_subparsers(help='commands', dest='command')
        display_parser = subparsers.add_parser('display', help='creates the display')



        display_parser.add_argument('-s', '--start-date',
                                 help='start date (inclusive) from which on ITC entries should be written (YYYYMMDD). Defaut is '+defaultstart,
                                 required=False, dest='startdate')     
        display_parser.add_argument('-e', '--end-date',
                                 help='end date (inclusive) to which on ITC entries should be written (YYYYMMDD) Defaut is ' + defaultend,
                                 required=False, dest='enddate')
        clear_parser = display_parser.add_mutually_exclusive_group(required=False)
        clear_parser.add_argument('--clear', dest='clearDisplay', action='store_true',
                                 help='if set, the display will be cleared. Mutually exclusive with --no-clear option.',
                                 default=self.__useBulk)
        clear_parser.add_argument('--no-clear', dest='clearDisplay', action='store_false',
                                 help='if set, the display will not be cleared.. Mutually exclusive with --clear option.')

        
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        args = parser.parse_args(argv)

        if args.command is not None:
            self.__command = args.command

        if args.startdate is not None:
            unlocalized = datetime.strptime(args.startdate, '%Y%m%d')
            localized = self.__tz.localize(datetime.combine(unlocalized, datetime.min.time()))
            self.startdate = localized.astimezone(pytz.utc)
        if args.enddate is not None:
            unlocalized = datetime.strptime(args.enddate, '%Y%m%d')
            localized = self.__tz.localize(datetime.combine(unlocalized, datetime.max.time()))
            self.enddate = localized.astimezone(pytz.utc)
        if self.__command == 'sync':
            if args.dryrun is not None:
                self.dryrun = args.dryrun
            if args.bulk is not None:
                self.__useBulk = args.bulk
            self.main()
        elif self.__command == 'stats':
            self.main()
        elif self.__command == 'display':
            self.main()
        else:
            parser.print_help()
            sys.exit(1)
        sys.exit(0)

    def doWork(self):
        """
        Overwrites the main

        :return: void
        """
        if self.__command == 'display':
            self.__doDisplayCommand()

    def __doDisplayCommand(self):
        self.__log.info('Printing stats')
        events = self.__getITCEvents()

        unlocalizedStartofDay = datetime.strptime('20190212 08:00', '%Y%m%d %H:%M')
        localizedStartofDay = self.__tz.localize(unlocalizedStartofDay)
        unlocalizedEndofDay = datetime.strptime('20190212 18:00', '%Y%m%d %H:%M')
        localizedEndofDay = self.__tz.localize(unlocalizedEndofDay)
        display = Display(self.clearDisplay, events, localizedStartofDay, localizedEndofDay)
        display.doDraw2()

    def __getITCEvents(self):
        """
        Parses all defined calendars and returns a list of events having ITC information.

        :return: a list of calendarEvent
        """
        calendarEvents = []
        calendars = self.config.get('Config', 'calendars')
        for cal in calendars.split(','):
            self.__log.debug('Parsing Calendar {0}'.format(cal))
            calendarurl = self.config.get(cal, 'url')
            calendarpass, calendaruser = self.__parseCalendarCredentials(cal)
            configjiraname = 'ADNOVUM'
            if self.config.has_option(cal, 'jiraname'):
                configjiraname = self.config.get(cal, 'jiraname')
            c = Calendar2Events(calendarurl, calendaruser, calendarpass, self.startdate, self.enddate,
                                self.__verifySSL)

            events = c.fetchCalendarEvents()
            events.sort(key=lambda k: k.startdatetime)
            #self.__logEvents(events)
            calendarEvents.extend(events)
        calendarEvents.sort(key=lambda k: k.startdatetime)
        return calendarEvents

    def __parseCalendarCredentials(self, cal):
        """
        Tries to load credentials for the given calendar form the properties file. If there is no password given
        Then we ask interactively for a password.

        :param cal: calendar to download
        :return: user and password to download the calendar
        """
        calendaruser = ''
        calendarpass = ''
        if self.config.has_option(cal, 'user'):
            calendaruser = self.config.get(cal, 'user')
            if self.config.has_option(cal, 'pass'):
                calendarpass = self.config.get(cal, 'pass')
            else:
                calendarpass = getpass.getpass('Password for calendar (' + cal + '):')
                # if the user just hits enter, take the calendar password
                if calendarpass == '':
                    calendarpass = self.__itcpass
        return calendarpass, calendaruser

    def __logEvents(self, events):
        """
        Pretty print to log. This is logged with an info level and should be shown to the user.

        :param events: the events to log
        :return: void
        """
        currentDay = date.min
        #self.__log.info('Printing Events for: {0}'.format(currentDay.strftime('%d-%m-%Y')))
        for calEvent in events:
            if calEvent.startdatetime.date() != currentDay:
                currentDay = calEvent.startdatetime.date()
                self.__log.info(Fore.RED+'Printing Events for: ####### {0} #######'.format(currentDay.strftime('%d-%m-%Y'))+Style.RESET_ALL)
            self.__log.info(
                'Writing: ' + calEvent.comment + ' (' + calEvent.getStartTimeString() + ' - ' + calEvent.getEndTimeString() + ')')
            self.__log.debug(calEvent.to_JSON())

if __name__ == "__main__":
    main = MainImpl()
    main.getArguments(sys.argv[1:])
