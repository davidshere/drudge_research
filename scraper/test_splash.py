import datetime
import unittest

from bs4 import BeautifulSoup, Tag

from page_metadata import parse_main_and_splash, ParseError
from drudge_data_classes import DrudgePageMetadata

EARLY_DT = datetime.datetime(2001, 11, 19, 0, 0)
LATE_DT = datetime.datetime(2017, 1, 1, 0, 0)

#TODO: The keys here should be datetimes, not numbers. That will require going and finding each page again in the archive
EXPECTED_RESULTS = {
 0: DrudgePageMetadata(splash_set=None, top_set=None),
 0.5: DrudgePageMetadata(splash_set=None, top_set={"Gen. Wesley Clark: 'White House tried to get me knocked off CNN'..."}),
 1: DrudgePageMetadata(splash_set={'ASHCROFT TO REQUIRE SOME VISITORS FINGERPRINTED'}, top_set={'India magazine paints scenario of horror...', 'NUCLEAR RIVALS EXCHANGE INSULTS... ', 'German delay threatens Meteor missile...'}),
 1.5: DrudgePageMetadata(splash_set={'WHAT WILL IT BE?'}, top_set={'Murdoch rebuffs level of DOW JONES family support...', 'Down to the Wire... '}),
 2: DrudgePageMetadata(splash_set=None, top_set=None),
 3: DrudgePageMetadata(splash_set={'CBS: BUSH KNEW IRAQ INFO WAS FALSE'}, top_set=None),
 4: DrudgePageMetadata(splash_set={'New worm spreading rapidly across Internet'}, top_set={'Dow Hits 31-Month High...'}),
 5: DrudgePageMetadata(splash_set={'HELL STORM SLAMS COAST; WINDS TOP 145 MPH'}, top_set=None),
 6: DrudgePageMetadata(splash_set=None, top_set={"FLASHBACK:  Judge in charge of Saddam Hussein's trial was in fear for his life today after his identity was revealed by a UK newspaper..."}),
 7: DrudgePageMetadata(splash_set={'Relief Head Questions New Orleans Reopen'}, top_set={'Money Earmarked for Evacuation Was Redirected...', 'Adios, Posse Comitatus:  Military May Play Bigger Relief Role...', 'Dem Brazile:  I Will Rebuild With You, Mr. President...'}),
 8: DrudgePageMetadata(splash_set={'Bird flu confirmed:  Dead swan in the UK'}, top_set={"Clinton Deja Vu: Hillary Caught Stealing Bill's Old Lines... ", 'Sen. Clinton says immigration bill would make her a criminal...'}),
 9: DrudgePageMetadata(splash_set=None, top_set={'DRUDGE RADIO LIVE SUNDAY NIGHT 10 PM ET TO 1 AM... HEARD IN ALL 50 STATES...'}),
 10: DrudgePageMetadata(splash_set={'STALEMATE'}, top_set={'BIGGEST GOVERNMENT   EVER!  Fed revenue collections and spending  at all-time highs... MORE...'}),
 11: DrudgePageMetadata(splash_set={'TROUBLE IN THE CITI'}, top_set={"CAN SHE BEAT THEM?  New poll shows Clinton trails top '08 Republicans..."}),
 12: DrudgePageMetadata(splash_set={'RUSSERT DEAD AT NBC'}, top_set={'Collapsed in the office...', 'Last interview...', 'Industry Shock...', 'Live Coverage...', 'Tributes pour in...', 'Towering figure in American journalism...', 'Network interrupted its regular programming...'}),
 13: DrudgePageMetadata(splash_set={'BLAGO STRIKES BACK!'}, top_set={'CHICAGOLAND:  Indicted Governor Names Obama Replacement...', 'On collision course with Washington...'}),
 14: DrudgePageMetadata(splash_set={'THE WAY IT USED TO BE'}, top_set={'Taliban video shows captive US soldier...'}),
 15: DrudgePageMetadata(splash_set={'SEAT ME'}, top_set={'NY POST:  COURIC, CBS REACH CROSSROADS...', 'COURIC FACES PAY CUT; DEEP LAYOFFS HIT CBSNEWS...', "'This is where I am for now'..."}),
 16: DrudgePageMetadata(splash_set={'PENTAGON EYES WIKILEAKS CHARGES'}, top_set={'US delays missile-zapping laser test for 4th time...', 'Iran unveils long-range bombing drone...'}),
 17: DrudgePageMetadata(splash_set={'SAUDI POLICE OPEN FIRE ON PROTESTERS'}, top_set={'SARKOZY, CAMERON TAKE CHARGE ON LIBYA...', 'Top U.S. Spy: GADHAFI WILL PREVAIL...', 'HILLARY: U.S. should wait for world to act...'}),
 18: DrudgePageMetadata(splash_set={'OBAMACARE HEADED FOR SUPREMES'}, top_set={'$200K Per Job? Geithner Says White House  Plan Still Bargain...'}),
 19: DrudgePageMetadata(splash_set={'ROMNEY WARNS:  OBAMA COMING FOR GUNS'}, top_set={'WHAT HAPPENS IN VEGAS, STAYS IN VEGAS:  GSA OFFICIAL TO THE FIFTH...'}),
 20: DrudgePageMetadata(splash_set={'THE MORNING AFTER'}, top_set=None),
 21: DrudgePageMetadata(splash_set={"TAXES IN FRANCE 'TOP 100% OF INCOME'"}, top_set=None),
 22: DrudgePageMetadata(splash_set={'MEX NUKE MYSTERY'}, top_set={'BLAST:  -40° MIDWEST!', 'Deep freeze across western half of nation...', 'Chill Temps Live...'}),
 23: DrudgePageMetadata(splash_set={'BOOK: HILLARY HAS BAD HEART'}, top_set=None),
 24: DrudgePageMetadata(splash_set={'EURABIA DEBATE ERUPTS'}, top_set={'Kouachi Rap Video... ', 'REPORT: Cop Executed In Street Was Muslim...', 'WIRES:  REUTERS...', 'Suspects spotted, manhunt continues...', 'Fear, paranoia in wooded area where  suspects hunted...', 'AFP...', 'Police find abandoned car with Molotov cocktails, Jihadist flags...', 'Before attack, French began ceding control of neighborhoods to Islamists...', "Britain's MI5 warns al Qaeda planning mass attacks on West...", 'Converge on small town...', 'Islamic immigration to USA on rise... ', 'Jewish residents fleeing...', 'Muslim Cleric Defends Slaughter... ', "Le Pen:  'Time's up for denial and hypocrisy'...", 'Female cop killed in separate Paris shooting...', "Europe's anti-Islamisation groups look to spread movement...", 'LIVE:  FRANCE 24...'}),
 25: DrudgePageMetadata(splash_set={'JARED SPEAKS!PUBLIC TALK ON MIDEAST PEACE', 'VIDEO'}, top_set={'*Role in Clinton email investigation under review...', "Flynn's plea fails to reveal smoking gun...", 'Inside secretive nerve center of investigation...', "PRESIDENT'S GALLUP POLL PLUNGE:  62% DISAPPROVAL...", 'REVEALED:  TRUMP HATER ON MUELLER TEAM...', 'House Republicans Prepare Contempt Action Against FBI, DOJ...', 'Special Counsel Removes Top Aide After Texts...'})}

# Add additional attributes to metadata objects that require them for testing
EXPECTED_RESULTS[1.5].raises = ParseError



def top_splash_to_text(top_and_splash):
  # don't want to test this
  if top_and_splash.splash_set:
    top_and_splash.splash_set = {tag.text for tag in top_and_splash.splash_set if isinstance(tag, Tag)}
  if top_and_splash.top_set:
    top_and_splash.top_set = {a.text for a in top_and_splash.top_set if isinstance(a, Tag)}
  return top_and_splash

def load_resource(page_number):
  with open('test/resources/test_file_{}.html'.format(page_number), 'r') as f:
    html = f.read()
  return BeautifulSoup(html, 'lxml') 


class TopAndSplashTest(unittest.TestCase):

  def test_parser(self):
    self.maxDiff=None
    for file_number in EXPECTED_RESULTS.keys():
      # need to simulate the datetimes that we're getting from a DayPage
      file_dt = EARLY_DT if file_number <= 14 else LATE_DT

      soup = load_resource(file_number)

      expected_result = EXPECTED_RESULTS[file_number]
      if hasattr(expected_result, 'raises'):
        with self.assertRaises(expected_result['raises']):
          top_splash_to_text(parse_main_and_splash(soup, file_dt))
      else:
        top_and_splash = top_splash_to_text(parse_main_and_splash(soup, file_dt))

        # don't want to test this
        self.assertEqual(expected_result, top_and_splash)


if __name__ == "__main__":
  unittest.main()
