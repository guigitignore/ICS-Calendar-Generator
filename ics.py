from datetime import datetime

class Container(list):
    def __init__(self,name:str) -> None:
        super().__init__()
        self.__name=name

    def __str__(self) -> str:
        ret = ['BEGIN:' + self.__name]
        for line in self:
            ret.append(str(line))
        ret.append('END:' + self.__name)
        return "\r\n".join(ret)
    
class ContentLineParam:
    def __init__(self,name:str,value:str) -> None:
        self.__name=name
        self.__value=value

    def __str__(self) -> str:
        return f"{self.__name}={self.__value}"
    
class ContentLineFlag(str):
    def __new__(cls,flag:str) -> None:
        return str.__new__(cls,flag)

class ContentLine(list):
    def __init__(self,name:str,value:str) -> None:
        super().__init__()
        self.__name=name
        self.__value=value

    def __str__(self) -> str:
        params=";".join([str(elt) for elt in self])
        if params:
            params=";"+params
        return f'{self.__name}{params}:{self.__value}'

class Calendar(Container):
    def __init__(self) -> None:
        super().__init__("VCALENDAR")
        self.append(ContentLine("VERSION","2.0"))
        self.append(ContentLine("PRODID","guigitignore"))

class Event(Container):
    def __init__(self) -> None:
        super().__init__("VEVENT")
        self.__summary:str=None
        self.__organizer:str=None
        self.__description:str=None

    @property
    def summary(self)->str:
        return self.__summary
    
    @summary.setter
    def summary(self,value:str):
        self.__summary=value

    @property
    def organizer(self)->str:
        return self.__organizer
    
    @organizer.setter
    def organizer(self,value:str):
        self.__organizer=value

    @property
    def description(self)->str:
        return self.__description

    @description.setter
    def description(self,value:str):
        self.__description=value

    def __str__(self) -> str:
        if self.summary:
            self.append(ContentLine("SUMMARY",self.summary))
        if self.organizer:
            organizer=ContentLine("ORGANIZER",self.organizer)
            organizer.append(ContentLineParam("CN",self.organizer))
            organizer.append(ContentLineFlag("mailto"))
            self.append(organizer)
        if self.description:
            self.append(ContentLine("DESCRIPTION",self.description))
        return super().__str__()
    
class EntireDayEvent(Event):
    def __init__(self) -> None:
        super().__init__()
        self.__day:datetime=None

    @property
    def day(self)->datetime:
        return self.__day
    
    @day.setter
    def day(self,value:datetime):
        self.__day=value

    def __str__(self) -> str:
        if self.day:
            day=ContentLine("DTSTART",self.day.strftime("%Y%M%d"))
            day.append(ContentLineParam("VALUE","DATE"))
            self.append(day)
        return super().__str__()
    
class TimeRangeEvent(Event):
    def __init__(self) -> None:
        super().__init__()
        self.__begin:datetime=None
        self.__end:datetime=None

    @property
    def begin(self):
        return self.__begin
    
    @begin.setter
    def begin(self,value:datetime):
        self.__begin=value

    @property
    def end(self):
        return self.__end
    
    @end.setter
    def end(self,value:datetime):
        self.__end=value

    def __str__(self) -> str:
        if self.begin:
            self.append(ContentLine("DTSTART",self.begin.strftime("%Y%m%dT%H%M%S")))
        if self.end:
            self.append(ContentLine("DTEND",self.end.strftime("%Y%m%dT%H%M%S")))
        return super().__str__()


calendar=Calendar() 
event=TimeRangeEvent()
event.summary="test"
event.description="me"
event.begin=datetime.utcnow()
event.end=datetime.now()
calendar.append(event)

print(calendar)



    
