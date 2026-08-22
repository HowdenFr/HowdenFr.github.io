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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


WORKSPACE = Path(__file__).resolve().parent
PAGE_LOAD_TIMEOUT = 20


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver that works both locally and on Streamlit Cloud.

    Streamlit Cloud runs on Linux and uses Chromium installed via apt-get.
    The binary paths are different from a local Windows/Mac install, so we
    check for the Streamlit Cloud paths first and fall back to defaults
    for local development.
    """
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    import os

    options = Options()

    # --- Always headless on a server (no display available) ---
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")           # required on Linux servers
    options.add_argument("--disable-dev-shm-usage") # prevents memory crashes
    options.add_argument("--disable-gpu")           # no GPU on cloud servers
    options.add_argument("--window-size=1920,1080")

    # --- Detect Streamlit Cloud vs local ---
    # Streamlit Cloud installs Chromium via apt at this path
    chromium_path = "/usr/bin/chromium"
    chromedriver_path = "/usr/bin/chromedriver"

    if os.path.exists(chromium_path):
        # We're on Streamlit Cloud — point directly at the apt-installed binaries
        options.binary_location = chromium_path

        service = Service(executable_path=chromedriver_path)
    else:
        # We're local — let Selenium Manager find the right driver automatically
        service = Service()  # Selenium 4.6+ handles this with no arguments

    driver = webdriver.Chrome(service=service, options=options)
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



