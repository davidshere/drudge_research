import dataclasses
import datetime

@dataclasses.dataclass
class DrudgeBase:
  """ A base class for various resources that refer to a particular internet page """
  url: str


@dataclasses.dataclass
class DayPage(DrudgeBase):
  """ Represents a page on the archive capturing a day's worth of DrudgePages """
  dt: datetime.date


@dataclasses.dataclass
class DrudgePage(DrudgeBase):
  """ Represents an individual iteration of the drudge report """
  page_dt: datetime.datetime 


@dataclasses.dataclass
class DrudgeLink(DrudgeBase):
  """ Represents a particular link on a particular iteration of the drudge report """
  page_dt: datetime.datetime
  hed: str
  is_top: bool = False
  is_splash: bool = False
