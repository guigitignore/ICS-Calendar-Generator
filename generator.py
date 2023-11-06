#!python3

from sys import argv
from  datetime import datetime,timedelta
from ics import Calendar,Event
from ics.utils import ContentLine,Container
import arrow
import re

def serialize_event_time(t:datetime):
    return arrow.get(t).format('YYYYMMDDTHHmmss')

class MyICSEventSerializer(Event.Meta.serializer):
    
    def serialize_start(event:Event, container:Container):
        if event.begin and not event.all_day:
            container.append(ContentLine("DTSTART", value=serialize_event_time(event.begin)))

    def serialize_end(event, container):
        if event.begin and event._end_time and not event.all_day:
            container.append(ContentLine("DTEND", value=serialize_event_time(event.end)))


class MyICSEvent(Event):
    
    class Meta:
        name = Event.Meta.name
        parser = Event.Meta.parser
        serializer = MyICSEventSerializer

    
    

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

def generate(filename:str):
    try:
        content=open(filename,"r").read()
    except:
        print("Cannot open input file")
        return
    
    year=datetime.now().year

    week_pattern= r"(?i)\bsemaine\b\s+du\s+(?P<begin>\d{2}/\d{2})\s+au\s+(?P<end>\d{2}/\d{2})"
    day_pattern = r'(?P<beginHour>\d{1,2})\s*[hH]\s*(?P<beginMinute>\d{1,2})\s*-\s*(?P<endHour>\d{1,2})\s*[hH]\s*(?P<endMinute>\d{1,2})\s*:\s*(?P<name>[^\(]+)\s*\((?P<information>[^\)]+)\)+'

    week_day_names=["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI"]
    week_begin:datetime=None
    
    lines=[line.strip() for line in content.split("\n")]

    calendar=Calendar()

    for line in lines:
        week_matches = re.search(week_pattern, line)
        if week_matches:
            string_date=f"{week_matches.group('begin')}/{year}"
            try:
                week_begin=datetime.strptime(string_date, "%d/%m/%Y")
            except:
                #cannot parse the week
                continue

        elif week_begin!=None and len(line):
            dayName,instructions=line.split(maxsplit=1)
            try:
                offset=week_day_names.index(dayName.upper())
            except:
                continue

            currentDay=week_begin+timedelta(days=offset)
            
            matches = re.finditer(day_pattern, instructions)
            matchCounter=0

            for match in matches:
                matchCounter+=1

                try:
                    beginHour = validateHour(match.group('beginHour'))
                    beginMinute = validateMinute(match.group('beginMinute'))

                    endHour = validateHour(match.group('endHour'))
                    endMinute = validateMinute(match.group('endMinute'))
                except:
                    continue

                name = match.group('name').strip()
                information = match.group('information').strip()

                eventBegin=currentDay+timedelta(hours=beginHour,minutes=beginMinute)
                eventEnd=currentDay+timedelta(hours=endHour,minutes=endMinute)
                #print(currentDay,eventBegin)

                event=Event()
            
                event.begin=eventBegin
                event.end=eventEnd
                event.name=name
                event.organizer=information
                
                calendar.events.add(event)
            
            if matchCounter==0:
                event=Event()
                event.begin=currentDay
                event.make_all_day()  
                event.name=instructions
                calendar.events.add(event)
    
    
    
    with open(f'{filename}.ics', 'w') as f:
        f.writelines(calendar)

    


if __name__=="__main__":
    for arg in argv:
        generate(arg)