"""
boxscore_scraper.py
-------------------
Scrapes the play-by-play section from college field hockey box score pages
and feeds the results into penalty_corner_stats.py.

TARGET LAYOUT: Sidearm Sports box score pages (used by many NCAA schools,
e.g. bucknellbison.com, goleathernecks.com, gofrogs.com, etc.)

The play-by-play on these pages is NOT a simple table — each play is
spread across TWO adjacent <td> cells inside a <tr> inside the
play-by-play section:
    Cell 1: the team logo image (alt text = team name)
    Cell 2: the text of the play ("Shot by Bucknell Kira Leclercq, Blocked.")

Timestamps appear as standalone <td> cells that only contain a time string
and no team logo.

HOW TO USE:
    from boxscore_scraper import scrape_and_report
    scrape_and_report(
        url="https://bucknellbison.com/.../boxscore/20270",
        scouted_team="Bucknell",
    )

Or run directly:
    python boxscore_scraper.py
"""

import re
import string
import time

# ---------------------------------------------------------------------------
# Selenium imports — make sure you have:
#   pip install selenium
# and a matching ChromeDriver / geckodriver on your PATH.
# ---------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Our stats engine from the other file
from penalty_corner_stats import compute_penalty_corner_stats, print_stats_report


# ---------------------------------------------------------------------------
# Constants you can tweak
# ---------------------------------------------------------------------------

# How many seconds to wait for the page to load before giving up
PAGE_LOAD_TIMEOUT = 20

# How many seconds to wait between page actions (be polite to servers)
POLITE_DELAY = 3.5


# ---------------------------------------------------------------------------
# Browser setup
# ---------------------------------------------------------------------------

def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create and return a Selenium Chrome WebDriver.

    We run headless (no visible browser window) by default so this works
    on servers and in automation. Set headless=False if you want to watch
    the browser while debugging.

    Args:
        headless: If True, run Chrome without a visible window.

    Returns:
        A configured Chrome WebDriver instance.
    """
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

#############################################################################################################################
# ---------------------------------------------------------
# grab all boxscore hrefs that are in the schedule
#----------------------------------------------------------

def grab_boxscore_hrefs(driver, url): 
    """
    grabs all the box score hrefs that are in the schedule.
    """
    driver.get(url)
    WebDriverWait(driver,PAGE_LOAD_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[class='s-game-card__header-inner-top flex w-full flex-row']"))
    )
    #grabbing all the elements that have the css selecter data-test-id='s-btn__root' which is the box score button"

    elements=driver.find_elements(By.CSS_SELECTOR, "a[class*='s-btn inline-flex cursor-pointer select-none appearance-none items-center justify-center transition-colors duration-75 disabled:cursor-not-allowed s-btn--theme-light-theme s-btn--size-small s-btn--type-priority s-game-card-game-link-button s-game-card__content__button-icon-boxscore last']")
    

    return elements

# ---------------------------------------------------------------------------------------------------------------------------------------------
# For each box score, go into the href.
# ---------------------------------------------------------------------------------------------------------------------------------------------
def grab_boxscore(elements):
    box_score_links=[]

    for element in elements: 
        # Some schedule cards are anchors themselves, while others wrap the
        # link in a child <a>. Try the direct href first, then fall back to a
        # nested link.
        href = element.get_attribute("href")
        if not href:
            try:
                href = element.find_element(By.CSS_SELECTOR, "a[href]").get_attribute("href")
            except NoSuchElementException:
                href = None

        if href:
            box_score_links.append(href)

    #getting rid of duplicate links
    box_score_links=list(set(box_score_links))

    return box_score_links

#############################################################################################################################

# ---------------------------------------------------------------------------
# Page navigation helpers
# ---------------------------------------------------------------------------

def load_page(driver: webdriver.Chrome, url: str) -> bool:
    """
    Navigate to a URL and wait for the page body to appear.

    Returns True if the page loaded successfully, False on timeout.

    Args:
        driver: Active Selenium WebDriver.
        url:    Full URL to load (e.g. "https://bucknellbison.com/...").

    Returns:
        True on success, False on failure.
    """
    try:
        print(f"[scraper] Loading: {url}")
        driver.get(url)
        # Wait until at least a <body> tag appears — basic sanity check
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), ' Box Score ')]"))
        )
        # Small delay to let JavaScript finish rendering dynamic content
        time.sleep(POLITE_DELAY)
        return True
    except TimeoutException:
        print(f"[scraper] ERROR: Page timed out after {PAGE_LOAD_TIMEOUT}s")
        return False


def click_play_by_play_tab(driver: webdriver.Chrome) -> bool:
    """
    Some box score pages hide the play-by-play behind a tab or button.
    This function looks for a "Play-by-play" link/button and clicks it.

    HOW IT WORKS:
        We search for any clickable element whose visible text contains
        "play" and "play" (case-insensitive), which matches labels like
        "Play-by-play", "Play by Play", "PBP", etc.

        If no tab is found, we assume the play-by-play is already visible
        on the page and return True anyway.

    Args:
        driver: Active Selenium WebDriver with the page already loaded.

    Returns:
        True if a tab was clicked or no tab was needed.
        False if a tab was found but couldn't be clicked.
    """
    # These CSS selectors cover common tab/button patterns across school sites
    tab_selectors = [
        "a[href*='play-by-play']",          # anchor with play-by-play in href
        "button[data-target*='pbp']",        # Bootstrap data-target button
        "li a[href*='pbp']",                 # list-item tab link
        ".tab-content a",                    # generic tab content link
    ]

    for selector in tab_selectors:
        try:
            tab = driver.find_element(By.CSS_SELECTOR, selector)
            tab.click()
            time.sleep(POLITE_DELAY)  # Wait for tab content to render
            print("[scraper] Clicked play-by-play tab.")
            return True
        except NoSuchElementException:
            continue  # Try the next selector

    # If none of the selectors found a tab, check if there's a text match
    try:
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH,"//*[contains(@id, 0-0-0-panel-1)]" ))
            )
        except TimeoutException:
            print("play-by-play did not load in time.")
            return True

        #hide box score
        boxScore_element=driver.find_element(By.XPATH, "//*[contains(@id, 0-0-0-panel-0)]")
        driver.execute_script("arguments[0].style.display=''", boxScore_element)

        #reveal playByPlay
        playByPlay_element=driver.find_element(By.XPATH, "//*[contains(@id, 0-0-0-panel-1)]")
        driver.execute_script("arguments[0].style.display= 'none'", playByPlay_element)

        return True

    
    except NoSuchElementException:
        # No tab found — play-by-play is probably already visible
        print("[scraper] No play-by-play tab found; assuming content is visible.")
        return True

# ---------------------------------------------------------------------------
# Penalty Corner Extraction
# ---------------------------------------------------------------------------
def calc_total_penalty_corners(parent_element, totalPCFor, totalPCAgainst,teamName):
    """
    Add the row's corner totals to the proper team bucket.

    Args:
        parent_element: Table row that contains the corner totals.
        totalPCFor: Running total for the scouted team.
        totalPCAgainst: Running total for the opponent.
        teamName: Team name used to identify the scouted row.

    Returns:
        Updated totals as a tuple of (for, against).
    """
    # Read the row directly under the corner header.
        
    td_tags=parent_element.find_elements(By.TAG_NAME, "td")
    team_name_tag=td_tags[0].get_property("textContent").lower()
    if(team_name_tag==teamName.lower()):
        
        for i in range(1,5):
            totalPCFor+=int(td_tags[i].get_property("textContent"))
    else:
        for i in range(1,5):
            totalPCAgainst+=int(td_tags[i].get_property("textContent"))
    
    return totalPCFor, totalPCAgainst



def extract_pc_sidearm(driver,teamName):
    """
    Read the penalty corner totals from a Sidearm boxscore page.

    Args:
        driver: Active Selenium WebDriver.
        teamName: Team name used to identify the scouted row.

    Returns:
        A tuple of (penalty_corners_for, penalty_corners_against).
    """
    tbody=driver.find_elements(By.TAG_NAME, "tbody")
    totalPCFor=0
    totalPCAgainst=0

  
    #going through the row
    for body in tbody: 

        tr=body.find_elements(By.TAG_NAME, "tr")
        #going through the row

        for row in tr: 
            #look at headers of each row
            headers=row.find_elements(By.TAG_NAME, "th")

            #find header that Says "PENALTY CORNERS" and print the data in that row.
            for header in headers:
                header_text=header.get_property("textContent").lower()
                
                if(header_text=="penalty corners" or header_text=="corner kicks"):
                    #step out of element
                    parent_element=header.find_element(By.XPATH, "..")
                    for i in range(2):
                        parent_element=parent_element.find_element(By.XPATH, "following-sibling::tr")
                        totalPCFor,totalPCAgainst=calc_total_penalty_corners(parent_element, totalPCFor, totalPCAgainst,teamName)
    return totalPCFor, totalPCAgainst
                                            



# ---------------------------------------------------------------------------
# Play-by-play text extraction
# ---------------------------------------------------------------------------

def scrape_scouted_team_side(row): 
    """
    Extract the home-side play text from a play-by-play row.

    Args:
        row: The current play-by-play row being inspected.

    Returns:
        The home-side text or an empty string if it is missing.
    """
    
    # Use a relative XPath so we only inspect the current row.
    content = row.find_element(By.XPATH, ".//*[contains(@class, 'home-content')]")
    text = content.get_property("textContent")

    if not text:
        return ""

    return text
        

def scrape_time(row):
    """
    Extract the timestamp from a play-by-play row.

    Args:
        row: The current play-by-play row being inspected.

    Returns:
        The play time string.
    """

    # These XPath queries must stay relative to the row, or Selenium will
    # grab the first matching element on the entire page every time.
    content = row.find_element(By.XPATH, ".//*[contains(@class, 'timeline__middle')]")
    time_content = content.find_element(By.XPATH, ".//*[contains(@class, 'timeline__point')]").get_property("textContent")
    if(len(time_content)>5):
        time_content=time_content[1:len(time_content)-1]
    
    return time_content

def scrape_scouted_opp_side(row):
    """
    Extract the away-side play text from a play-by-play row.

    Args:
        row: The current play-by-play row being inspected.

    Returns:
        The away-side text or an empty string if it is missing.
    """

    # Use a relative XPath so the search is limited to this row.
    content = row.find_element(By.XPATH, ".//*[contains(@class, 'away-content')]")
    text = content.get_property("textContent")

    if not text:
        return ""

    return text

def extract_plays_sidearm(driver: webdriver.Chrome, plays: list) -> list:
    """
    Extract play-by-play strings from a Sidearm Sports box score page.

    HOW SIDEARM FORMATS THE PLAY-BY-PLAY:
    ──────────────────────────────────────
    The play-by-play section is a series of <div> rows. Each row has cells
    that contain either:
        (a) A timestamp like "10:37" — appears alone in a <td>
        (b) A team logo <img> and a play description text — in adjacent <td>s
        (c) A goal banner row (contains "GOAL" in large text)

    The page also has period header rows ("Start of 2nd period") and
    "End of Period" rows which we skip.

    STRATEGY:
        1. Find all <div> rows in the play-by-play section.
        2. For each row, read all <td> cell texts.
        3. If a cell has a timestamp pattern, remember it as `current_time`.
        4. If a cell has a play keyword (Shot, Penalty corner, GOAL by),
           combine it with `current_time` to make a complete play string.
        5. Yield the combined string.

    This is generic — it doesn't rely on specific class names that might
    differ between school websites.

    Args:
        driver: Active Selenium WebDriver on the box score page.

    Returns:
        List of play strings, e.g.:
            ["10:37 Penalty corner by Sacred Heart Amelia Pellegrini [10:37].",
             "10:44 Shot by Sacred Heart Lizzie Mendrzycki, Blocked.",
             ...]
    """

    # ── Step 1: Locate the play-by-play container ─────────────────────────
    # Sidearm pages wrap play-by-play in a div with id or class containing
    # "play-by-play" or "pbp". We try several selectors, most specific first.
    container = _find_pbp_container(driver)
    if container is None:
        print("[scraper] WARNING: Could not find play-by-play container.")
        return []

    # ── Step 2: Get all table rows inside the container ───────────────────
    rows = container.find_elements(By.XPATH, "//*[contains(@class, 'relative grid')]")
   
    print(f"[scraper] Found {len(rows)} rows in play-by-play section.")

    
    

    
    
    #step 3, scrape the time
    #step 4, scrape the opposing team side 
    #step 5, convert the row into a string the parcer can look at 


    for row in rows:
        #step 1, find the row that has all the information 
        home_content=scrape_scouted_team_side(row)

        #step 2, scrape the scouting team side (always on the left)
        time_content=scrape_time(row)

        #step 3, scrape the opposing team side 
        opp_content=scrape_scouted_opp_side(row)

        #step 5, convert the row into a string the parcer can look at 
        row_text=""
        if(home_content==""):
            row_text=time_content+ " " + opp_content
        else:
            row_text= time_content + " " + home_content
        
    

    #     # ── Skip structural / non-play rows ──────────────────────────────
        if _is_structural_row(row_text):
            continue

   

    #     # ── Find the play description in the row ──────────────────────────
        play_text = _extract_play_text(row_text).strip().lower()
        if (play_text==""):
            continue
        else:
            plays.append(play_text)
            
    print(f"[scraper] Total plays extracted: {len(plays)}")
    return


def _find_pbp_container(driver: webdriver.Chrome):
    """
    Try several CSS/ID selectors to locate the play-by-play section.

    Different schools using the Sidearm platform may have slightly different
    div IDs or classes, so we try a list of known patterns. Returns the
    first match found, or None if nothing matches.

    Args:
        driver: Active Selenium WebDriver.

    Returns:
        A WebElement for the container, or None.
    """
    # Ordered from most specific to most generic
    selectors = [
        "#play-by-play",                    # ID used by many Sidearm sites
        "[id*='play-by-play']",             # ID containing "play-by-play"
        "[id*='pbp']",                      # ID containing "pbp"
        ".play-by-play",                    # class name
        "[class*='play-by-play']",          # class containing the string
        "[class*='pbp']",                   # class containing "pbp"
        "section.boxscore",                 # fallback: whole boxscore section
        "div.boxscore",
        "main",                             # last resort: entire main content
    ]

    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            
            return element
        except NoSuchElementException:
            continue

    return None  # Nothing found


def _is_structural_row(row_text: str) -> bool:
    """
    Return True if this row is a header, period marker, or other non-play row.

    We skip rows like:
        "Start of 2nd period [15:00]."
        "End of Period"
        "Sarah Althouse at goalie for Bucknell."
        "" (empty rows)

    Args:
        row_text: Full text content of the <tr> element.

    Returns:
        True if this row should be skipped.
    """
    if not row_text:
        return True  # Empty row

    low = row_text.lower()

    skip_phrases = [
        "start of",          # "Start of 2nd period"
        "end of period",     # "End of Period"
        "at goalie for",     # "Sarah Althouse at goalie for Bucknell."
        "team at goalie",    # "Team at goalie for Sacred Heart."
        "1st half",          # Period header labels in some formats
        "2nd half",
        "3rd half",
        "4th half",
        "overtime",
        "Foul",
        "Offside"
        
    ]

    for phrase in skip_phrases:
        if phrase in low:
            return True

    return False


# Keywords that identify a play we care about.
# Using lowercase for case-insensitive matching.
PLAY_KEYWORDS = [
    "penalty corner by",
    "corner kick by",
    "shot by",
    "goal by",
]


def _extract_play_text(row_text: str) -> str:
    """
    Find the play description within a row's cell texts.

    HOW IT WORKS:
        We look at each cell's text for any of our PLAY_KEYWORDS.
        The first cell that contains a keyword is our play description.

        We also handle GOAL rows which Sidearm renders differently —
        the full goal text appears in row_text even if no single cell
        has the complete string.

    Args:
        cell_texts: List of stripped text strings from each <td> in the row.
        row_text:   Full text content of the entire <tr> element.

    Returns:
        The play description string, or "" if no play is found in this row.
    """
    low_row = row_text.lower()
   
    # ── Check each cell for play keywords ─────────────────────────────────
    if "shot by" in low_row or "corner kick by" in low_row or "penalty corner by" in low_row or "goal by" in low_row:
        
        return low_row


    return ""  # No play found in this row


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------

def scrape_plays(urls: list, scouted_team: str, driver,headless: bool = True) -> tuple[list,list]:
    """
    Scrape all boxscore URLs and return plays plus corner totals.

    Args:
        urls: Boxscore URLs to visit.
        scouted_team: Team name used for corner counting.
        driver: Active Selenium WebDriver.
        headless: Kept for compatibility; not used here.

    Returns:
        A tuple of (plays, PCs).
    """
    
    PCs=[0,0]
    plays = []

    for url in urls:
        try:
            # Load the page
            success = load_page(driver, url)
            if not success:
                return []

            #Extract PCs
            penalty_corners=extract_pc_sidearm(driver,scouted_team)
            PCs[0]+=penalty_corners[0]
            PCs[1]+=penalty_corners[1]
            # Click the play-by-play tab if one exists
            #click_play_by_play_tab(driver)

            
            # Extract the plays
            extract_plays_sidearm(driver,plays)

        except Exception as e:
            # Catch-all so we always close the browser even if something crashes
            print(f"[scraper] UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print("[scraper] Completed Play-By-Play scrapping for link.")

        

        

    print(len(plays))
    return plays, PCs


def scrape_and_report(url: str, scouted_team: str, driver, headless: bool = True) -> None:
    """
    Run the full non-box scraping workflow and print the report.

    Args:
        url: Schedule page URL to load.
        scouted_team: Team name or acronym used for matching.
        driver: Active Selenium WebDriver.
        headless: Kept for compatibility; not used here.

    Returns:
        None. The report is printed by the stats module.
    """
    print(f"\n{'='*60}")
    print(f"  Scouting: {scouted_team.upper()}")
    print(f"  URL: {url}")
    print(f"{'='*60}\n")

   
    elements=grab_boxscore_hrefs(driver, url)
    box_score_links=grab_boxscore(elements)

    #Step 1: Go into each url and scrape the plays
    
    
    plays,PCs=scrape_plays(box_score_links, scouted_team,driver)

    print("[scraper] browser closing...")
    driver.quit()
    print("[scraper] browser closed")
    #step 2: create plays that are for and against scouted team
    scouted_stats, opponent_stats=compute_penalty_corner_stats(plays, scouted_team)

    #step 3: create a scouting report
    report=print_stats_report(scouted_team, scouted_stats, opponent_stats, PCs[0], PCs[1])

 
    return report



 

    
