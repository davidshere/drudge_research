import datetime

def day_page_url_from_dt(dt: datetime.date) -> str:
  fmt_url = 'http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag'
  return fmt_url % (dt.year, dt.month, dt.day)
