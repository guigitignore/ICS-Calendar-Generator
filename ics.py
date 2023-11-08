from datetime import datetime

class Singleton:
    _instance=None

    def __new__(cls,*args,**kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls,*args,**kwargs)
        return cls._instance

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
    
    def contains(self,klass):
        return any(isinstance(elt, klass) for elt in self)
    
    def __repr__(self) -> str:
        return f"<ICS:Container:{self.__class__.__name__}>"
    
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
    
    def __repr__(self) -> str:
        return f"<ICS:ContentLine:{self.__class__.__name__}>"
    
class ContentLineTime(ContentLine):
    class TZID(ContentLineParam,Singleton):
        def __init__(self) -> None:
            ContentLineParam.__init__(self,"TZID", datetime.now().astimezone().strftime("%Z"))

    def __init__(self,name:str,instant:datetime) -> None:
        super().__init__(name,instant.strftime("%Y%m%dT%H%M%S"))
        self.append(ContentLineTime.TZID())
    
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

    class Start(ContentLineTime):
        def __init__(self,start:datetime) -> None:
            super().__init__("DTSTART",start)

    class End(ContentLineTime):
        def __init__(self,end:datetime) -> None:
            super().__init__("DTEND",end)
    
    class Summary(ContentLineString):
        pass

    class Description(ContentLineString):
        pass

    class Location(ContentLineString):
        pass

    class Organizer(ContentLineString):
        def __init__(self, organizer: str) -> None:
            super().__init__(f"mailto:{organizer}")


