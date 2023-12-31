from __future__ import annotations

from datetime import datetime,timedelta
from ics import Calendar,TimeRangeEvent,TimeEvent,DayEvent,Event,ICSObject
import re
from io import TextIOWrapper

class TextCalendar2:

    WEEK_REGEX=r"semaine\s+du\s+(?P<day>\d{1,2})[/-|\s+](?P<month>\d{1,2})([/-|\s+](?P<year>(?:\d{2}){1,2}))?"

    def __init__(self) -> None:
        # store the currentdate for later use
        self.__instant=datetime.now()
        # registry to store weeks
        self.__weeks:dict[datetime,TextCalendar2Week]={}


    # eval text instructions
    def eval(self,*instructions:str):
        #instructions to pass to the week object
        instructionsStack=[]

        # browse line in reverse order to accumulate instructions and push them in week object
        for instruction in reversed(instructions):
            # strip instructions
            instruction=instruction.strip()

            if not instruction:
                continue
            # try to match regex
            match=re.match(self.__class__.WEEK_REGEX,instruction,re.IGNORECASE)

            # if match pass instructions to week
            if match:
                try:
                    weekDate=self.__parseWeekDate(match.group("year"),match.group("month"),match.group("day"))

                    #create new week only if not exist
                    if not weekDate in self.__weeks:
                        self.__weeks[weekDate]=TextCalendar2Week(weekDate)

                    #eval week instructions
                    self.__weeks[weekDate].eval(*instructionsStack)
                    
                finally:
                    instructionsStack.clear()
                
            else:
                # accumulate instructions
                instructionsStack.append(instruction)

    def evalFile(self,filename:str):
        with open(filename,"r") as file:
            # pass all lines
            self.eval(*file.readlines())

    def toICS(self)->Calendar:
        calendar=Calendar()
        calendar+=self.events
        return calendar
    
    def exportICS(self,filename:str):
        with open(filename,"w") as file:
            file.write(str(self.toICS()))

    # private method that return the nearest year from now given a date with day/month. It tries current, previous and next year.
    def __findNearestYear(self,date:datetime):
        l=[abs(self.__instant-date.replace(year=self.__instant.year+i)) for i in range(-1,2)]
        return self.__instant.year-1+l.index(min(l))

    # private method to parse date from string (this method can raise error!)
    def __parseWeekDate(self,year:str,month:str,day:str)->datetime:
        # try to parse strings
        temp=datetime.strptime(f"{day}/{month}","%d/%m")
        # if not year set year to current year
        if not year:
            date=temp.replace(year=self.__findNearestYear(temp))
        # if year is incomplete
        elif len(year)==2:
            date=temp.replace(year=(self.__instant.year//100)+int(year))
        else:
            date=temp.replace(year=int(year))
        
        # return the first day of the week
        return TextCalendar2Week.firstWeekDay(date)
    
    def __str__(self) -> str:
        return "\n".join([str(week) for week in self.weeks])

    @property
    def weeks(self)->list[TextCalendar2Week]:
        # return week object sorted by time
        return [self.__weeks[d] for d in sorted(self.__weeks.keys())]
    
    @property
    def events(self)->list[Event]:
        result=[]
        for week in self.weeks:
            result+=week.events
        return result


class TextCalendar2Week:
    DAY_NAMES=["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]

    # we init text calendar week only with a day
    def __init__(self,weekDate:datetime) -> None:
        # get the first day of the week
        self.__date:datetime=self.__class__.firstWeekDay(weekDate)
        # set to 0 unsused values
        self.__date.replace(hour=0,minute=0,second=0,microsecond=0)
        # store days in a dict
        self.__days:dict[datetime,TextCalendar2Week]={}

    def eval(self,*instructions:str):
        for instruction in instructions:
            instruction=instruction.strip()

            if not instruction:
                continue

            try:
                # try to split day name and other part
                dayName,dayInstructions=instruction.split(" ",maxsplit=1)
                # get the day number from the day name
                dayNumber=TextCalendar2Week.DAY_NAMES.index(dayName.upper())
            except:
                continue
            
            # get datetime from the day name
            currentDay=self.__date+timedelta(days=dayNumber)
            # plit day arguments
            dayInstructions=dayInstructions.split(" / ")

            if not currentDay in self.__days:
                self.__days[currentDay]=TextCalendar2Day(currentDay)

            # eval day arguments in day object
            self.__days[currentDay].eval(*dayInstructions)

    def __str__(self) -> str:
        data="\n".join([f"{self.__class__.DAY_NAMES[day.date.weekday()]:10}{day}" for day in self.days])
        return f"Semaine du {self.__date.day}/{self.__date.month}/{self.__date.year}:\n{data}\n"
    
    @property
    def days(self)->list[TextCalendar2Day]:
        #sort days
        return [self.__days[d] for d in sorted(self.__days.keys())]

    #return date
    @property
    def date(self)->datetime:
        return self.__date
    
    # return the first day of the week
    def firstWeekDay(date:datetime)->datetime:
        return date-timedelta(days=date.weekday())
    
    @property
    def events(self)->list[Event]:
        result=[]
        for day in self.days:
            result+=day.events
        return result
    

class TextCalendar2Day:
    TIME_REGEX=r"((?P<beginHour>\d{1,2})\s*[hH]\s*(?P<beginMinute>\d{1,2})\s*(-\s*(?P<endHour>\d{1,2})\s*[hH]\s*(?P<endMinute>\d{1,2})\s*)?)"
    INSTRUCTION_REGEX=r"(?P<name>[^\(\[]+)?\s*(\((?P<organizer>[^\)]+)\))?\s*(\[(?P<location>[^\]]+)\])?\s*\2?"

    def __init__(self,date:datetime) -> None:
        self.__date:datetime=date
        # reset hour , minutes...
        self.__date.replace(hour=0,minute=0,second=0,microsecond=0)
        self.__events:list[Event]=[]
        
    def eval(self,*instructions:str):
        for instruction in instructions:

            if not instruction.strip():
                continue

            event=None
            
            try:
                time,instruction=instruction.split(":",maxsplit=1)

                matchDate=re.match(self.__class__.TIME_REGEX,time.strip())

                if matchDate:
                    beginTime=self.__parseTime(matchDate.group("beginHour"),matchDate.group("beginMinute"))
                    
                    try:
                        endTime=self.__parseTime(matchDate.group("endHour"),matchDate.group("endMinute"))
                        event=TimeRangeEvent(beginTime,endTime)
                    except:
                        event=TimeEvent(beginTime)
                else:
                    raise ValueError
            except:
                event=DayEvent(self.__date)

            matchInstruction=re.match(self.__class__.INSTRUCTION_REGEX,instruction.strip())
            if matchInstruction:
                name=(matchInstruction.group('name') or '').strip()
                organizer=(matchInstruction.group('organizer') or '').strip()
                location=(matchInstruction.group('location') or '').strip()

                if location:
                    event.append(Event.Location(location))
                if organizer:
                    event.append(Event.Organizer(organizer))
                if name:
                    event.append(Event.Summary(name))

                self.__events.append(event)
            else:
                print(f"no instruction for event {self.date}")
        
                
    def __parseTime(self,hour:str,minute:str)->datetime:
        dt=datetime.strptime(f"{hour}:{minute}","%H:%M")
        return self.__date+timedelta(hours=dt.hour,minutes=dt.minute)


    def __str__(self) -> str:
        result=[]

        for event in self.events:
            eventString=""

            if "SUMMARY" in event:
                eventString+=event["SUMMARY"].value+" "
            if "ORGANIZER" in event:
                eventString+=f"({event['ORGANIZER']['CN'].value}) "
            if "LOCATION" in event:
                eventString+=f"[{event['LOCATION']}] "

            result.append(eventString)
        
        return " / ".join(result)


    @property
    def date(self)->datetime:
        return self.__date
    
    @property
    def events(self)->list[Event]:
        return self.__events