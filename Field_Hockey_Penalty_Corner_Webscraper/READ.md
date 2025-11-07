# 📌 Field Hockey Penalty Corner Webscraper Scout
**by _Frank Howden_**

**Project description**: Penalty Corners are an essential part of a field hockey team's offense. As such, teams who are defending against penalty corners must be ready for them. This program webscrapped play-by-play game logs for any D1 Field Hockey Program. The user can chang inputs for certain website layouts and what words to search for the scrap the data. The program calculates penalty corner stats and logs the top 5 shot takers for penalty corners throughout the season. All of the data is placed into a .txt file. 

---

## 🧑‍💻 Libraries used
The project was completed in python. 

🐍 Coding Language: **Python**  
📚 Libraries: datetime, requests, selenium, time
🔗 [Link to code](https://github.com/HowdenFr/HowdenFr.github.io/blob/2fc8e109c29bde849038bf0302f7f7fd6dd398eb/Field_Hockey_Penalty_Corner_Webscraper/code/Field%20Hockey%20Pre-game%20Analysis%20webscraper%208-9-25.py)

---

## 🏑 Features of the Project  
📝 Step-by-step: The user needs to tweak a few things in the code for the program to work. All changes are labeled with a "#change" comment above the things the user needs to change. The user needs to change
*the link of a team's schedule
*the acronoym or label used to designate the team the program is webscrapping for. This helps identify the plays for the team the program is webscrapping for. 
*the acronym of the .txt file.

There are two types of website layouts which the program can handle. The first is a box type of layout, where the play-by-play has a box like layout. The second is called non-box (creative I know), where there aren't line dividers or a grid layout. Teams such as Davidson College, Richmond University, and Bucknell have this layout. To change the program to be able to read the box layout to the non-box layout, the user needs to comment out the box layout code and uncomment the non-box layout code. The sections of code for both layouts are commented in the python file. 

When the user has inputed all changes for the program, the user can run the python file. The program creates a new google chrome window and runs through the schedule webscrapping stats. 

When the program is over, it creates the .txt file. Photos below show what the program looks like webscrapping a box layout. 
![Start of program]()







