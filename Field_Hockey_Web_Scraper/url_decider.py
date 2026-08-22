"""
url_decider.py
----------------
Entry point that accepts a URL and scouted team name, determines whether the
page uses a box layout or a non-box layout, and then launches the matching
scraper script.
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WORKSPACE = Path(__file__).resolve().parent
PAGE_LOAD_TIMEOUT = 20


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver that works both locally and on Streamlit Cloud.

    Streamlit Cloud usually runs on Linux with Chromium installed via
    packages.txt. Local development should fall back to Selenium Manager when
    a system browser/driver is not present.
    """
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    
    options = Options()

    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

      # If chromedriver is not already on PATH, use SeleniumBase to download it
    # into its managed drivers folder, then expose it on PATH for Selenium.
    chromedriver_path = shutil.which("chromedriver")
    if chromedriver_path is None:
        os.system("sbase get chromedriver")
        sb_driver_dir = Path.home() / ".local" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "seleniumbase" / "drivers"
        for candidate in [sb_driver_dir / "chromedriver", sb_driver_dir / "chromedriver.exe"]:
            if candidate.exists():
                chromedriver_path = str(candidate)
                break

    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
    else:
        # Last resort: let Selenium Manager attempt resolution.
        service = Service()

    chromium_candidates = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ]

    chromium_path = next((path for path in chromium_candidates if os.path.exists(path)), None)

    if chromium_path:
        options.binary_location = chromium_path
        

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def detect_layout(driver: webdriver.Chrome, url: str) -> str:
    """
    Detect whether the page appears to use a box layout.
    """
    driver.get(url)

    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException as exc:
        raise RuntimeError(f"Timed out while loading {url}") from exc

    try:
        driver.find_element(By.ID, "schedulePage")
    except NoSuchElementException:
        return "box"

    return "non-box"


def launch_scraper(layout: str, url: str, scouted_team: str, driver):
    """
    Call the scraper that matches the detected layout.
    """
    if layout == "box":
        script = WORKSPACE / "box_layout.py"
        print(f"[url_decider] Detected layout: {layout}")
        print(f"[url_decider] Launching: {script.name}")
        from box_layout import program

        return program(driver, url, scouted_team)

    script = WORKSPACE / "non_box_layout.py"
    print(f"[url_decider] Detected layout: {layout}")
    print(f"[url_decider] Launching: {script.name}")
    from non_box_layout import scrape_and_report

    try:
        return scrape_and_report(url, scouted_team, driver)
    except TypeError:
        return scrape_and_report(url, scouted_team)


def url_decider(url: str, scouted_team: str):
    """
    Create one driver, detect layout, and run the matching scraper.
    """
    driver = create_driver(headless=True)
    try:
        layout = detect_layout(driver, url)
        return launch_scraper(layout, url, scouted_team, driver)
    except NoSuchElementException:
        print("element not found in url \n try again")
        return None
    finally:
        driver.quit()
