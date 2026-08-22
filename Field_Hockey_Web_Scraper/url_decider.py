"""
url_decider.py
----------------
Entry point that accepts a URL and scouted team name, determines whether the
page uses a box layout or a non-box layout, and then launches the matching
scraper script.
"""

from __future__ import annotations

import os
import shutil
from contextlib import suppress
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

    # Prefer system-installed binaries from packages.txt on Streamlit Cloud.
    chromedriver_path = shutil.which("chromedriver")
    chromium_path = next(
        (
            path
            for path in [
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
            ]
            if os.path.exists(path)
        ),
        None,
    )

    # If Chromium is installed but the driver is not on PATH, check the common
    # apt install location before falling back to Selenium Manager.
    if not chromedriver_path:
        for path in ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver"]:
            if os.path.exists(path):
                chromedriver_path = path
                break

    if chromium_path:
        options.binary_location = chromium_path

    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
    else:
        service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as exc:
        browser_hint = chromium_path or "not found"
        driver_hint = chromedriver_path or "not found"
        raise RuntimeError(
            "Chrome could not start in Streamlit Cloud. "
            f"Chromium path: {browser_hint}. "
            f"Chromedriver path: {driver_hint}. "
            f"Original error: {type(exc).__name__}: {exc}. "
            "then redeploy the app."
        ) from exc

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
    driver = None
    try:
        driver = create_driver(headless=True)
        layout = detect_layout(driver, url)
        return launch_scraper(layout, url, scouted_team, driver)
    except NoSuchElementException as exc:
        raise RuntimeError(
            "The page structure did not match what the scraper expected. "
            "Please verify the URL is a valid SideArm schedule or boxscore page."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            "The scraper ran into a browser startup or page-loading problem. "
              f"Original error: {type(exc).__name__}: {exc}."
        ) from exc
    finally:
        with suppress(Exception):
            if driver is not None:
                driver.quit()
