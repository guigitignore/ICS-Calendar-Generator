#!python3

from textcalendar import TextCalendar
from argparse import ArgumentParser,FileType
from ics import DayEvent,Event

parser=ArgumentParser("generator",description="ICalendar generator from text files")
parser.add_argument("-l","--location",type=str,help="Add a location for non day events")
parser.add_argument("-i","--input",type=FileType("r"),nargs="+",help="input files",required=True,action="extend")
parser.add_argument("-o","--output",type=FileType("w"),nargs="+",help="output files",required=True,action="extend")

args=parser.parse_args()

if len(args.input)==len(args.output):
    calendars=[TextCalendar.fromBuffer(buffer) for buffer in args.input]

    for (buffer,calendar) in zip(args.output,calendars):
        # add location
        if args.location:
            for event in calendar.events:
                if not isinstance(event,DayEvent):
                    event.append(Event.Location(args.location))
        
        calendar.exportToBuffer(buffer)

else:
    print("Need to have 1 input file for 1 output file")

# Don't forget to close files opened by argparse
for file in args.input:
    file.close()

for file in args.output:
    file.close()
