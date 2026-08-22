"""
Document made to webscrape box layout field hockey score

Author: Frank Howden

"""

#making importations
from datetime import datetime
from requests import URLRequired
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import re
from penalty_corner_stats import compute_penalty_corner_stats, print_stats_report



    


        

#grab all boxscore hrefs that are in the schedule. 

def grab_boxscore_hrefs(driver):
    """
    Find all boxscore links on the schedule page.

    Args:
        driver: Active Selenium WebDriver on the schedule page.

    Returns:
        A list of Selenium elements that contain boxscore links.
    """
    
    #grabbing all the hrefs for box scores in the schedule. 
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sidearm-schedule-game-links-boxscore"))
    )
    #grabbing all the elements that have the class name "sidearm-schedule-game-opponent"
    elements=driver.find_elements(By.CLASS_NAME, "sidearm-schedule-game-links-boxscore")
    
    return elements



#for each box score, go into the href.
"""
grabs all the box score htmls that need to be scraped.
""" 
def grab_boxscore(elements):
    """
    Extract unique boxscore URLs from the schedule link elements.

    Args:
        elements: Selenium elements that wrap boxscore anchors.

    Returns:
        A deduplicated list of boxscore URLs.
    """
    box_score_links = []
    
    for element in elements:
        
        aTag=element.find_element(By.TAG_NAME, "a")
        box_score_links.append(aTag.get_attribute("href"))

    box_score_links=list(set(box_score_links))
    

    return box_score_links
        




#################################################################################
# Penalty Corners #
#################################################################################
def calc_total_penalty_corners(element, totalPCFor, totalPCAgainst,teamName):
    """
    Add the current row's corner totals to the right team bucket.

    Args:
        element: Table row that contains the corner totals.
        totalPCFor: Running total for the scouted team.
        totalPCAgainst: Running total for the opponent.
        teamName: Team name used to identify the scouted row.

    Returns:
        Updated totals as a tuple of (for, against).
    """
    
    #go to adjacent element
    
    td_tags=element.find_elements(By.TAG_NAME, "td")
    if(td_tags[0].text.lower()==teamName):
        
        for i in range(1,5):
            totalPCFor+=int(td_tags[i].text)
    else:
        for i in range(1,5):
            totalPCAgainst+=int(td_tags[i].text)
    
    return totalPCFor, totalPCAgainst
            


def get_penalty_corners(teamName,driver):
    """
    Read the penalty corner table for the current boxscore page.

    Args:
        teamName: Scouted team name used for row matching.
        driver: Active Selenium WebDriver on the boxscore page.

    Returns:
        A tuple of (penalty_corners_for, penalty_corners_against).
    """

    #find table
    tbody=driver.find_elements(By.TAG_NAME, "tbody")
    totalPCFor=0
    totalPCAgainst=0
    #go through each table and find the one with the header "PENALTY CORNERS" and print the data in that row.
    for body in tbody:
        
        tr=body.find_elements(By.TAG_NAME, "tr")
        #going through the row
        for row in tr:
            #look at headers of each row
            headers=row.find_elements(By.TAG_NAME, "th")
            #find header that says "PENALTY CORNERS" and print the data in that row.
            for header in headers:
                header_text=header.text.lower()
                if(header_text=="penalty corners" or header_text=="corner kicks"):
                    #step out of element
                    parent_element=header.find_element(By.XPATH, "..")
                    for i in range(2):
                        parent_element=parent_element.find_element(By.XPATH, "following-sibling::tr")
                        totalPCFor,totalPCAgainst=calc_total_penalty_corners(parent_element, totalPCFor, totalPCAgainst,teamName)
    return totalPCFor, totalPCAgainst
                    

#############################################################################################################
# Play-by-Play #        
#############################################################################################################
def loadPlayByPlayScreen(driver):
    """
    Reveal the play-by-play section on the current boxscore page.

    Args:
        driver: Active Selenium WebDriver on the boxscore page.

    Returns:
        The play-by-play WebElement when it is available.
    """
    #wait for box score to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "box-score")))

    #hide box score
    box_score_element=driver.find_element(By.ID, "box-score")
    driver.execute_script("arguments[0].setAttribute('aria-hidden','true');", box_score_element)
    driver.execute_script("arguments[0].style.display= 'none'", box_score_element)

    #wait for changes to take effect
    try: 
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "play-by-play")))
    except TimeoutException:
        print("play-by-play did not load in time.")
        return
    #unhide play-by-play
    playByPlay_element=driver.find_element(By.ID, "play-by-play")
    driver.execute_script("arguments[0].setAttribute('aria-hidden','false');", playByPlay_element)
    driver.execute_script("arguments[0].style.display= 'block'", playByPlay_element)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "play-by-play"))
    )
    #wait for the play-by-play table to load

    return playByPlay_element

def scrapeRows(rows,plays):
    """
    Filter raw play rows down to the plays we care about.

    Args:
        rows: Table rows from the play-by-play section.
        plays: Output list that receives matching play strings.

    Returns:
        None. Matching rows are appended into `plays`.
    """
    #wait for webdriver to load the table
    #go through each row and grab the text content of each row.
    for row in rows:
        raw=row.get_attribute("textContent")
        play=re.sub(r"\s+", " ", raw).strip().lower()
        if ('penalty corner' in play or 'shot by' in play or 'goal by' in play or 'corner kick' in play):
            plays.append(play)
    
    return 

def scrapePlayByPlayTable(playByPlay_element,plays):
    """
    Scrape every period table in the play-by-play section.

    Args:
        playByPlay_element: The play-by-play container element.
        plays: Output list that receives matching play strings.

    Returns:
        The same `plays` list after it has been updated.
    """
    
    #scrape the penalty corner totals before switching to playByPlays

     #all the periods in the play-by-play section are in a table with the id "period-1", "period-2", "period-3", "period-4"
    period_names=["period-1","period-2","period-3","period-4"]

    for period in period_names:
        #the table for each period
        period_table=playByPlay_element.find_element(By.ID, period)

        #get all the tables in the play-by-play section
        rows=period_table.find_elements(By.TAG_NAME, "tr")
        #scrape each row of the play-by-play table and look for penalty corner, shot_by, goal.
        scrapeRows(rows,plays)
    
    #get all the plays that have penalty corner, shot_by, goal and print the length of the list.
    return plays 


def getPlayByPlay(acronym,plays,PCs,driver):
    """
    Collect penalty corners and play-by-play text from one boxscore.

    Args:
        acronym: Team acronym or name used for matching.
        plays: Output list that receives matching play strings.
        PCs: Mutable two-item list for corner totals.
        driver: Active Selenium WebDriver on the boxscore page.

    Returns:
        None. Results are stored in `plays` and `PCs`.
    """

    #scrape penalty corners
    pc_for,pc_ags=get_penalty_corners(acronym,driver)
    PCs[0]+=pc_for
    PCs[1]+=pc_ags


    #hide the box score page and unhide the play-by-play page.
    playByPlay_element=loadPlayByPlayScreen(driver)
    #find all the plays that have penalty corner, shot_by, goal and print the length of the list.
    scrapePlayByPlayTable(playByPlay_element,plays)
    
    return
    
               


#############################################################################################################################
                            #WEBSCRAPE EACH BOX LINK# 
#############################################################################################################################


#webscrape each box score link 

def webscrape_box_score(link,plays,PCs, acronym,driver):
    """
    Load one boxscore URL and extract its stats.

    Args:
        link: Boxscore page URL.
        plays: Shared list for matching play strings.
        PCs: Shared two-item list for corner totals.
        acronym: Team acronym or name used for matching.
        driver: Active Selenium WebDriver.

    Returns:
        None. Extracted data is appended to the shared containers.
    """
    driver.get(link)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "large-6.columns"))
    )

    #get penalty corner totals for each team.
    
    
    getPlayByPlay(acronym=acronym,plays=plays, PCs=PCs,driver=driver)
    return
       
       


def go_into_box_score(box_score_links, acronym,driver):
    """
    Loop through all boxscore links and collect scraped data.

    Args:
        box_score_links: Unique boxscore URLs from the schedule page.
        acronym: Team acronym or name used for matching.
        driver: Active Selenium WebDriver.

    Returns:
        A tuple of (plays, PCs) gathered from every boxscore.
    """
    plays=[]
    PCs=[0,0]
    for link in box_score_links:
        webscrape_box_score(link,plays,PCs, acronym,driver)
    return plays, PCs
        


#penalty corner totals (T) for each team. 

#if penalty corners in OTs, take them and subtract for the total. 

#inside box score href, click play-by-play

#for each period (only 1-4 no OT), grab all Play-by-Play

#save all plays that have penalty corner, shot_by, goal. 

def program(driver,url:str,acronym:str):
    """
    Run the full box-layout scraping workflow.

    Args:
        driver: Active Selenium WebDriver.
        url: Schedule page URL to load.
        acronym: Team acronym or name used for matching.

    Returns:
        None. The report is written by penalty_corner_stats.py.
    """
    driver.get(url)
    print(f"\n{'='*60}")
    print(f"  Scouting: {acronym.upper()}")
    print(f"  URL: {url}")
    print(f"{'='*60}\n")
        
    elements=grab_boxscore_hrefs(driver)
    box_score_links=grab_boxscore(elements)
    plays,PCs=go_into_box_score(box_score_links,acronym,driver) 
    
   
    print("[scraper] browser closing...")
    driver.quit()
    print("[scraper] browser closed")
    # # use the penalty_corner_stats.py file to compute the penalty corner stats for each team.
    scouted_stats, opponent_stats = compute_penalty_corner_stats(plays, acronym)
    report=print_stats_report(acronym, scouted_stats, opponent_stats, PCs[0],PCs[1])
    return report


