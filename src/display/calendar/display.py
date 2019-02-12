#!/usr/bin/python
# -*- coding:utf-8 -*-
from display.utils import utilities

try:
    import lib.epd7in5b as epd7in5b
    localMode = False
except:
    localMode = True
from PIL import Image,ImageDraw,ImageFont
import logging
import traceback
import calendar
import time
from datetime import datetime, date, timedelta
import requests
import display.utils.utilities


class Display(object):
    """This class is responsible for drawing stuf to the display"""

    def __init__(self, doClear, events, localizedStartofDay, localizedEndofDay):
        """Constructor"""
        self.__font = ImageFont.truetype('src/fonts/FreeMonoBold.ttf', 20)
        self.__font_cal = ImageFont.truetype('src/fonts/FreeMonoBold.ttf', 16)
        self.__font_day = ImageFont.truetype('src/fonts/Roboto-Black.ttf', 110)
        self.__font_day_str = ImageFont.truetype('src/fonts/Roboto-Light.ttf', 35)
        self.__font_month_str = ImageFont.truetype('src/fonts/Roboto-Light.ttf', 25)
        self.__font_weather_icons = ImageFont.truetype('src/fonts/weathericons-regular-webfont.ttf', 35)
        self.__font_weather_degree = ImageFont.truetype('src/fonts/Roboto-Light.ttf', 25)
        self.__font_tasks_list_title = ImageFont.truetype('src/fonts/Roboto-Light.ttf',30)
        self.__font_tasks_list = ImageFont.truetype('src/fonts/tahoma.ttf',12)
        self.__font_tasks_due_date = ImageFont.truetype('src/fonts/tahoma.ttf',9)
        self.__salahFont = ImageFont.truetype('src/fonts/arial.ttf', 13)
        self.__icons_list={u'chancerain':u'',u'chancesleet':u'','chancesnow':u'','chancetstorms':u'','clear':u'','flurries':u'','fog':u'','hazy':u'','mostlycloudy':u'','mostlysunny':u'','partlycloudy':u'','partlysunny':u'','sleet':u'','rain':u'','sunny':u'','tstorms':u'','cloudy':u''}
            
        self.__log = logging.getLogger('Tube4Droid')
        self.events = events
        self.localizedStartofDay = localizedStartofDay
        self.localizedEndofDay = localizedEndofDay
        self.epd = None
        self.__doClear = doClear

        self.contract=None
        self.ticket=None
        self.comment=None
        self.startdatetime=None
        self.enddatetime=None
        self.jira = 'false'
        self.zimbra = 'false'
        self.user = ''
        self.remarks = ''
        self.jiraname = 'ADNOVUM'
        self.UUID = ''
        self.recurrenceId = None

    def doDraw2(self):
        draw, drawRed = self.__setup()
        self.__fillLeftSide(draw, drawRed)
        try:
            draw.rectangle((245, 5, 635, 55), fill=0)
            draw.text((250, 10), "Dr. Andreas Ruppen ", font=self.__font_tasks_list_title, fill=255)

            for i in range(10):
                self.__log.info(i)
                linepos = 70+(i+1)*30
                drawRed.line((500, linepos, 630, linepos), fill=0)
                drawRed.rectangle((595, linepos, 630, linepos+10), fill = 0)
                displayTime = self.localizedStartofDay+ timedelta(hours=1*i)
                drawRed.text((600, linepos+0.5), datetime.strftime(displayTime, '%H:%M'), font=self.__font_tasks_due_date, fill=255)
            
            LINEHEIGHT = 20
            counter = 0
            for calEvent in self.events:
                name = calEvent.comment
                deltaToStart = calEvent.startdatetime-self.localizedStartofDay
                #deltaToStarInMinutes = deltaToStart.seconds/60
                deltaToStarInMinutes = utilities.td2seconds(deltaToStart) / 60
                pixelsStart = 0.5*deltaToStarInMinutes
                deltaToEnd = calEvent.enddatetime-self.localizedStartofDay
                #deltaToEndInMinutes = deltaToEnd.seconds/60
                deltaToEndInMinutes = utilities.td2seconds(deltaToEnd) / 60
                pixelsEnd = 0.5*deltaToEndInMinutes
                if(len(name)>55):
                    name = name[0:55]+'...'

                #draw.line((250,pixelsStart,630,pixelsStart),fill=0)
                #draw.line((250,pixelsEnd,630,pixelsEnd),fill=0)
                drawRed.rectangle((255, 70+pixelsStart, 595, 70+pixelsEnd), outline=0)
                draw.rectangle((255, 70+pixelsStart, 595, 70+pixelsEnd), fill=0)
                draw.text((270, 70+pixelsStart+1), name, font=self.__font_tasks_list, fill=255)
                self.__log.info(calEvent.startdatetime)
                LINEHEIGHT += 26
                counter += 1
        except:
            print('traceback.format_exc():\n%s', traceback.format_exc())
            exit()
        self.__tearDown()

    def __fillLeftSide(self, draw, drawRed):
        #Calendar Strings
        temp = requests.get("http://192.168.15.9/report").json()
        cal_day_str = time.strftime("%A")
        cal_day_number = time.strftime("%d")
        cal_month_str = time.strftime("%B")+' '+ time.strftime("%Y")
        cal_year_str = time.strftime('%Y')

        cal_month_cal = str(calendar.month(int(cal_year_str), int(cal_day_number))).replace(time.strftime("%B")+' ' +time.strftime("%Y"), ' ')
        print(cal_month_cal)

        cal_width = 240

        #this section is to center the calendar text in the middle

        #the Day string "Monday" for Example
        w_day_str,h_day_str=self.__font_day_str.getsize(cal_day_str)
        x_day_str=(cal_width/2)-(w_day_str/2)
        #y_day_str=(epd2in9.EPD_HEIGHT/2)-(h/2)

        #the settings for the Calenday today number
        w_day_num,h_day_num=self.__font_day.getsize(cal_day_number)
        x_day_num=(cal_width/2)-(w_day_num/2)

        #the settings for the Calenday Month String
        w_month_str,h_month_str=self.__font_month_str.getsize(cal_month_str)
        x_month_str=(cal_width/2)-(w_month_str/2)

        drawRed.rectangle((0, 0, 240, 640), fill=0)
        drawRed.text((15, 190), cal_month_cal, font=self.__font_cal, fill=255)
        drawRed.text((x_day_str, 25), cal_day_str, font=self.__font_day_str, fill=255)
        drawRed.text((x_day_num, 50), cal_day_number, font=self.__font_day, fill=255)
        drawRed.text((x_month_str, 165), cal_month_str, font=self.__font_month_str, fill=255)

        drawRed.text((145, 340),'Stetten', font=self.__salahFont, fill='red')
        drawRed.text((80, 340), str(round(temp['temperature'] ,0)) + u'°', font=self.__font_weather_degree, fill=255)
        drawRed.text((145, 355), 'sun', font=self.__salahFont, fill=255)
        drawRed.text((30, 330), self.__icons_list['chancesnow'], font=self.__font_weather_icons ,fill=255)

        draw.line((5, 320, 225, 320), fill=255) #weather line

    def __setup(self):
        try:
            if not localMode:
                self.epd = epd7in5b.EPD()
                self.epd.init()
                print("Clear")
                self.epd.Clear(0xFF)
            
            if localMode:
                widht, height = (640, 384)
            else:
                widht, height = (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT)

            print("Drawing")
            self.__bwImage = Image.new('1', (widht, height), 255)  # 255: clear the frame      
            self.__redImage = Image.new('1', (widht, height), 255)  # 255: clear the frame      
            draw = ImageDraw.Draw(self.__bwImage)
            drawRed = ImageDraw.Draw(self.__redImage)
            return draw, drawRed
        except:
            print('traceback.format_exc():\n%s', traceback.format_exc())
            exit()

    def __tearDown(self):
        try:
            if localMode:
                self.__bwImage.show()
                self.__redImage.show()
            else:
                print("Printing Display")
                self.epd.display(self.epd.getbuffer(self.__bwImage), self.epd.getbuffer(self.__redImage))
                #epd.display(epd.getbuffer(Himage))
                print("Going to sleep")
                self.epd.sleep()
        except:
            print('traceback.format_exc():\n%s', traceback.format_exc())
            exit()