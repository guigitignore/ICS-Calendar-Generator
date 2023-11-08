# This little libray allows to generate ICS file with a Python class approach
# Summary of defined classes:
# - Container
# - Calendar
# - Event
# - ContentLine
# - ContentLineDate
# - ContentLineTime
# - ContentLineParam


# We rely only on builtin python library
from datetime import datetime,timedelta
# Generate event UID
from uuid import uuid1

# this class allows to make a singleton class easily
class Singleton:
    _instance=None

    def __new__(cls,*args,**kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls,*args,**kwargs)
        return cls._instance
    
# A container in ICS file is delimited by BEGIN:<name> and END:<name>
# It can contains other container or just content lines
class Container(list):
    def __init__(self,name:str) -> None:
        super().__init__()
        #use uppercase key
        self.__name=name.upper()

    # stringify container
    def __str__(self) -> str:
        ret = ['BEGIN:' + self.__name]
        # we insert string representations of all elements between tags
        for line in self:
            ret.append(str(line))
        ret.append('END:' + self.__name)
        return "\r\n".join(ret)
    
    # basic representation (otherwise it shows empty list)
    def __repr__(self) -> str:
        return f"<ICS:Container:{self.__class__.__name__}>"    
    
# Content line is just an entry in ICS file. It syntax is <KEY>:<VALUE>
class ContentLine(list):
    def __init__(self,name:str,value:str) -> None:
        super().__init__()
        #use uppercase key
        self.__name=name.upper()
        self.__value=value

    def __str__(self) -> str:
        params=";".join([str(elt) for elt in self])
        # we must insert all parameter between key and value
        if params:
            params=";"+params
        return f'{self.__name}{params}:{self.__value}'
    
    def __repr__(self) -> str:
        return f"<ICS:ContentLine:{self.__class__.__name__}>"
    
# Content line params are inserted between ContentLine key and value and are separated by semicolons:
# Example: <KEY>;<PARAM_NAME>=<PARAM_VALUE>:<VALUE>
class ContentLineParam:
    def __init__(self,name:str,value:str) -> None:
        self.__name=name.upper()
        self.__value=value

    def __str__(self) -> str:
        return f"{self.__name}={self.__value}"
    
# This type of ContentLine represent a time with second precision
class ContentLineTime(ContentLine):
    # We use a special ContentLineParam to insert timezone id for each time.
    # Otherwise it uses UTC time
    # This class is a singleton because timezone is constant
    class CurrentTimezone(ContentLineParam,Singleton):
        def __init__(self) -> None:
            ContentLineParam.__init__(self,"TZID", datetime.now().astimezone().strftime("%Z"))

    # export datetime in the good format
    def __init__(self,name:str,instant:datetime) -> None:
        super().__init__(name.upper(),instant.strftime("%Y%m%dT%H%M%S"))
        self.append(ContentLineTime.CurrentTimezone())

# This ContentLine represent a date
class ContentLineDate(ContentLine):
    def __init__(self,name:str,date:datetime) -> None:
        super().__init__(name.upper(), date.strftime("%Y%m%d"))
        self.append(ContentLineParam("VALUE","DATE"))

# This class allow to insert quickly string type ContentLine
# It uses the name of the class as key and the value passed in argument as value 
class ContentLineString(ContentLine):
    def __init__(self, value: str) -> None:
        super().__init__(self.__class__.__name__.upper(), value)

# A calendar is the root container of the ICS file
# It contains some header field such as the version and the ProdId key
class Calendar(Container):
    def __init__(self) -> None:
        super().__init__("VCALENDAR")
        self.append(ContentLine("VERSION","2.0"))
        self.append(ContentLine("PRODID","guigitignore"))

# An Event is a container to represent an event
# It has recommanded fields: 
# - DTSTAMP is the instant of creation of the event
# - UID is a unique id associated to the event (Here I chose a UID generation based on the time -> uuid1)
# https://docs.python.org/3/library/uuid.html
class Event(Container):
    def __init__(self) -> None:
        super().__init__("VEVENT")
        self.append(ContentLineTime("DTSTAMP",datetime.now()))
        self.append(ContentLine("UID",str(uuid1()).upper()))

    # We define some well known keys in VEVENT
    class Summary(ContentLineString):
        pass

    class Description(ContentLineString):
        pass

    class Location(ContentLineString):
        pass
    
    class Organizer(ContentLineString):
        def __init__(self, organizer: str) -> None:
            super().__init__(f"mailto:{organizer}")


# Next we define some useful type of events:

# Date range event
class DateRangeEvent(Event):
    def __init__(self,begin:datetime,end:datetime) -> None:
        super().__init__()
        self.append(ContentLineDate("DTSTART",begin))
        self.append(ContentLineDate("DTEND",end))

# For a day event we must use the next day as end
class DayEvent(DateRangeEvent):
    def __init__(self,date:datetime) -> None:
        super().__init__(date,date+timedelta(days=1))

# Range time event
class TimeRangeEvent(Event):
    def __init__(self,begin:datetime,end:datetime) -> None:
        super().__init__()
        self.append(ContentLineTime("DTSTART",begin))
        self.append(ContentLineTime("DTEND",end))