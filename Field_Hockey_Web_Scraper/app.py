import streamlit as st
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
from collections import defaultdict, Counter, OrderedDict

# All the periods
period_names = ["period-1", "period-2", "period-3", "period-4"]
period_titles = ["1st Period", "2nd Period", "3rd Period", "4th Period"]

def shot_by_tracker(play_desc, team_acronym):
    team_pattern = "|".join([re.escape(name) for name in team_acronym])
    match = re.search(
        rf"(?:shot|goal) by (?:{team_pattern})\s+(.+)",
        play_desc
    )
    if match:
        name_part = match.group(1).strip()
        # Remove jersey numbers if present
        name_part = re.sub(r'^\d+\s*', '', name_part)
        # Split by comma for last, first
        if ',' in name_part:
            parts = name_part.split(',')
            last = parts[0].strip()
            first = parts[1].strip() if len(parts) > 1 else ''
        else:
            # Assume first last
            parts = name_part.split()
            if len(parts) >= 2:
                first = parts[0]
                last = ' '.join(parts[1:])
            else:
                last = name_part
                first = ''
        # Detect type
        if 'shot by' in play_desc:
            type_ = 'shot'
        else:
            type_ = 'goal'
        formatted = f"{type_} by {team_acronym[0]} {last}, {first}"
        return formatted
    return None

def corner_tracker(array, penalty_corner_count, recorner_count, goal_count, team_acronym, shot_goal_list):
    plays_array = array
    last_play_pc = False
    last_play_time = datetime.strptime("00:00", "%M:%S")

    for count in range(0, len(plays_array)):
        play_desc = plays_array[count]
        current_time = ""

        if (play_desc[0] == '6' or "*" in play_desc[0:5] or ' pen' in play_desc[1:5]):
            continue

        if ('--' in play_desc):
            play_desc = "00:00" + play_desc[2:]
        elif ("shot " in play_desc[0:5] or "penal" in play_desc[0:5] or "corne" in play_desc[0:5]):
            time_search = play_desc.split(".")
            if (len(time_search) >= 3):
                play_desc = time_search[len(time_search) - 1][1:] + " " + time_search[0] + " " + time_search[1]
            else:
                play_desc = time_search[1][1:] + " " + time_search[0]
        elif (len(play_desc[0:5].split(' ')) == 2):
            play_desc = '0' + play_desc
        if (len(play_desc[0:5].split(':')[0]) == 1):
            play_desc = '0' + play_desc

        if (play_desc[0:5] == '60:00'):
            current_time = datetime.strptime("59:59", "%M:%S")
            current_play_pc = False
        else:
            current_time = datetime.strptime(play_desc[0:5], "%M:%S")
            current_play_pc = False

        if any(acronym in play_desc for acronym in team_acronym):
            if ('penalty corner' in play_desc):
                penalty_corner_count = penalty_corner_count + 1
                current_play_pc = True
                if (current_play_pc and last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        recorner_count = recorner_count + 1
                last_play_time = current_time
                last_play_pc = True
            elif ('corner kick' in play_desc):
                penalty_corner_count = penalty_corner_count + 1
                current_play_pc = True
                if (current_play_pc and last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        recorner_count = recorner_count + 1
                last_play_time = current_time
                last_play_pc = True
            elif ('shot by' in play_desc):
                if (last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        formatted = shot_by_tracker(play_desc, team_acronym)
                        if formatted:
                            shot_goal_list.append(formatted)
                last_play_time = current_time
                last_play_pc = False
            elif ('goal by' in play_desc):
                if (last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        goal_count = goal_count + 1
                        formatted = shot_by_tracker(play_desc, team_acronym)
                        if formatted:
                            shot_goal_list.append(formatted)
                last_play_pc = False
                last_play_time = current_time
            else:
                last_play_pc = False
                last_play_time = current_time
        elif any(acronym not in play_desc for acronym in team_acronym):
            if ('penalty corner' in play_desc):
                penalty_corner_count = penalty_corner_count + 1
                current_play_pc = True
                if (current_play_pc and last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        recorner_count = recorner_count + 1
                last_play_time = current_time
                last_play_pc = True
            elif ('corner kick' in play_desc):
                penalty_corner_count = penalty_corner_count + 1
                current_play_pc = True
                if (current_play_pc and last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        recorner_count = recorner_count + 1
                last_play_time = current_time
                last_play_pc = True
            elif ('goal by' in play_desc):
                if (last_play_pc):
                    time_difference = current_time - last_play_time
                    if (time_difference.total_seconds() <= 12 and time_difference.total_seconds() >= 0):
                        goal_count = goal_count + 1
                last_play_pc = False
                last_play_time = current_time
            else:
                last_play_pc = False
                last_play_time = current_time

    return penalty_corner_count, recorner_count, goal_count

def stat_recon(driver, url, layout, team_acronym):
    driver.get(url)
    time.sleep(3)

    input_element = driver.find_elements(By.CSS_SELECTOR, 'a[target="_blank"]')

    penalty_corner_count = 0
    recorner_count = 0
    goal_count = 0
    def_p_c_c = 0
    def_r_c = 0
    def_g_c = 0
    shot_goal_list = []

    if layout == "box":
        elements = driver.find_elements(By.CSS_SELECTOR, "li.sidearm-schedule-game-links-boxscore a")
    else:
        # For non-box, assume similar
        elements = driver.find_elements(By.CSS_SELECTOR, 'a[target="_blank"]')  # Adjust if needed

    box_score_links = [el.get_attribute("href") for el in elements if el.get_attribute("href") and "boxscore" in el.get_attribute("href")]
    box_score_links = list(set(box_score_links))

    count = 0
    for box_score in box_score_links:
        off_array = []
        def_array = []
        if ("boxscore" in box_score):
            count = count + 1
            driver.get(str(box_score))
            time.sleep(3)

            if layout == "non-box":
                # Non-box layout logic
                buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="s-tab__link"]')
                for btn in buttons:
                    if btn.text == "Play-by-play":
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        break
                periods = driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="s-tab__link"]')
                quarter = 0
                for period in periods:
                    if (quarter >= 4):
                        continue
                    if period.text == period_titles[quarter]:
                        driver.execute_script("arguments[0].click();", period)
                        quarter = quarter + 1
                        time.sleep(3)
                        plays = driver.find_elements(By.CSS_SELECTOR, "div.stats")
                        for play in plays:
                            entry = re.sub(r"\s+", " ", play.text).strip().lower()
                            if ('penalty corner' in entry or 'shot by' in entry or 'goal by' in entry or 'corner kick' in entry):
                                if any(acronym in entry for acronym in team_acronym):
                                    off_array.append(entry)
                                else:
                                    def_array.append(entry)
            else:
                # Box layout
                section = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "box-score"))
                )
                driver.execute_script("arguments[0].setAttribute('aria-hidden', 'true')", section)
                driver.execute_script("arguments[0].style.display = 'none';", section)
                time.sleep(5)
                try:
                    section = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "play-by-play"))
                    )
                except TimeoutException:
                    raise Exception("No play-by-play section found. Please check the layout type.")
                driver.execute_script("arguments[0].setAttribute('aria-hidden', 'false')", section)
                driver.execute_script("arguments[0].style.display = 'block';", section)
                time.sleep(5)

                for i in period_names:
                    try:
                        period_table = driver.find_element(By.ID, i)
                        rows = period_table.find_elements(By.TAG_NAME, "tr")
                        for row in rows:
                            raw = row.get_attribute("textContent")
                            play = re.sub(r"\s+", " ", raw).strip().lower()
                            if ('penalty corner' in play or 'shot by' in play or 'goal by' in play or 'corner kick' in play):
                                if any(acronym in play for acronym in team_acronym):
                                    off_array.append(play)
                                else:
                                    def_array.append(play)
                    except:
                        continue

            penalty_corner_count, recorner_count, goal_count = corner_tracker(off_array, penalty_corner_count, recorner_count, goal_count, team_acronym, shot_goal_list)
            def_p_c_c, def_r_c, def_g_c = corner_tracker(def_array, def_p_c_c, def_r_c, def_g_c, team_acronym, shot_goal_list)

            time.sleep(6)

    return penalty_corner_count, recorner_count, goal_count, def_p_c_c, def_r_c, def_g_c, shot_goal_list

st.title("Field Hockey Scout Web Scraper")

tab1, tab2, tab3 = st.tabs(["URL Input", "Layout Selection", "Run Scraper"])

with tab1:
    url = st.text_input("Enter the team scouting website URL", value="https://vcuathletics.com/sports/fhockey/schedule")
    team_acronym_input = st.text_input("Enter team acronym (comma separated)", value="vcu, virginia commonwealth university")
    team_acronym = [x.strip() for x in team_acronym_input.split(',')]

with tab2:
    layout = st.radio("Select layout type", ["box", "non-box"])

with tab3:
    if st.button("Run Scraper"):
        with st.spinner("Scraping..."):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                penalty_corner_count, recorner_count, goal_count, def_p_c_c, def_r_c, def_g_c, shot_goal_list = stat_recon(driver, url, layout, team_acronym)
                driver.close()

                execution_rate = (goal_count / penalty_corner_count) * 100 if penalty_corner_count > 0 else 0
                recorner_rate = (recorner_count / penalty_corner_count) * 100 if penalty_corner_count > 0 else 0
                def_execution_rate = (def_g_c / def_p_c_c) * 100 if def_p_c_c > 0 else 0
                def_r_c_rate = (def_r_c / def_p_c_c) * 100 if def_p_c_c > 0 else 0

                st.subheader("Game Stats")
                st.write(f"Penalty Corners Total: {penalty_corner_count}")
                st.write(f"Goals: {goal_count}")
                st.write(f"Execution rate: {execution_rate:.2f}%")
                st.write(f"Recorners: {recorner_count}")
                st.write(f"Recorner rate: {recorner_rate:.2f}%")
                st.write(f"Defensive Penalty Corner Execution Rate: {def_execution_rate:.2f}%")
                st.write(f"Defensive Recorner Rate: {def_r_c_rate:.2f}%")

                st.subheader("Shots and Goals")
                for item in shot_goal_list:
                    st.write(item)

            except Exception as e:
                st.error(f"Error: {str(e)}. Please check the URL and layout type.")