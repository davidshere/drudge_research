import unittest

from grab_main_and_splash import *

TEST_FILE_NUMBERS = [24, 14]

EXPECTED_RESULTS = {
  1: {
    'splash': u'ASHCROFT TO REQUIRE SOME VISITORS FINGERPRINTED',
    'top': None
  },
  2: {
    'splash': None,
    'top': None
  },
  3: {
    'splash': u'CBS: BUSH KNEW IRAQ INFO WAS FALSE', 
    'top': []
  },
  4: {
    'splash': u'New worm spreading rapidly across Internet',
    'top': [u'Dow Hits 31-Month High...']
  },
  5: {
    'splash': u'HELL STORM SLAMS COAST; WINDS TOP 145 MPH', 'top': []},
  6: {'splash': None,
     'top': [u"FLASHBACK:  Judge in charge of Saddam Hussein's trial was in fear for his life today after his identity was revealed by a UK newspaper..."]},
  7: {'splash': u'Relief Head Questions New Orleans Reopen',
     'top': [u'Adios, Posse Comitatus:  Military May Play Bigger Relief Role...',
             u'Money Earmarked for Evacuation Was Redirected...',
             u'Dem Brazile:  I Will Rebuild With You, Mr. President...']},
  8: {'splash': u'Bird flu confirmed:  Dead swan in the UK',
     'top': [u"Clinton Deja Vu: Hillary Caught Stealing Bill's Old Lines... ",
             u'Sen. Clinton says immigration bill would make her a criminal...']},
  9: {'splash': None,
     'top': [u'DRUDGE RADIO LIVE SUNDAY NIGHT 10 PM ET TO 1 AM... HEARD IN ALL 50 STATES...']},
  10: {'splash': u'STALEMATE',
      'top': [u'BIGGEST GOVERNMENT   EVER!  Fed revenue collections and spending  at all-time highs... MORE...']},
  11: {'splash': u'TROUBLE IN THE CITI',
      'top': [u"CAN SHE BEAT THEM?  New poll shows Clinton trails top '08 Republicans..."]},
  12: {'splash': u'RUSSERT DEAD AT NBC',
      'top': [u'Tributes pour in...',
              u'Collapsed in the office...',
              u'Last interview...',
              u'Network interrupted its regular programming...',
              u'Live Coverage...',
              u'Towering figure in American journalism...',
              u'Industry Shock...']},
  13: {'splash': u'BLAGO STRIKES BACK!',
      'top': [u'On collision course with Washington...',
              u'CHICAGOLAND:  Indicted Governor Names Obama Replacement...']},
  14: {'splash': u'THE WAY IT USED TO BE',
      'top': [u'Taliban video shows captive US soldier...']},
  15: {'splash': u'SEAT ME',
      'top': [u'COURIC FACES PAY CUT; DEEP LAYOFFS HIT CBSNEWS...',
              u'NY POST:  COURIC, CBS REACH CROSSROADS...',
              u"'This is where I am for now'..."]},
  16: {'splash': u'PENTAGON EYES WIKILEAKS CHARGES',
      'top': [u'Iran unveils long-range bombing drone...',
              u'US delays missile-zapping laser test for 4th time...']},
  17: {'splash': u'SAUDI POLICE OPEN FIRE ON PROTESTERS',
      'top': [u'SARKOZY, CAMERON TAKE CHARGE ON LIBYA...',
              u'HILLARY: U.S. should wait for world to act...',
              u'Top U.S. Spy: GADHAFI WILL PREVAIL...']},
  18: {'splash': u'OBAMACARE HEADED FOR SUPREMES',
      'top': [u'$200K Per Job? Geithner Says White House  Plan Still Bargain...']},
  19: {'splash': u'ROMNEY WARNS:  OBAMA COMING FOR GUNS',
      'top': [u'WHAT HAPPENS IN VEGAS, STAYS IN VEGAS:  GSA OFFICIAL TO THE FIFTH...']},
  20: {'splash': u'THE MORNING AFTER', 'top': []},
  21: {'splash': u"TAXES IN FRANCE 'TOP 100% OF INCOME'", 'top': []},
  22: {'splash': u'MEX NUKE MYSTERY',
       'top': [u'BLAST:  -40\xb0 MIDWEST!',
               u'Deep freeze across western half of nation...',
               u'Chill Temps Live...']},
  23: {'splash': u'BOOK: HILLARY HAS BAD HEART', 'top': []},
  24: {'splash': u'EURABIA DEBATE ERUPTS',
      'top': [u'Suspects spotted, manhunt continues...',
              u'Kouachi Rap Video... ',
              u'Police find abandoned car with Molotov cocktails, Jihadist flags...',
              u'Converge on small town...',
              u'Fear, paranoia in wooded area where  suspects hunted...',
              u'REPORT: Cop Executed In Street Was Muslim...',
              u'Female cop killed in separate Paris shooting...',
              u'Before attack, French began ceding control of neighborhoods to Islamists...',
              u'Jewish residents fleeing...',
              u'WIRES:  REUTERS...',
              u'AFP...',
              u'LIVE:  FRANCE 24...',
              u"Europe's anti-Islamisation groups look to spread movement...",
              u"Le Pen:  'Time's up for denial and hypocrisy'...",
              u'Muslim Cleric Defends Slaughter... ',
              u'Islamic immigration to USA on rise... ',
              u"Britain's MI5 warns al Qaeda planning mass attacks on West..."]}}


def top_splash_to_text(top_and_splash):
  if top_and_splash['splash']:
    top_and_splash['splash'] = top_and_splash['splash'].text
  if top_and_splash['top']:
    top_and_splash['top'] = [a.text for a in top_and_splash['top']]
  return top_and_splash


class TopAndSplashTest(unittest.TestCase):

  def test_parser(self):
    for file_number in EXPECTED_RESULTS.keys():
      soup = load_html(file_number)
      top_and_splash = top_splash_to_text(get_main_and_splash(soup))
      self.assertEquals(EXPECTED_RESULTS[file_number], top_and_splash)

if __name__ == "__main__":
  unittest.main()