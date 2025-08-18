"""
Code is for Cat Stats Baseball. 
The program is made to grab any trackman game and produce 
data analysis displays for coaches and players. 
Much Thanks to Chat GPT, Professor Katy Williams, Aidan Wirshing, 
and .... 
Okay, let's go.
"""

import os
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.filedialog import askopenfilename
import mplcursors


#select the txt file using tkinter

def select_file_txt():
    """
    Function which finds the game csv.
    Parameters: none
    returns: the file_path to the csv which is basically the csv
    """
    file_path=askopenfilename(filetypes=[("Text files","*.txt")]) #parameters that force the user to find .txt.
    #if you add an s to askopenfilename, you can select multiple files
    return file_path

    
#select the CSV file using tkinter
def select_file_csv():
    """
    Function which finds the game csv.
    Parameters: none
    returns: the file_path to the csv which is basically the csv
    """
    
    file_path=askopenfilename(filetypes=[("CSV files", "*.csv")]) #parameters that force the user to find csv.
    #if you add an s to askopenfilename, you can select multiple files
    return file_path

#check the CSV file.
def check_file(file_path):
    """
    Function which checks the csv if it is a csv
    Parameters: file_path. the path to the csv, which is basically the csv object
    returns: nothing 
    
    """
    
    if file_path:
        print(f"loaded data from: {file_path}")
        return True
        
    else:
        print("No file selected.")
        return False
    
#get the roster of davidosn baseball
def player_search(file_path):
        """
        Creates the textbox for the player submission.
        This will be used a lot. 
        Parameters: currentWindow, the window being used 
        Returns: text_data: the data of players
                 result_data: the data returned by the search
                player_entry: the entry that you type to search the player
        """
    
        players=[]
        with open(file_path,'r')as file:
            lines=file.readlines()
        
            for line in lines:
                elements=line.split('\n')
                players.append(elements[0])
        return players

#build the page which will filter through the page. 
def listbox_filler(listbox,options):
    """
    function which adds in the options per list box
    Helper function
    Parameters: listbox. the list box that will have options inserted
                Options: the options for the listbox. 
    Returns: the list box
    
    """
    for option in options:
        listbox.insert(tk.END,option)
    return listbox

# Function to update Text widget based on Listbox selection
def update_text(event, listbox, text_widget):

    selected_indices = listbox.curselection()  # Get selected indices
    selected_items = [listbox.get(i) for i in selected_indices]  # Get selected items
    
    # Get the current selections in the Text widget
    current_text = text_widget.get(1.0, tk.END).strip()  # Get current text, remove trailing newline
    
    # Append the new selected items to the current content (without duplicates)
    new_items = [item for item in selected_items if item not in current_text]
    if new_items:
        text_widget.delete(1.0, tk.END)  # Clear the Text widget
        updated_text = current_text + "\n" + "\n".join(new_items) if current_text else "\n".join(new_items)
        
        text_widget.insert(tk.END, updated_text)  # Insert updated selections


# Function to create a Listbox and Text widget pair
# Function to create a Listbox and Text widget pair
def create_filter(window, options, label_text, x, y):

    label = tk.Label(window, text=label_text)
    label.place(x=x, y=y - 30)

    # Listbox
    listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, height=6, width=15)
    listbox.place(x=x, y=y)
    for option in options:
        listbox.insert(tk.END, option)

    # Text widget
    text_widget = tk.Text(window, height=6, width=15)
    text_widget.place(x=x + 100, y=y)

    # Bind Listbox selection to update_text
    listbox.bind("<<ListboxSelect>>", lambda event: update_text(event, listbox, text_widget))

    return listbox, text_widget

# get keywords from filter
def get_data(textbox):
    """
    function which get's the filters 
    Parameters: textbox: the text box wit filters.
    Returns: nothing
    """
    #get the filters
    # Retrieve all text
    text = textbox.get("1.0", "end").strip()
    
    # Split by spaces instead of commas
    keywords = [word for word in text.split() if word]
    return keywords

#player filtering
def player_filter(player_count):
    """
    function which gives the players. 
    Parameters: player_count: the players in the count
    Returns: the players that the user wants to look at. 
    """
    players_name=player_count.get("1.0", "end").strip()
    
    
    # Split by spaces instead of commas
    keywords = [word for word in players_name.split("\n") if word]
    names=[]
    for i in keywords:
        name_to_break=i.split()
        new_name=name_to_break[2] + ", " + name_to_break[1]
        names.append(new_name)
    return names
       
#make the filter statement
def filter_data(data, pitch_thrown, pitch_call,ball_scenario, strike_scenario,player,inning_scenario,choice):
    """
    function which makes the filter statement for the data
    Parameters:
                data: the csv
                pitch_throw: the pitch thrown filter results
                pitch_call: the pitch call filter results
                ball_scenario: what the ball scenario the user want's to see
                strike_scenario: what the strike scenario the user want's to see
                players the player the user want's to see
                inning: the innings the user want to see. 
    Returns: the filter conditions statement
    
    """
    # Build filter conditions dynamically
    conditions = []
    if(choice==0):
        conditions.append(data["Batter"].isin(player))
    else:
        conditions.append(data["Pitcher"].isin(player))

    # Check each filter and add conditions
    if pitch_thrown is not None:
        conditions.append(data["TaggedPitchType"].isin(pitch_thrown))
    if pitch_call is not None:
        conditions.append(data["PitchCall"].isin(pitch_call))
    if ball_scenario is not None:
        ball_scenario=[int(i) for i in ball_scenario]
        conditions.append(data["Balls"].isin(ball_scenario))
    if strike_scenario is not None:
        strike_scenario=[int(i) for i in strike_scenario] #convert to integers
        conditions.append(data["Strikes"].isin(strike_scenario))
    if inning_scenario is not None:
        # Convert valid numeric inputs to integers, ignoring "Extra"
        inning_values = [int(i) for i in inning_scenario if i.isdigit()]
        
        # If "Extra" is in the input, add a condition for innings > 9
        if "Extra" in inning_scenario:
            conditions.append((data["Inning"] > 9) | (data["Inning"].isin(inning_values)))
        else:
            conditions.append(data["Inning"].isin(inning_values))
            

    # Combine all conditions (AND operation)
    #that's the name
    filtered_df=None
    final_condition = conditions[0]
    
    if(len(conditions)>1):
        for condition in conditions[1:]:
            final_condition &= condition
        
        filtered_df =data[final_condition]
    else: 
        filtered_df=data[final_condition]

    
    return filtered_df

#calculate batter statistics part 1
def calculate_batter_swings(swing_data):
    """
    function which takes in an array of data and calculates the whiff, chasing, 
    in-zone swing miss%
    Parameters: swing_data: an array of the data to calculate the whiff, chasing, in=zone
    swing miss%
    Returns: chase, swing_miss, in-zone
    """
    whiff=0
    chase=0
    in_zone_whiff=0
    total_swings=0
    strikes=0
    pitches=0
    
    
    #adding up swings taken and what type they were. 
    for i in swing_data:
        pitches+=1
        if(i[2]!='BallCalled'):
            
            strikes+=1

        if (i[2]=='StrikeSwinging' or i[2]=='FoulBallNotFieldable' or i[2]== 'FoulBallFieldable'
        or i[2]=='InPlay'):
            total_swings +=1
            if(i[2]=='StrikeSwinging'):
                whiff+=1
            if((i[0]<=1.50000 or i[0]>=3.50000) or (i[1]<=-0.90000 or i[1]>=0.90000)):
                chase +=1
            else:
                in_zone_whiff+=1
        else:
            continue
    #recalculate percentage with total_swings and pitches therefore making them percentages. 
    if (total_swings==0):
        whiff=0
        in_zone_whiff=0
        chase=0
        strikes=0
    else:
        whiff=(whiff/total_swings) *100
        in_zone_whiff=(in_zone_whiff/total_swings) * 100
        chase=(chase/total_swings) * 100
        strikes=(strikes/pitches) * 100

    #make the string for the graph/figure. 
    stats_text=(f"Whiff: {whiff:.3f}%\n"
        f"in_zone_whiff: {in_zone_whiff:.3f}%\n"
        f"chase: {chase:.3f}%\n"
        f"Strike: {strikes:.3f}%"
        )
    
    return stats_text





#calculate batters statistics:
def calculate_batter(calculating_data,choice):
    """
    function which takes in what happened to the at bats and derives batting statistics
    Parameters: calculcating_data: a list which has all the results of each pitch
    Returns: OBP: On base percentage
             Slugging: slugging percentage
             BA: batting average
    """
    #all the things a user needs to calculate stats. 
    OnBasePer=0
    Slugging=0
    BatAvg=0
    Singles=0
    double=0
    triples=0
    homeruns=0
    sacrifice=0
    hits=0
    atBats=0
    walks=0
    strikeouts=0
    hitByPitch=0

    #sorting through the data to get the calculations
    for data in calculating_data:
        pitch=data[0]
        playResult=data[1]
        pitchCall=data[2]
        if(pitch=='Strikeout'):
            atBats+=1
            strikeouts+=1
        if(pitch=='Walk'):
            atBats+=1
            walks+=1
        if(playResult=='Single'):
            Singles+=1
            atBats+=1
            hits+=1
        if(playResult=='Double'):
            double+=1
            atBats+=1
            hits+=1
        if(playResult=='Triple'):
            triples+=1
            atBats+=1
            hits+=1
        if(playResult=='HomeRun'):
            homeruns+=1
            atBats+=1
            hits+=1
        if(playResult=='Sacrifice'):
            sacrifice+=1
            atBats+=1
        if(playResult=='Out'):
            atBats+=1
        if(pitchCall=='HitByPitch'):
            atBats+=1
            hitByPitch+=1
    
    
    #the calculations
    if(atBats==0):
        BatAvg=0
        Slugging=0
        OnBasePer=0
    else:
        BatAvg=hits/atBats
        Slugging=(Singles + (2* double)+ (3*triples) + (4*homeruns))/atBats
        OnBasePer=(hits + walks + hitByPitch)/(atBats +walks + hitByPitch +sacrifice)

    if(choice==0):
        return BatAvg,Slugging,OnBasePer
    else:
        return BatAvg,strikeouts,hits,walks

#start the calculations for either pitcher or batter:
def calculations(calculating_data,choice):
    """
    defintion which calculates the pitcher and batter
    Parameters: calculating_data. the calculating data
                choice: 0 if it's batter
                        1 if it's a pitcher

    Returns: the stats_text
    """
    stats_text=None
    batAvg=None
    Slugging=None
    OnBasePer=None
    Strikeouts=None
    Walks=None
    hits=None
    #on the side text.
    # Create stats text
    #calculate stats:
    if(choice==0):
        batAvg,Slugging,OnBasePer=calculate_batter(calculating_data,choice)
        stats_text = (
        f"OBP: {OnBasePer:.3f}%\n"
        f"BA: {batAvg:.3f}\n"
        f"Slugging: {Slugging:.3f}%"
        )
    else:
        batAvg, Strikeouts,hits,Walks=calculate_batter(calculating_data,choice)
        stats_text=(f"BA: {batAvg:.3f}\n"
        f"SOs: {Strikeouts:.3f}\n"
        f"Hits: {hits:.3f}\n"
        f"Ws:{Walks:.3f}"
        )
    return stats_text

def on_yes(name,root,fig,result):
        file_name=name+"pitch chart.png"
        result = 0  # Set the return value for "Yes"
        
        fig.savefig(file_name)  # Save the figure as an image. Must do it 
        # Use OS-specific print command
       
        os.startfile(file_name, "print")
        root.destroy()
        return result

def on_no(root,figure,result):
    result=1
    root.destroy()
    return result

#print the grid if the user wants to 
def print_graph(name,figure, axis):
    """
    function which puts the user to decide whether to print the grid or not
    Parameters: figure: the figure
                axis: the axis on the figure
    Returns: 1 if the user doesn't want it printed
             0 if the user does want it printed
    
    """
    result=None
    root=tk.Tk()
    root.title("Print")
    root.geometry("300x300")
    instructions=tk.Label(root, text="Do you want to print?", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1)
    instructions.place(x=0,y=0)
    yes_button=tk.Button(root,text="Yes", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1,command=lambda:on_yes(name,root,figure,result) )
    yes_button.place(x=0,y=200)

    no_button=tk.Button(root,text="No", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1,command=lambda:on_no(root,figure,result))

    no_button.place(x=100, y=200)
    return result




#start the matplot lib process
def start_graph(refined_data,choice):
    """
    function which takes in the refined_data and will start the graph process
    Parameters: data: the player csv that is looking at
    Returns: ?
    
    """
    
    #extract the position of each pitch and type
    data_as_list=[]
    calculating_data=[]
    graph_data=[]
    swing_data=[]
    player=''
    if choice==0:
        player='Batter'
    else:
        player='Pitcher'

    for _, row in refined_data.iterrows():
        data_as_list.append([row['PlateLocHeight'],row['PlateLocSide'],row['TaggedPitchType']])
        calculating_data.append([row['KorBB'],row['PlayResult'],row['PitchCall']])
        graph_data.append([row[player],row['ZoneSpeed'],row['Inning'],row['Top/Bottom'],row['Outs'],row['Balls'],row['Strikes'],row['VertBreak'],row['HorzBreak'],row['SpinRate'],row['PlayResult'],row['PitchCall'],row['ExitSpeed'], row['Angle']])
        
        swing_data.append([row['PlateLocHeight'],row['PlateLocSide'],row['PitchCall']])
      
        
                    #print(data_as_list)
    #all the other data of a pitch
    
    if(len(data_as_list)==0):
        messagebox.showerror("Selection Error","Player Has No Stats.")
        return
    
    #the rest is from ChatGPT
    # Define Strike Zone Dimensions
    strike_zone_top = 3.5
    strike_zone_bottom = 1.5
    strike_zone_left = -0.9
    strike_zone_right = 0.9

    #the pitch colors
    pitch_colors = {
    "Fastball": "red",
    "Curveball": "blue",
    "Slider": "green",
    "ChangeUp": "purple",
    "Sinker": "black",
    "Splitter":"orange",
    "Slurve":"yellow",
    "Screw": "pink"}

    x_coords=[]
    y_coords=[]
    pitch_types=[]
    additional_data=[]
    
    for i in range(len(data_as_list)):
        y_coords.append(data_as_list[i][0])
        x_coords.append(data_as_list[i][1])
        pitch_types.append(data_as_list[i][2])
        additional_data.append(graph_data[i])

    
    #Assign Colors Based on Pitch Types
    colors=[pitch_colors[pitch_type] for pitch_type in pitch_types]

    #Create Plot
   
    manager = plt.get_current_fig_manager()
    
    #making the figure screen wide
    screen_dpi=plt.rcParams['figure.dpi']
    fig_width = manager.window.winfo_screenwidth() / screen_dpi
    fig_height= manager.window.winfo_screenheight() / screen_dpi

    plt.rcParams['figure.dpi']=screen_dpi
    fig,ax = plt.subplots(figsize=(fig_width,fig_height))
    

    # Plot Strike Zone
    ax.add_patch(
        plt.Rectangle(
            (strike_zone_left, strike_zone_bottom),  # Bottom-left corner
            strike_zone_right - strike_zone_left,   # Width
            strike_zone_top - strike_zone_bottom,   # Height
            fill=False, edgecolor="black", linewidth=2, linestyle="--", label="Strike Zone"
        )
    )

    

    # Plot Pitches
    scatter = ax.scatter(x_coords, y_coords, c=colors, edgecolors="black", s=50, alpha=0.8, label="Pitches")

    # Add Legend
    legend_labels = list(pitch_colors.keys())
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=pitch_colors[p], markersize=10) for p in legend_labels]
    ax.legend(legend_handles, legend_labels, loc="upper right", title="Pitch Types")

    # Add Labels and Title
    #making the title correct based on what the user wants. 
    player_type=""
    if (choice==0):
        player_type=" Batting"
    else:
        player_type=" Pitching"
    #if a player has no data, then the program won't print anything. Have to catch this!!!
   
    name=str(graph_data[0][0])
    
    ax.set_title(name + player_type,fontsize=14)
    ax.set_xlabel("Horizontal Location (ft)", fontsize=12)
    ax.set_ylabel("Vertical Location (ft)", fontsize=12)

    # Set Axes Limits to Frame Strike Zone
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0, 5.0)
    ax.set_aspect('equal',adjustable='box')
    

    #on the side text.
    # Create stats text
    #calculate stats:
    
    stats_text = calculations(calculating_data,choice)
    swing_stats= calculate_batter_swings(swing_data)
    
    # Add the stats_text to the top left of the data
    #this is the ops, ba, slugging
    ax.text(
        2.7, 4.5,  # Adjust x, y to position text to the side
        stats_text,
        fontsize=10,
        verticalalignment='top',  # Align to top of the text box
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='black')  # Optional: Add a background box
    )
    # add the swing_stats to the top left of the data
    #this is the whiff, strikes, in_zone, chase%
    ax.text(
        -4.2,4.5,
        swing_stats,
        fontsize=10, 
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='black')
    )

    ax.text(
        -4.2,3.0,
        "Parameters: \n Pitch Type \n Player Name \n Speed \n Inning \n Top/Bottom \n Outs \n Balls \n Strikes \n Vertical Break \n Horizontal Break \n Spin Rate \n Play Result \n Pitch Call \n Exit Speed \n Angle",
        fontsize=10,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='black')
    )
    

    # Add Interactive Tooltips
    cursor = mplcursors.cursor(scatter, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        # Add custom text to tooltip
        index = sel.index
        tooltip_text = f"{pitch_types[index]}\n" + "\n".join(str(value) for value in additional_data[index])
        sel.annotation.set_text(tooltip_text)

    
    # Display Plot
    plt.grid(True, linestyle="--", alpha=1.0)
    #user selects if they want to print out the grid or not. 
    print_graph(name,fig,ax)
    
    plt.show(block=True)
    plt.close('all')
        




#start filtering
def csv_reading(data,pitch_type,pitch_result,ball_count,strike_count,player_count,inning,choice):
    """
    function which reads through the csv with the filters. 
    Parameters: data: the csv
                pitch_type: the pitch type filter results
                pitch_result: the pitch result filter
                ball_count: what the ball count the user want's to see
                strike_count: what the strike count the user want's to see
                player_count: the player the person want's to se
                inning: the inning the coaches want to see. 
    Returns: Nothing?
    """
    pitch_thrown=get_data(pitch_type)
    pitch_call=get_data(pitch_result)
    ball_scenario=get_data(ball_count)
    strike_scenario=get_data(strike_count)
    inning_scenario=get_data(inning)
    players=player_filter(player_count)
    
    if (len(players)==0 or len(players)>1) :
        messagebox.showerror("Selection Error","Please select A player.")
        return
    else:
        name=players[0]
    if("BreakingBalls" in pitch_thrown):
        breaking_balls=["Curveball","Slider","Sinker","Slurve"]
        for i in breaking_balls:
            if i not in pitch_thrown:
                pitch_thrown.append(i)
            else:
                continue
    
    if(len(pitch_thrown)==0):
        pitch_thrown=None
    if(len(pitch_call)==0):
        pitch_call=None
    if(len(ball_scenario)==0):
        ball_scenario=None
    if(len(strike_scenario)==0):
        strike_scenario=None
    if(len(inning_scenario)==0):
        inning_scenario=None
    
    datas=filter_data(data,pitch_thrown,pitch_call,ball_scenario, strike_scenario,players,inning_scenario,choice)
    
    #making the specific columns to look at. Literally it's either looking at a batter or pitcher. 
    batter_specific_columns=['Batter','PitchNo','Inning', 'Top/Bottom','Outs','Balls','Strikes','TaggedPitchType','PitchCall', 'KorBB','PlayResult','OutsOnPlay','RunsScored',
    'VertBreak','HorzBreak', 'SpinRate','PlateLocHeight','PlateLocSide','ZoneSpeed','ExitSpeed','Distance','HangTime', 'Angle']
    pitcher_specific_columns=['Pitcher','PitchNo','Inning', 'Top/Bottom','Outs','Balls','Strikes','TaggedPitchType','PitchCall','KorBB','PlayResult','OutsOnPlay','RunsScored',
    'VertBreak','HorzBreak', 'SpinRate','PlateLocHeight','PlateLocSide','ZoneSpeed','ExitSpeed','Distance','HangTime', 'Angle']
    correct_data=0
    #make the correct data based on the choices. 
    if(choice==0):
        correct_data=datas[batter_specific_columns].fillna("No Hit")
    else:
        correct_data=datas[pitcher_specific_columns].fillna("No Hit")
    start_graph(correct_data,choice)
    



# Main window setup
def start_filter(data,main_window,roster):
    """
    function which is the selection for the user to see the pitching chart. 
    Set's up the screen for the user. 
    Parameters: data: the csv that holds the game. 
                window: the original window they came from
    Returns: nothing
    """
    window = tk.Toplevel(main_window)
    window.title("Multiple Listbox and Text Example")
    window.geometry("1000x600")

    # Create Listbox-Text pairs
    Pitch_type_listbox,pitch_type_text=create_filter(window, 
                  ["Fastball", "Curveball", "Slider", "ChangeUp","Sinker","Splitter","Slurve","Screw","BreakingBalls"], 
                  "Pitch Type:", 
                  50, 100)
    Pitch_Result_listbox,pitch_Result_text=create_filter(window, 
                  ["StrikeCall", "StrikeSwinging", "BallCalled", "FoulBallNotFieldable","HitchByPitch","FoulBallFieldable", "InPlay"], 
                  "Pitch Results:", 
                  50, 300)
    Ball_Count_listbox,Ball_Count_text=create_filter(window, 
                  ["0", "1", "2", "3"], 
                  "Ball Count:", 
                  350, 100,)
    Strike_Count_listbox,Strike_Count_text=create_filter(window, 
                  ["0", "1", "2"], 
                  "Strike Count:", 
                  350, 300)
    Player_listbox,Player_text=create_filter(window, player_search(roster),"Player:",650,100)
    Inning_listbox,Inning_text=create_filter(window,
    ["1","2","3","4","5","6","7","8","9","Extra"],"Inning",650,300)

    batter_button=tk.Button(window,text="BATTER", font=("Arial",40), fg="Red", background="Black" ,borderwidth=1,command=lambda: csv_reading(data,pitch_type_text,pitch_Result_text,Ball_Count_text
                                                                                                                                        ,Strike_Count_text,Player_text,Inning_text,0) )
    batter_button.place(x=0,y=400)

    pitcher_button=tk.Button(window,text="PITCHER", font=("Arial",40), fg="Red", background="Black" ,borderwidth=1,command=lambda: csv_reading(data,pitch_type_text,pitch_Result_text,Ball_Count_text
                                                                                                                                        ,Strike_Count_text,Player_text,Inning_text,1) )
    pitcher_button.place(x=400,y=400)

    end_button=tk.Button(window,text="END", font=("Arial",40), fg="Red", background="Black" ,borderwidth=1,command=lambda:window.destroy() )
    end_button.place(x=800,y=400)



   

def add_onto_season(window):
    """
    program which adds onto the season total 
    Parameters: window. the window it came from. 
    Returns: nothing
    """
    season_file=None
    game_to_add=None

    #files to be read
    season_file=select_file_csv()
    game_to_add=select_file_csv()

    #if the files haven't been added to each other check

    #add the files together
    game=pd.read_csv(game_to_add)
    # Check if the target CSV exists and is blank
    if not os.path.exists(season_file) and os.stat(season_file).st_size == 0:
    # Write the source data to the target file (with headers)
        game.to_csv(season_file, index=False, mode='w', header=True)
        
    else:
    # Append the source data to the target file (without headers)
        game.to_csv(season_file, index=False, mode='a', header=False)
    

   
def season_program(main_window,roster):
    """
    Function which runs the season part of the program. 
    There are a few steps that need to happen in order to get to the visual display
    Parameters: window the original window
    Returns: nothing
    """
    window=tk.Toplevel(main_window)
    window.title("Season Program")
    window.geometry("500x500")

    directions=tk.Label(window,text="Add onto Season or Analyze", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
    directions.pack()

    add_button=tk.Button(window,text="Add", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1, command=lambda: add_onto_season(window) )
    add_button.place(x=50,y=100)

    Analyze_button=tk.Button(window,text="Analyze", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1,command=lambda: game_program(main_window,roster))
    Analyze_button.place(x=250,y=100)

    stop_program=tk.Button(window,text="Stop", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1,command=lambda: window.destroy())
    stop_program.place(x=200,y=300)

    








    

def game_program(window,roster):
    """
    Function which starts the game program for the Trackman analysis
    Parameters: window, the window you came from. 

    """
    file_path=select_file_csv() #this selects the file

    
    #file_path="Davidson Baseball Trackman CSV Example.csv"
    #if the file is not true, don't run program. 
    #if it is, run the program. Big if statement
    if(check_file(file_path)):
         #read in the data
        data=pd.read_csv(file_path)
       
        start_filter(data,window,roster)

    else:
        print("Program won't run")
        return False

def start_program():
    """
    Functon which starts the program. 
    Parameters: none
    Returns: none or the root. 
    
    """
    window = tk.Tk()
    window.title("Start Program")
    window.geometry("500x500")

    roster=select_file_txt()
    print(roster)


    directions=tk.Label(window,text="Season or One Game", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
    directions.pack()

    season_button=tk.Button(window,text="Season", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1, command=lambda: season_program(window,roster) )
    season_button.place(x=50,y=100)

    pitcher_button=tk.Button(window,text="Game", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1,command=lambda: game_program(window,roster))
    pitcher_button.place(x=250,y=100)

    stop_program=tk.Button(window,text="Stop", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1,command=lambda: window.destroy())
    stop_program.place(x=200,y=300)

    window.mainloop()


start_program()


    
#funtion which runs the program