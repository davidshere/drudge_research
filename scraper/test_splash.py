import datetime
import unittest

from bs4 import BeautifulSoup, Tag

from transform_page_into_drudge_links import *

EARLY_DT = datetime.datetime(2001, 11, 19, 0, 0)
LATE_DT = datetime.datetime(2017, 1, 1, 0, 0)

#TODO: The keys here should be datetimes, not numbers. That will require going and finding each page again in the archive
EXPECTED_RESULTS = {
  0: {
    'splash': set(),
    'top': set()
  },
  1: {
    'splash': {'ASHCROFT TO REQUIRE SOME VISITORS FINGERPRINTED'},
    'top': {
      'India magazine paints scenario of horror...',
      'NUCLEAR RIVALS EXCHANGE INSULTS... ',
      'German delay threatens Meteor missile...'
    }
  },
  2: {
    'splash': set(),
    'top': set()
  },
  3: {
    'splash': {'CBS: BUSH KNEW IRAQ INFO WAS FALSE'},
    'top': set()
  },
  4: {
    'splash': {'New worm spreading rapidly across Internet'},
    'top': {'Dow Hits 31-Month High...'}
  },
  5: {
    'splash': {'HELL STORM SLAMS COAST; WINDS TOP 145 MPH'},
    'top': set()
  },
  6: {
    'splash': set(),
    'top': {
      "FLASHBACK:  Judge in charge of Saddam Hussein's trial was in fear for his life today after his identity was revealed by a UK newspaper..."
    }
  },
  7: {
    'splash': {'Relief Head Questions New Orleans Reopen'},
    'top': {
      'Adios, Posse Comitatus:  Military May Play Bigger Relief Role...',
      'Money Earmarked for Evacuation Was Redirected...',
      'Dem Brazile:  I Will Rebuild With You, Mr. President...'
    }
  },
  8: {
    'splash': {'Bird flu confirmed:  Dead swan in the UK'},
    'top': {
      "Clinton Deja Vu: Hillary Caught Stealing Bill's Old Lines... ",
      'Sen. Clinton says immigration bill would make her a criminal...'
    }
  },
  9: {
    'splash': set(),
    'top': {'DRUDGE RADIO LIVE SUNDAY NIGHT 10 PM ET TO 1 AM... HEARD IN ALL 50 STATES...'}
  },
  10: {
    'splash': {'STALEMATE'},
    'top': {'BIGGEST GOVERNMENT   EVER!  Fed revenue collections and spending  at all-time highs... MORE...'}
  },
  11: {
    'splash': {'TROUBLE IN THE CITI'},
    'top': {"CAN SHE BEAT THEM?  New poll shows Clinton trails top '08 Republicans..."}
  },
  12: {
    'splash': {'RUSSERT DEAD AT NBC'},
    'top': {
      'Tributes pour in...',
      'Collapsed in the office...',
      'Last interview...',
      'Network interrupted its regular programming...',
      'Live Coverage...',
      'Towering figure in American journalism...',
      'Industry Shock...'
    }
  },
  13: {
    'splash': {'BLAGO STRIKES BACK!'},
    'top': {
      'On collision course with Washington...',
      'CHICAGOLAND:  Indicted Governor Names Obama Replacement...'
    }
  },
  14: {
    'splash': {'THE WAY IT USED TO BE'},
    'top': {'Taliban video shows captive US soldier...'}
  },
  15: {
    'splash': {'SEAT ME'},
    'top': {
        'COURIC FACES PAY CUT; DEEP LAYOFFS HIT CBSNEWS...',
        'NY POST:  COURIC, CBS REACH CROSSROADS...',
        "'This is where I am for now'..."
      }
    },
  16: {
    'splash': {'PENTAGON EYES WIKILEAKS CHARGES'},
    'top': {
      'Iran unveils long-range bombing drone...',
      'US delays missile-zapping laser test for 4th time...'
    }
  },
  17: {
    'splash': {'SAUDI POLICE OPEN FIRE ON PROTESTERS'},
    'top': {
      'SARKOZY, CAMERON TAKE CHARGE ON LIBYA...',
      'HILLARY: U.S. should wait for world to act...',
      'Top U.S. Spy: GADHAFI WILL PREVAIL...'
    }
  },
  18: {
    'splash': {'OBAMACARE HEADED FOR SUPREMES'},
    'top': {'$200K Per Job? Geithner Says White House  Plan Still Bargain...'}
  },
  19: {
    'splash': {'ROMNEY WARNS:  OBAMA COMING FOR GUNS'},
    'top': {'WHAT HAPPENS IN VEGAS, STAYS IN VEGAS:  GSA OFFICIAL TO THE FIFTH...'}
  },
  20: {
    'splash': {'THE MORNING AFTER'},
    'top': set()
  },
  21: {
    'splash': {"TAXES IN FRANCE 'TOP 100% OF INCOME'"},
    'top': set()
  },
  22: {
    'splash': {'MEX NUKE MYSTERY'},
    'top': {
      'BLAST:  -40\xb0 MIDWEST!',
      'Deep freeze across western half of nation...',
      'Chill Temps Live...'
    }
  },
  23: {
    'splash': {'BOOK: HILLARY HAS BAD HEART'},
    'top': set()
  },
  24: {
    'splash': {'EURABIA DEBATE ERUPTS'},
    'top': {
      'Suspects spotted, manhunt continues...',
      'Kouachi Rap Video... ',
      'Police find abandoned car with Molotov cocktails, Jihadist flags...',
      'Converge on small town...',
      'Fear, paranoia in wooded area where  suspects hunted...',
      'REPORT: Cop Executed In Street Was Muslim...',
      'Female cop killed in separate Paris shooting...',
      'Before attack, French began ceding control of neighborhoods to Islamists...',
      'Jewish residents fleeing...',
      'WIRES:  REUTERS...',
      'AFP...',
      'LIVE:  FRANCE 24...',
      "Europe's anti-Islamisation groups look to spread movement...",
      "Le Pen:  'Time's up for denial and hypocrisy'...",
      'Muslim Cleric Defends Slaughter... ',
      'Islamic immigration to USA on rise... ',
      "Britain's MI5 warns al Qaeda planning mass attacks on West..."
    }
  },
  0.5: {
    'splash': set(),
    'top': {"Gen. Wesley Clark: 'White House tried to get me knocked off CNN'..."}
  },
  1.5: {
    'splash': {'WHAT WILL IT BE?'},
    'top': {
      'Murdoch rebuffs level of DOW JONES family support...',
      'Down to the Wire... '
    },
    'raises': ParseError
  },
  25: {
    'splash': {'JARED SPEAKS!PUBLIC TALK ON MIDEAST PEACE', 'VIDEO'},
    'top': {
      'REVEALED:  TRUMP HATER ON MUELLER TEAM...',
      'Special Counsel Removes Top Aide After Texts...',
      '*Role in Clinton email investigation under review...',
      "Flynn's plea fails to reveal smoking gun...",
      'Inside secretive nerve center of investigation...',
      'House Republicans Prepare Contempt Action Against FBI, DOJ...',
      "PRESIDENT'S GALLUP POLL PLUNGE:  62% DISAPPROVAL..."
    }
  }
}

def top_splash_to_text(top_and_splash):
  # don't want to test this
  if top_and_splash['splash']:
    top_and_splash['splash'] = {tag.text for tag in top_and_splash['splash'] if isinstance(tag, Tag)}
  if top_and_splash['top']:
    top_and_splash['top'] = {a.text for a in top_and_splash['top'] if isinstance(a, Tag)}
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
      if 'raises' in expected_result.keys():
        with self.assertRaises(expected_result['raises']):
          top_splash_to_text(parse_main_and_splash(soup, file_dt))
      else:
        top_and_splash = top_splash_to_text(parse_main_and_splash(soup, file_dt))

        # don't want to test this
        self.assertEqual(expected_result, top_and_splash)


if __name__ == "__main__":
  unittest.main()