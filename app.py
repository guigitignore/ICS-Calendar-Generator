#!python3

from textcalendar2 import TextCalendar2
from argparse import ArgumentParser,FileType
from ics import DayEvent,Event

parser=ArgumentParser("generator",description="ICalendar generator from text files")
parser.add_argument("-l","--location",type=str,help="Add a location for non day events")
parser.add_argument("-i","--input",type=FileType("r"),nargs="+",help="input files",required=True,action="extend")
parser.add_argument("-o","--output",type=FileType("w"),help="output files",required=True)

args=parser.parse_args()

calendar=TextCalendar2()

for f in args.input:
    calendar.eval(*f.readlines())
    f.close()

if args.location:
    for event in calendar.events:
        if not isinstance(event,DayEvent):
            event.append(Event.Location(args.location))


args.output.write(str(calendar.toICS()))
args.output.close()
