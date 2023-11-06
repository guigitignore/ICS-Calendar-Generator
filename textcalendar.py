from io import TextIOWrapper

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
    def __init__(self,calendarParser:CalendarParser,file:TextIOWrapper) -> None:
        pass


class CalendarDay:
    pass


CalendarParser("calendar.txt")