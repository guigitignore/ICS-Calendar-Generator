from textcalendar import TextCalendar
from sys import argv
from ics import Event

tc=TextCalendar("calendar.txt")

for event in tc.events:
    if not event.contains(Event.Day):
        event.append(Event.Location("V04 Paris Vézale"))

tc.export("result.ics")
