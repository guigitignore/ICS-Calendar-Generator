from __future__ import annotations
from datetime import datetime,timedelta
from ics import Calendar,Event
import re

class TextCalendar:

    class Day:
        DAY_REGEX=r'(?P<beginHour>\d{1,2})\s*[hH]\s*(?P<beginMinute>\d{1,2})\s*-\s*(?P<endHour>\d{1,2})\s*[hH]\s*(?P<endMinute>\d{1,2})\s*:\s*(?P<name>[^\(]+)\s*\((?P<information>[^\)]+)\)+'

        def validateHour(hour:str)->int:
            result=int(hour)
            if result<0 or result>23:
                raise ValueError
            return result

        def validateMinute(minute:str)->int:
            result=int(minute)
            if result<0 or result>59:
                raise ValueError
            return result
        
        def __init__(self,day:datetime,instructions:str) -> None:
            self.__events=[]

            matches = re.finditer(TextCalendar.Day.DAY_REGEX, instructions)
            matchCounter=0

            for match in matches:
                matchCounter+=1

                try:
                    beginHour = TextCalendar.Day.validateHour(match.group('beginHour'))
                    beginMinute = TextCalendar.Day.validateMinute(match.group('beginMinute'))

                    endHour = TextCalendar.Day.validateHour(match.group('endHour'))
                    endMinute = TextCalendar.Day.validateMinute(match.group('endMinute'))
                except:
                    continue

                name = match.group('name').strip()
                information = match.group('information').strip()

                eventBegin=day+timedelta(hours=beginHour,minutes=beginMinute)
                eventEnd=day+timedelta(hours=endHour,minutes=endMinute)

                event=Event()
                event.append(Event.Start(eventBegin))
                event.append(Event.End(eventEnd))
                event.append(Event.Summary(name))
                event.append(Event.Description(information))
                self.__events.append(event)

            if matchCounter==0:
                event=Event()
                event.append(Event.Summary(instructions))
                event.append(Event.Day(day))
                self.__events.append(event)
        

        @property
        def events(self)->list[Event]:
            return self.__events

    class Week:
        WEEK_DAYS=["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI"]

        def __init__(self,startDate:datetime,instructions:list[str]) -> None:
            self.__days:list[TextCalendar.Day]=[]
            
            for line in instructions:
                try:
                    dayName,dayInstructions=line.split(" ",maxsplit=1)
                    dayNumber=TextCalendar.Week.WEEK_DAYS.index(dayName.upper())
                except:
                    continue

                currentDay=startDate+timedelta(days=dayNumber)
                self.__days.append(TextCalendar.Day(currentDay,dayInstructions.strip()))

        @property
        def days(self)->list[TextCalendar.Day]:
            return self.__days
        
        @property
        def events(self)->list[Event]:
            result=[]
            for day in self.days:
                result.extend(day.events)
            return result


    WEEK_REGEX=r"(?i)\bsemaine\b\s+du\s+(?P<begin>\d{2}/\d{2})"
    YEAR=datetime.now().year

    def __init__(self,filename:str) -> None:
        self.__filename=str
        self.__weeks:list[TextCalendar.Week]=[]

        with open(filename,"r") as file:
            lines=file.readlines()

        weekInstructions=[]
        
        while lines:
            line=lines.pop().strip()

            if not line:
                continue
            
            match=re.match(TextCalendar.WEEK_REGEX,line,re.IGNORECASE)
            if match:
                string_date=f"{match.group('begin')}/{TextCalendar.YEAR}"
                try:
                    weekBegin=datetime.strptime(string_date, "%d/%m/%Y")
                    weekInstructions.reverse()
                    self.__weeks.append(TextCalendar.Week(weekBegin,weekInstructions))
                finally:
                    weekInstructions.clear()
            else:
                weekInstructions.append(line)

        self.__weeks.reverse()

    @property
    def weeks(self)->list[TextCalendar.Week]:
        return self.__weeks 

    @property
    def filename(self)->str:
        return self.__filename
    
    @property
    def events(self)->list[Event]:
        result=[]
        for week in self.weeks:
            result.extend(week.events)
        return result
    
    def export(self,filename:str)->None:
        calendar=Calendar()
        calendar.extend(self.events)

        with open(filename,"w") as f:
            f.write(str(calendar))
    