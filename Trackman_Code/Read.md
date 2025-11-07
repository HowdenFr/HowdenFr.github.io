# 📌 Trackman Visualization  
**by _Frank Howden_**

Project description: Davidson Baseball is a subscriber to Trackman baseball. Trackman is a program which records statistics on every pitch thrown throughout a game.
After each game, the Trackman program produces a CSV, holding every pitch thrown during the game. 
Unfortunately, Trackman does not provide visualization of pitches and hits like Synergy or Baseball Savant, leaving college teams with just raw data. 
I took on the task to create a visualization for the Trackman CSVs for Davidson Baseball. 

---

## 🧑‍💻 Libraries used
The project was completed in python. 

🐍 Coding Language: **Python**  
📚 Libraries: Pandas, Matplotlib, tkinter, mplcursors 
🔗 [Link to code](https://github.com/HowdenFr/HowdenFr.github.io/blob/528fcb6c3b3a2a9af246a35bc5d3bd42cd8f42f3/Trackman_Code/code/Trackman_code.py)

---

## ⚾ Features of the Project  
📝 Description: The program starts by looking for a roster of baseball players. The roster correlates to the players that will be found in the csvs. 
![roster lookup](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120018.png)

Next, the program ask the user if they want to look at a season, just one game, or stop the program. At any point the user can click the stop button 
and close the program down.
![season or game](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120033.png)

If the user clicks season, the program open new window with the following layout.
![season screen](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07130824.png)
If the user clicks the add button, the program will open a folder window and look for Trackman csvs. The user can input as many Trackman CSVs as they want. When the user has put enough Trackman CSVs into the program, the user can click Analyze to analyze the CSVs. At any point, the user can click stop to shut down the season mode of the program. 

If the user clicks game, the window will be the same except the user only needs to put in one Trackman CSV. 

Once the Trackman CSV(s) has been loaded and the user clicks analyze, the following screen will appear

![filter_screen](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120124.png)
This window is for the filters. The user can click on words in the scroll boxes and the word options appear on the boxes to the left. 
The filters are used to sort data in the Trackman CSVs. 
The user can ONLY look at 1 player at a time. 
The user can look at a pitcher's or a batter's statistics by clicking on the respected buttons. 
When the user clicks "Batter" or "Pitcher", it will produce a graph and another window as shown below. 
![Print Graph](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120156.png)
This window asks if the user wants the graph to be printed. If the user clicks yes, the program can print the graph. If the user clicks no, the window will close. 
![Player Graph](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120211.png)
The graph contains a key on the right and the dots represent the pitches thrown or seen by a batter. 
The user can hover over a pitch to see the pitch description. 
![Pitch_hover](https://github.com/HowdenFr/HowdenFr.github.io/blob/ed6bd8850e8fd5dc68bf12e1960855fd56ca26cc/Trackman_Code/img/Screenshot2025-11-07120221.png)

If the user puts in filters which don't find any data, a box Selection Error window will appear. 
![selection_error](https://github.com/HowdenFr/HowdenFr.github.io/blob/0ecaa159e2476723ffdb90f1220367c0dd8cba1e/Trackman_Code/img/Screenshot2025-11-07120131.png)

As stated above, the program closes when the user clicks the "Stop button" on the window which asks for season or game analysis. 




