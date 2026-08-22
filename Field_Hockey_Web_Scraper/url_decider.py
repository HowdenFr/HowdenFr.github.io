"""
url_decider.py
----------------
Entry point that accepts a URL and scouted team name, determines whether the
page uses a box layout or a non-box layout, and then launches the matching
scraper script.

This file is intentionally the only place that handles user input and layout
selection for now.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


WORKSPACE = Path(__file__).resolve().parent
PAGE_LOAD_TIMEOUT = 20


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Selenium Chrome driver for layout detection.

    Args:
        headless: If True, hide the browser window while loading pages.

    Returns:
        A configured Chrome WebDriver instance.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver




def detect_layout(driver: webdriver.Chrome, url: str) -> str:
    """
    Detect whether the page appears to use a box layout.

    Args:
        driver: Active Selenium WebDriver.
        url: Schedule or boxscore URL to inspect.

    Returns:
        "box" when the page matches the box-score pattern.
        "non-box" when the page looks like the alternate layout.
    """
    driver.get(url)

    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        raise RuntimeError(f"Timed out while loading {url}")

    try:
        driver.find_element(By.ID,"schedulePage")
        
    except NoSuchElementException:
        return "box"

    return "non-box"

     


def launch_scraper(layout: str, url: str, scouted_team: str,driver):
    """
    Call the scraper that matches the detected layout.

    Args:
        layout: Layout name returned by detect_layout().
        url: Source page URL entered by the user.
        scouted_team: Team name or abbreviation entered by the user.
        driver: Selenium driver reused for layout detection and scraping.

    Returns:
        None. The selected scraper handles its own reporting.
    """
    report=""
    if layout == "box":
        script = WORKSPACE / "box_layout.py"
        print(f"[url_decider] Detected layout: {layout}")
        print(f"[url_decider] Launching: {script.name}")
        from box_layout import program
        report=program(driver, url, scouted_team)
        
    else:
        script = WORKSPACE / "non_box_layout.py"
        print(f"[url_decider] Detected layout: {layout}")
        print(f"[url_decider] Launching: {script.name}")
        from non_box_layout import scrape_and_report
        try:
            report=scrape_and_report(url, scouted_team, driver)
        except TypeError:
            report=scrape_and_report(url, scouted_team)

    
    return report


def url_decider(url:str,scouted_team:str):
    """
    Create one driver, detect layout, and run the matching scraper.

    Args:
        url: Source page URL entered by the user.
        scouted_team: Team name or abbreviation entered by the user.

    Returns:
        None. Errors are printed or raised by the downstream scraper.
    """

    driver = create_driver(headless=True)
    try:
        layout = detect_layout(driver, url)
        report=launch_scraper(layout, url, scouted_team, driver)
    except NoSuchElementException:
        print("element not found in url \n try again")
    finally:
        driver.quit()

    return report



