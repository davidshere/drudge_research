import datetime
import unittest

from bs4 import BeautifulSoup, Tag

from html_parser.page_metadata import parse_main_and_splash, ParseError
from drudge_data_classes import DrudgePageMetadata

EARLY_DT = datetime.datetime(2001, 11, 19, 0, 0)
LATE_DT = datetime.datetime(2017, 1, 1, 0, 0)


EXPECTED_RESULTS = {
 "20011118_235701": DrudgePageMetadata(splash_set=None, top_set=None),
 "20030826_212842": DrudgePageMetadata(splash_set=None, top_set={"Gen. Wesley Clark: 'White House tried to get me knocked off CNN'..."}),
 "20020605_181424": DrudgePageMetadata(splash_set={'ASHCROFT TO REQUIRE SOME VISITORS FINGERPRINTED'}, top_set={'India magazine paints scenario of horror...', 'NUCLEAR RIVALS EXCHANGE INSULTS... ', 'German delay threatens Meteor missile...'}),
 "20070730_190020": DrudgePageMetadata(splash_set={'WHAT WILL IT BE?'}, top_set={'Murdoch  rebuffs level of DOW JONES family support...', 'Down to the Wire...'}),
 "20030711_013426": DrudgePageMetadata(splash_set={'CBS: BUSH KNEW IRAQ INFO WAS FALSE'}, top_set=None),
 "20040127_003603": DrudgePageMetadata(splash_set={'New worm spreading rapidly across Internet'}, top_set={'Dow Hits 31-Month High...'}),
 "20040813_202402": DrudgePageMetadata(splash_set={'HELL STORM SLAMS COAST; WINDS TOP 145 MPH'}, top_set=None),
 "20050302_000200": DrudgePageMetadata(splash_set=None, top_set={"FLASHBACK:  Judge in charge of Saddam Hussein's trial was in fear for his life today after his identity was revealed by a UK newspaper..."}),
 "20050918_001000": DrudgePageMetadata(splash_set={'Relief Head Questions New Orleans Reopen'}, top_set={'Money Earmarked for Evacuation Was Redirected...', 'Adios, Posse Comitatus:  Military May Play Bigger Relief Role...', 'Dem Brazile:  I Will Rebuild With You, Mr. President...'}),
 "20060406_000558": DrudgePageMetadata(splash_set={'Bird flu confirmed:  Dead swan in the UK'}, top_set={"Clinton Deja Vu: Hillary Caught Stealing Bill's Old Lines... ", 'Sen. Clinton says immigration bill would make her a criminal...'}),
 "20061023_000428": DrudgePageMetadata(splash_set=None, top_set={'DRUDGE RADIO LIVE SUNDAY NIGHT 10 PM ET TO 1 AM... HEARD IN ALL 50 STATES...'}),
 "20070510_235228": DrudgePageMetadata(splash_set={'STALEMATE'}, top_set={'BIGGEST GOVERNMENT   EVER!  Fed revenue collections and spending  at all-time highs... MORE...'}),
 "20071127_000102": DrudgePageMetadata(splash_set={'TROUBLE IN THE CITI'}, top_set={"CAN SHE BEAT THEM?  New poll shows Clinton trails top '08 Republicans..."}),
 "20080613_230611": DrudgePageMetadata(splash_set={'RUSSERT DEAD AT NBC'}, top_set={'Collapsed in the office...', 'Last interview...', 'Industry Shock...', 'Live Coverage...', 'Tributes pour in...', 'Towering figure in American journalism...', 'Network interrupted its regular programming...'}),
 "20081230_222429"
: DrudgePageMetadata(splash_set={'BLAGO STRIKES BACK!'}, top_set={'CHICAGOLAND:  Indicted Governor Names Obama Replacement...', 'On collision course with Washington...'}),
 "20090719_002218": DrudgePageMetadata(splash_set={'THE WAY IT USED TO BE'}, top_set={'Taliban video shows captive US soldier...'}),
 "20100204_000826": DrudgePageMetadata(splash_set={'SEAT ME'}, top_set={'NY POST:  COURIC, CBS REACH CROSSROADS...', 'COURIC FACES PAY CUT; DEEP LAYOFFS HIT CBSNEWS...', "'This is where I am for now'..."}),
 "20100823_005023": DrudgePageMetadata(splash_set={'PENTAGON EYES WIKILEAKS CHARGES'}, top_set={'US delays missile-zapping laser test for 4th time...', 'Iran unveils long-range bombing drone...'}),
 "20110310_234242": DrudgePageMetadata(splash_set={'SAUDI POLICE OPEN FIRE ON PROTESTERS'}, top_set={'SARKOZY, CAMERON TAKE CHARGE ON LIBYA...', 'Top U.S. Spy: GADHAFI WILL PREVAIL...', 'HILLARY: U.S. should wait for world to act...'}),
 "20110926_235613": DrudgePageMetadata(splash_set={'OBAMACARE HEADED FOR SUPREMES'}, top_set={'$200K Per Job? Geithner Says White House  Plan Still Bargain...'}),
 "20120414_000031": DrudgePageMetadata(splash_set={'ROMNEY WARNS:  OBAMA COMING FOR GUNS'}, top_set={'WHAT HAPPENS IN VEGAS, STAYS IN VEGAS:  GSA OFFICIAL TO THE FIFTH...'}),
 "20121030_234354": DrudgePageMetadata(splash_set={'THE MORNING AFTER'}, top_set=None),
 "20130519_134536": DrudgePageMetadata(splash_set={"TAXES IN FRANCE 'TOP 100% OF INCOME'"}, top_set=None),
 "20131205_000917": DrudgePageMetadata(splash_set={'MEX NUKE MYSTERY'}, top_set={'BLAST:  -40° MIDWEST!', 'Deep freeze across western half of nation...', 'Chill Temps Live...'}),
 "20140623_000118": DrudgePageMetadata(splash_set={'BOOK: HILLARY HAS BAD HEART'}, top_set=None)
}


IDS_THAT_SHOULD_RAISE_PARSE_ERRORS = []# ['20070730_190020']

def top_splash_to_text(top_and_splash):
  # don't want to test this
  if top_and_splash.splash_set:
    top_and_splash.splash_set = {tag.text for tag in top_and_splash.splash_set if isinstance(tag, Tag)}
  if top_and_splash.top_set:
    top_and_splash.top_set = {a.text for a in top_and_splash.top_set if isinstance(a, Tag)}
  return top_and_splash

def load_resource(drudge_page_timestamp):
  with open('test/resources/{}.html'.format(drudge_page_timestamp), 'r') as f:
    html = f.read()
  return BeautifulSoup(html, 'html5lib') 

def deserialize_timestamp(drudge_page_timestamp):
  return datetime.datetime.strptime(drudge_page_timestamp, '%Y%m%d_%H%M%S')

class TopAndSplashTest(unittest.TestCase):

  def test_parser(self):
#    self.maxDiff=None
    for drudge_page_timestamp in EXPECTED_RESULTS.keys():
      # need to simulate the datetimes that we're getting from a DayPage
      soup = load_resource(drudge_page_timestamp)
      drudge_page_datetime_obj = deserialize_timestamp(drudge_page_timestamp)
      expected_result = EXPECTED_RESULTS[drudge_page_timestamp]
      if drudge_page_timestamp in IDS_THAT_SHOULD_RAISE_PARSE_ERRORS:
        with self.assertRaises(ParseError):
          top_splash_to_text(parse_main_and_splash(soup, drudge_page_datetime_obj))
      else:
        top_and_splash = top_splash_to_text(parse_main_and_splash(soup, drudge_page_datetime_obj))
        print("ex", expected_result)
        print("ts", top_and_splash)
        # don't want to test this
        self.assertEqual(expected_result, top_and_splash)


if __name__ == "__main__":
  unittest.main()
