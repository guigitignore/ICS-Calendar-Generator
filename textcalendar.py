from io import TextIOWrapper,StringIO
from datetime import datetime
from ics import Calendar,Event

class CalendarParser:
    def __init__(self,filename:str) -> None:
        self.__filename=str
        self.__weeks:list[CalendarWeek]=[]

        with open(filename,"r") as file:
            pass

    @property
    def filename(self):
        return self.__filename
    
    @property
    def weeks(self):
        return self.__weeks
   

class CalendarWeek:
    def __init__(self,startdate:datetime,instructions:StringIO) -> None:
        self.__days:list[CalendarDay]=[]



    @property
    def days(self):
        return self.__days


class CalendarDay:
    def __init__(self,day:datetime,instructions:str) -> None:
        pass
    


CalendarParser("calendar.txt")