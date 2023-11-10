from __future__ import annotations

# This file contains the TextCalendar class

from datetime import datetime,timedelta
from ics import Calendar,TimeRangeEvent,DayEvent,Event
import re
from io import TextIOWrapper

class TextCalendar:

    class Day:
        DAY_REGEX=r'(?P<beginHour>\d{1,2})\s*[hH]\s*(?P<beginMinute>\d{1,2})\s*-\s*(?P<endHour>\d{1,2})\s*[hH]\s*(?P<endMinute>\d{1,2})\s*:\s*(?P<name>[^\(]+)\s*\((?P<organizer>[^\)]+)\)+'

        def parseTime(date:datetime,hour:str,minute:str)->datetime:
            dt=datetime.strptime(f"{hour}:{minute}","%H:%M")
            return date+timedelta(hours=dt.hour,minutes=dt.minute)
        
        def __init__(self,day:datetime,instructions:str) -> None:
            self.__events=[]
            self.__date=day

            matches = re.finditer(TextCalendar.Day.DAY_REGEX, instructions)
            matchCounter=0

            for match in matches:
                matchCounter+=1

                try:
                    eventBegin=+TextCalendar.Day.parseTime(self.__date,match.group("beginHour"),match.group("beginMinute"))
                    eventEnd=TextCalendar.Day.parseTime(self.__date,match.group("endHour"),match.group("endMinute"))
                except:
                    continue

                name = match.group('name').strip()
                organizer = match.group('organizer').strip()

                event=TimeRangeEvent(eventBegin,eventEnd)
                event.append(Event.Summary(f"{name} - {organizer}"))
                self.__events.append(event)

            if matchCounter==0:
                event=DayEvent(day)
                event.append(Event.Summary(instructions))
                self.__events.append(event)

        def eval(self,*instructions:str):
            for i in instructions:
                pass
        

        @property
        def events(self)->list[Event]:
            return self.__events
        
        @property
        def date(self)->datetime:
            return self.__date

    class Week:
        WEEK_DAYS=["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]

        def __init__(self,startDate:datetime,instructions:list[str]) -> None:
            # check date
            self.__date=startDate-timedelta(days=startDate.weekday())

            self.__days:dict[datetime,TextCalendar.Day]={}
            
            for line in instructions:
                try:
                    dayName,dayInstructions=line.split(" ",maxsplit=1)
                    dayNumber=TextCalendar.Week.WEEK_DAYS.index(dayName.upper())
                except:
                    continue

                currentDay=self.__date+timedelta(days=dayNumber)
                
                if not currentDay in self.__days:
                    self.__days[currentDay]=TextCalendar.Day(currentDay)
                
                self.__days.append(TextCalendar.Day(currentDay,dayInstructions))

        @property
        def days(self)->list[TextCalendar.Day]:
            return [self.__days[d] for d in sorted(self.__days.keys())]
        
        @property
        def events(self)->list[Event]:
            result=[]
            for day in self.days:
                result.extend(day.events)
            return result
        
        @property
        def date(self):
            return self.__date


    WEEK_REGEX=r"semaine\s+du\s+(?P<day>\d{1,2})[/-|\s+](?P<month>\d{1,2})([/-|\s+](?P<year>(?:\d{2}){1,2}))?"
    YEAR=datetime.now().year

    def __init__(self,instructions:list[str]) -> None:
        self.__weeks:dict[datetime,TextCalendar.Week]=[]
        weekInstructions=[]
        
        while instructions:
            line=instructions.pop().strip()

            if not line:
                continue
            
            match=re.match(TextCalendar.WEEK_REGEX,line,re.IGNORECASE)
            if match:
                day=match.group("day")
                month=match.group("month")
                year=match.group("year")

                if not year:
                    year=TextCalendar.YEAR
                elif len(year)==2:
                    year=str(TextCalendar.YEAR//100)+year

                try:
                    weekBegin=datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y")
                    weekInstructions.reverse()
                    self.__weeks.append(TextCalendar.Week(weekBegin,weekInstructions))
                finally:
                    weekInstructions.clear()
            else:
                weekInstructions.append(line)

        self.__weeks.reverse()


    def eval(self,*instructions):
        pass

    def parseDate(self,year:str,month:str,day:str)->datetime:
        pass

    @classmethod
    def fromBuffer(cls,file:TextIOWrapper)->TextCalendar:
        return cls(file.readlines())
    
    @classmethod
    def open(cls,filename:str)->TextCalendar:
        with open(filename,"r") as file:
            arguments=file.readlines()
        return cls(arguments)

    @property
    def weeks(self)->list[TextCalendar.Week]:
        return self.__weeks 
    
    @property
    def events(self)->list[Event]:
        result=[]
        for week in self.weeks:
            result.extend(week.events)
        return result
    
    def exportToBuffer(self,file:TextIOWrapper)->None:
        calendar=Calendar()
        calendar.extend(self.events)
        file.write(str(calendar))
    
    def export(self,filename:str)->None:
        with open(filename,"w") as f:
            self.exportToBuffer(f)

    