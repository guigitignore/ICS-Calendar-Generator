from textcalendar import TextCalendar
from sys import argv
from ics import DayEvent,Event

tc=TextCalendar("calendar.txt")

for event in tc.events:
    if not isinstance(event,DayEvent):
        event.append(Event.Location("V04 Paris Vézale"))

tc.export("result.ics")
