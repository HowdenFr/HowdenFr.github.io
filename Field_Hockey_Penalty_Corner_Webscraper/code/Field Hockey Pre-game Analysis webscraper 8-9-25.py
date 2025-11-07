"""
Webscraper to do pre-game analysis on penalty corner on opponents 

Author: Frank Howden 

"""

#making importations
from datetime import datetime
import bs4 
from bs4 import BeautifulSoup
import requests
from requests import URLRequired
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
import math



#all the periods
period_names=["period-1","period-2","period-3","period-4"]

period_titles=["1st Period", "2nd Period", "3rd Period", "4th Period"]
#count of player dictionary
player_dictionary={}






driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#go to website
#change
driver.get("https://vcuathletics.com/sports/fhockey/schedule")




#in this example, we are looking for the google search bar 

#look for all games
input_element=driver.find_elements(By.CSS_SELECTOR, 'a[target="_blank"]')




def shot_by_tracker(play_desc, team_acronym):
                             #[A-Z]

    team_pattern = "|".join([re.escape(name) for name in team_acronym])  # lock\ haven|haven

    match = re.search(
    rf"(?:shot|goal) by (?:{team_pattern})\s+([A-Za-z'\-]+(?: [A-Za-z'\-]+)*)",
    play_desc
)

    if match:

        name = match.group(1).strip()
        print(name)
       
        

        if(name in player_dictionary):
            shot_count=player_dictionary[name]
            shot_count=shot_count+1
            player_dictionary[name]=shot_count
        else:
            player_dictionary[name]=1
        
        return

    else:
    
        return


def corner_tracker(array,penalty_corner_count,recorner_count,goal_count, team_acronym): 
    plays_array=array
    #needs to be in a function...            
    last_play_pc=False
    last_play_time=datetime.strptime("00:00","%M:%S")

    for count in range(0, len(plays_array)):
            
            play_desc=plays_array[count]
            
            current_time=""
            

            if(play_desc[0]=='6' or "*" in play_desc[0:5] or ' pen' in play_desc[1:5]):
                continue

            if('--' in play_desc):
                play_desc="00:00" + play_desc[2:]
            
            elif("shot " in play_desc[0:5] or "penal" in play_desc[0:5] or "corne" in play_desc[0:5]):
                time_search=play_desc.split(".")
               
                if(len(time_search)>=3):
                    
                    play_desc=time_search[len(time_search)-1][1:] + " "+ time_search[0] + " " + time_search[1]
                else:
                    play_desc=time_search[1][1:] + " " + time_search[0]
            
            elif(len(play_desc[0:5].split(' '))==2):
                
                play_desc='0'+play_desc
                
                
            if(len(play_desc[0:5].split(':')[0])==1):
                play_desc='0' + play_desc

            
            if(play_desc[0:5]=='60:00'):
                current_time=datetime.strptime("59:59","%M:%S")
                current_play_pc=False
            else:
                current_time=datetime.strptime(play_desc[0:5],"%M:%S")
                current_play_pc=False
            
            if any(acronym in play_desc for acronym in team_acronym):
                
       
                if ('penalty corner' in play_desc):
                 
                    penalty_corner_count=penalty_corner_count +1
                    current_play_pc=True
                    if(current_play_pc and last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            recorner_count=recorner_count+1
                    #update the last plays
                    
                    last_play_time=current_time
                    last_play_pc=True
                
                elif ('corner kick' in play_desc):
                    
                    penalty_corner_count=penalty_corner_count+1
                    current_play_pc=True
                    if(current_play_pc and last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            recorner_count=recorner_count+1
                    last_play_time=current_time
                    last_play_pc=True
                
                elif('shot by' in play_desc):
                    print(play_desc)
                    if(last_play_pc):
                        time_difference=current_time-last_play_time
                        
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            shot_by_tracker(play_desc, team_acronym)

                    last_play_time=current_time
                    last_play_pc=False
                    
                    
                
                elif('goal by' in play_desc):
                   
                    
                    
                    print(play_desc)
                    if(last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            goal_count=goal_count+1
                            shot_by_tracker(play_desc, team_acronym)
                    last_play_pc=False
                    last_play_time=current_time

                else:

                    last_play_pc=False
                    last_play_time=current_time
            
            elif any(acronym not in play_desc for acronym in team_acronym):


                if ('penalty corner' in play_desc):
                    
                    penalty_corner_count=penalty_corner_count +1
                    current_play_pc=True
                    if(current_play_pc and last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            recorner_count=recorner_count+1
                    #update the last plays
                    
                    last_play_time=current_time
                    last_play_pc=True
                
                elif ('corner kick' in play_desc):
                    
                    penalty_corner_count=penalty_corner_count+1
                    current_play_pc=True
                    if(current_play_pc and last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            recorner_count=recorner_count+1
                    last_play_time=current_time
                    last_play_pc=True
                
                elif('goal by' in play_desc):
             
                    
                    
                    
                    if(last_play_pc):
                        time_difference=current_time-last_play_time
                        if(time_difference.total_seconds()<=12 and time_difference.total_seconds()>=0):
                            goal_count=goal_count+1
                    last_play_pc=False
                    last_play_time=current_time

                else:

                    last_play_pc=False
                    last_play_time=current_time

                

    return penalty_corner_count,recorner_count,goal_count


def stat_recon (input_element,penalty_corner_count,recorner_count,goal_count,def_p_c_c,def_r_c,def_g_c):
      
    # #Richmond and wake tags                                               #change
    #elements = driver.find_elements(By.XPATH, "//a[contains(@aria-label,'Box Score of University of Richmond')]")

    # #box layout tags
    elements = driver.find_elements(By.CSS_SELECTOR, "li.sidearm-schedule-game-links-boxscore a")


    #  # adjust selector
    box_score_links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]
    box_score_links=list(set(box_score_links))
    
 
    count = 0
    for box_score in box_score_links:
        off_array=[]
        def_array=[]
        #change
        team_acronym=["vcu", "virginia commonwealth university"]

      
        
        
        if("boxscore" in box_score):
            count=count + 1
            
         
            
            #go into box score link
            driver.get(str(box_score))
            time.sleep(3)
            
            """
            start of Richmond and Wake
            """
            
            # # #use only if Richmond, Wake Forest, Bucknell
            
            # # # #use for non-box layoyut
            # buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="s-tab__link"]')
            # for btn in buttons:
            #     if btn.text=="Play-by-play":
            #         driver.execute_script("arguments[0].click();", btn)
            #         time.sleep(3)
            

            
            # periods=driver.find_elements(By.CSS_SELECTOR, 'button[data-test-id="s-tab__link"]')
            # quarter=0
            # for period in periods:
                
            #     if(quarter>=4):
            #         continue
            #     if period.text==period_titles[quarter]:
            #         driver.execute_script("arguments[0].click();", period)
            #         quarter=quarter+1
            #         time.sleep(3)
            #         plays = driver.find_elements(By.CSS_SELECTOR, "div.stats")
            #         for play in plays:
            #             entry=re.sub(r"\s+", " ",play.text ).strip().lower()
                       
            #                 #CHANGE
            #             if ('penalty corner' in entry or 'shot by' in entry or 'goal by' in entry or 'corner kick' in entry):
            #                 if any(acronym in entry for acronym in team_acronym): 
                            
            #                     off_array.append(entry)
            # #                 #change
            #                 else:
            #                     def_array.append(entry)
                                

                    
            
            # penalty_corner_count,recorner_count,goal_count=corner_tracker(off_array,penalty_corner_count,recorner_count,goal_count,team_acronym)   
            # def_p_c_c, def_r_c, def_g_c=corner_tracker(def_array,def_p_c_c,def_r_c,def_g_c, team_acronym)

           
            """
            end of wake or richmond/ non box layout
            """
            
        

            """
            Start of Box Layout
            """

            #get to the play by play site
            section = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "box-score"))
            )
            driver.execute_script("arguments[0].setAttribute('aria-hidden', 'true')",section)
            driver.execute_script("arguments[0].style.display = 'none';", section)
            time.sleep(5)
            try:
                section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "play-by-play"))
        )
            except TimeoutException:
               print("no play-by-play")
               continue
            driver.execute_script("arguments[0].setAttribute('aria-hidden', 'false')",section)
            driver.execute_script("arguments[0].style.display = 'block';", section)


            

            time.sleep(5)
            #start tracking plays
            
            for i in period_names:
                period_table=driver.find_element(By.ID, i)
                rows=period_table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows: 
                    
                    raw=row.get_attribute("textContent")
            
                  
                    play=re.sub(r"\s+", " ",raw ).strip().lower()
               
                
                        #Change this for every team
                    if ('penalty corner' in play or 'shot by' in play or 'goal by' in play or 'corner kick' in play):
                            #change
                        if any(acronym in play for acronym in team_acronym): 
                            
                            off_array.append(play)
                            
                        else:
                            
                            def_array.append(play)

            
            penalty_corner_count,recorner_count,goal_count=corner_tracker(off_array,penalty_corner_count,recorner_count,goal_count,team_acronym)   
            def_p_c_c, def_r_c, def_g_c=corner_tracker(def_array,def_p_c_c,def_r_c,def_g_c, team_acronym)        
            
           
            
            
            
                    
            """
            end of box layout
            """
           
            
            # #reset
            time.sleep(6)
            print(count)
            print(player_dictionary)
        
        

    print(player_dictionary)
    return penalty_corner_count, player_dictionary,recorner_count,goal_count, def_p_c_c, def_r_c, def_g_c



def stat_calc(penalty_corner_count, player_dictionary,recorner_count, goal_count,def_p_c_c, def_r_c, def_g_c):
    #make calculations
    execution_rate=(goal_count/penalty_corner_count) * 100
    recorner_rate=(recorner_count/penalty_corner_count) * 100

    def_execution_rate=(def_g_c/def_p_c_c) * 100
    def_r_c_rate=(def_r_c/def_p_c_c) * 100

                #change
    document=open("VCU Post.txt", "a")
                                        #change
    document.writelines(["Game Stats for VCU \n", 
                         "Penalty Corners Total: " + str(penalty_corner_count) + "\n",
                         "Goals: " + str(goal_count)+ "\n",
                         "Execution rate: " + str(execution_rate)+ "% \n", 
                         "Recorners: " + str(recorner_count) + "\n",
                         "Recorner rate: " + str(recorner_rate) + "% \n",
                         "Top 5 shot takers: \n"])
    
    sorted_items = sorted(player_dictionary.items(), key=lambda x: x[1], reverse=True)

    # Print the top 5 items (key and value)
    
    for key, value in sorted_items[:5]:
        document.write(f"{key}: {value}" + "\n")
    
    document.writelines(["Defensive Penalty Corner Execution Rate: " + str(def_execution_rate)+ "% \n",
                         "Defensive Recorner Rate: " + str(def_r_c_rate) + "% \n"])
        
    document.close()
    return 


penalty_corner_count,player_dictionary,recorner_count,goal_count, def_p_c_c, def_r_c, def_g_c=stat_recon(input_element, 0, 0,0,0,0,0)   
time.sleep(5)
driver.close()

stat_calc(penalty_corner_count, player_dictionary,recorner_count,goal_count, def_p_c_c, def_r_c, def_g_c)
# always at the end












