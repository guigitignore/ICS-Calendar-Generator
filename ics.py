from datetime import datetime

class Container(list):
    def __init__(self,name:str) -> None:
        super().__init__()
        self.__name=name.upper()

    def __str__(self) -> str:
        ret = ['BEGIN:' + self.__name]
        for line in self:
            ret.append(str(line))
        ret.append('END:' + self.__name)
        return "\r\n".join(ret)
    

class ContentLineParam:
    def __init__(self,name:str,value:str) -> None:
        self.__name=name.upper()
        self.__value=value

    def __str__(self) -> str:
        return f"{self.__name}={self.__value}"
    

class ContentLine(list):
    def __init__(self,name:str,value:str) -> None:
        super().__init__()
        self.__name=name.upper()
        self.__value=value

    def __str__(self) -> str:
        params=";".join([str(elt) for elt in self])
        if params:
            params=";"+params
        return f'{self.__name}{params}:{self.__value}'
    
class ContentLineString(ContentLine):
    def __init__(self, value: str) -> None:
        super().__init__(self.__class__.__name__.upper(), value)

class Calendar(Container):
    def __init__(self) -> None:
        super().__init__("VCALENDAR")
        self.append(ContentLine("VERSION","2.0"))
        self.append(ContentLine("PRODID","guigitignore"))

class Event(Container):
    def __init__(self) -> None:
        super().__init__("VEVENT")

    class Day(ContentLine):
        def __init__(self,date:datetime) -> None:
            super().__init__("DTSTART", date.strftime("%Y%M%d"))
            self.append(ContentLineParam("VALUE","DATE"))

    class Start(ContentLine):
        def __init__(self,start:datetime) -> None:
            super().__init__("DTSTART",start.strftime("%Y%m%dT%H%M%S"))

    class End(ContentLine):
        def __init__(self,end:datetime) -> None:
            super().__init__("DTEND",end.strftime("%Y%m%dT%H%M%S"))
    
    class Summary(ContentLineString):
        pass

    class Description(ContentLineString):
        pass

    class Location(ContentLineString):
        pass

    class Organizer(ContentLineString):
        def __init__(self, organizer: str) -> None:
            super().__init__(f"mailto:{organizer}")

    

calendar=Calendar() 
event=Event()
event.append(Event.Summary("test"))
event.append(Event.Start(datetime.utcnow()))
event.append(Event.End(datetime.now()))
calendar.append(event)

print(calendar)



    
