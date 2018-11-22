import dataclasses
import datetime

import requests

import utils

@dataclasses.dataclass
class DrudgePageMetadata:
  """ Should populated by page_metadata.py """
  splash_set: set() = None
  top_set: set() = None


@dataclasses.dataclass
class DrudgeBase:
  """ A base class for various resources that refer to a particular internet page """
  url: str


@dataclasses.dataclass
class DayPage(DrudgeBase):
  """ Represents a page on the archive capturing a day's worth of DrudgePages """
  def __init__(self, dt: datetime.date):
    super().__init__(url=utils.day_page_url_from_dt(dt))
    self.dt = dt


@dataclasses.dataclass
class DrudgePage(DrudgeBase):
  """ Represents an individual iteration of the drudge report """
  def __init__(self, url: str, page_dt: datetime.datetime):
    super().__init__(url=url)
    self.page_dt = page_dt


  def __repr__(self):
    return f"  DrudgePage(url={self.url.__repr__()}, page_dt={self.page_dt.__repr__()}),"

  

@dataclasses.dataclass
class DrudgeLink(DrudgeBase):
  """ Represents a particular link on a particular iteration of the drudge report """
  page_dt: datetime.datetime
  hed: str
  is_top: bool = False
  is_splash: bool = False

  def to_csv(self):
    attrs = self.__dict__
    return ','.join([str(attrs[attr]) for attr in attrs])
