"""
this is the program for the Field Hockey Penalty Corners look

Authors: Frank Howden and Chat GPT



"""

from csv import excel
import tkinter as tk
from tkinter import ACTIVE, END, ttk
from PIL import ImageTk, Image
from functools import partial
from FieldHockeyExcel import CreateStat

class App():

    def __init__(self):
        
        #total number of offense data needed per penalty corner
        self.offense_penalty_corner_length=22
        #this is the offense penalty corner count
        self.offense_penalty_corners=[[] for _ in range(self.offense_penalty_corner_length)]
        #making the offense penalty corner labels
        self.offense_penalty_corners_labels=[['Quarter'],['Time'],['Total'],['Earned'],['Redraw'],['Inserter'],['L'],['SS1'],['A'],['SS2'],['B'],['R'],['W'],['Initial'],['Execute Trap'],['Pass'],['Shot'],['Tip'],['Shot Go'],['Score'],['Who Scored?'],['Rebound']]
        
        #this is the array that keep tracks of the defense penalty corners
        self.defense_penalty_corners_length=21
        self.defense_penalty_corners=[[] for _ in range(self.defense_penalty_corners_length)]
        self.defense_penalty_corners_labels=[['Quarter'],['Time'],['Total'],['Caused'],['Redraw'],['RT'],['GK'],['Flier'],['LT'],['Post'],['Formation'],['Initial'],['Flier Make it to ball?'],['Flier Touch Ball?'],['Shot'],['Shot Go Initially'],['Who Blocked'],['Tip?'],['Who Tipped'],['Recorner'],['Score']]
        #this is the back page of the program. All windows will lay on top of this window
        #some of the other data for the game
        self.other_stats=[[]for _ in range(3)]
        
        self.offense_total=0
        self.defense_total=0
        self.root=self.start_program(self)

        #first we neeed to make the dimensions of the program the size for any screen

        self.root.mainloop()
    
    def insert_photo(window,string):
        """
        this is the command that creates an image on the screen

        string: the naem of the photo
        Returns: the image
        
        """
        image=Image.open(string)
        image=image.resize((250,250),Image.LANCZOS)
        photo=ImageTk.PhotoImage(image)
        image_label=tk.Label(window,image=photo)
        image_label.image=photo
        return image_label
    
    def new_stat(self,new_window, player_entry):
        """
        this is the command that renters the stats
        Parameters: window: the window that will be destroyed
                    player_entry: the entry that will be used
        Returns: nothing
        
        """
        
        self.query=player_entry.get()
        new_window.destroy()

    
    
    def stat_entry(self,entry, index, path):
        """
        this is the command that puts the player entry and puts them into the arrays

        Parameters: self: self
                    entry: the text entry
                    index: the index of where to put the entry into the array
                    path: whether we are inputting into the offense or defense
        Returns: nothing
        

        """
        query=entry.get()
        if(path==1):
            if(index>=13 and index<=21):
                if(len(self.offense_penalty_corners[index])==(self.offense_total)):
                    
                    self.offense_penalty_corners[index][self.offense_total-1]=query
                    
                else:
                    self.offense_penalty_corners[index].append(query)
            else:

                self.offense_penalty_corners[index].append(query)
        else:
            if(index>=14 and index<=21):
                if(len(self.defense_penalty_corners[index])==(self.defense_total)):
                    self.defense_penalty_corners[index][self.defense_total-1]=query
                else:
                    self.defense_penalty_corners[index].append(query)
            else:

                self.defense_penalty_corners[index].append(query)
            
            
    
        
   
    
    @staticmethod
    def search (entry, result_listbox, text_data):
        """
        this method is used to make the search box search while typing in the entry
        Parameters: player_entry: the player list
                    result_listbox: listbox that shows the results of the text
                    text_data: the listbox that has all the players names
        returns: Nothing
        """
        query=entry.get()
        result_listbox.delete(0,tk.END)
        for i in range(text_data.size()):
            if query.lower() in text_data.get(i).lower():
                result_listbox.insert(tk.END, text_data.get(i))
        return
    
    @staticmethod
    def on_select(entry, result_listbox):
        """
        this method on select puts the mouse select from the result box 
        into the entry
        Parameters: entry: the player entry
        result_listbox: the list box of the players after the search
        Parameters: Nothing

        """
        selected_item=result_listbox.get(result_listbox.curselection())
        entry.delete(0, tk.END)
        entry.insert(0,selected_item)

    
    @staticmethod
    def fixEntry(entry,text):
        """
        this method fixes an entry with the text given
        Parameter: entry: the entry we are trying to fix
                    text: the text we are inputting
        Returns: nothing

        
        """
        entry.delete(0,tk.END)
        entry.insert(0,text)
        return


    
    @staticmethod
    def player_search(currentWindow):
        """
        Creates the textbox for the player submission.
        This will be used a lot. 
        Parameters: currentWindow, the window being used 
        Returns: text_data: the data of players
                 result_data: the data returned by the search
                player_entry: the entry that you type to search the player
        """
        text_data=tk.Listbox(currentWindow, width=25, height=5)
        

        players=[]
        with open('Davidson Field Hockey Roster 2023-2024.txt','r')as file:
            lines=file.readlines()
        
            for line in lines:
                elements=line.split('\n')
                players.append(elements)
        for item in players:
            text_data.insert(tk.END, item[0])
        
        player_entry=tk.Entry(currentWindow, width=25)
        result_listbox=tk.Listbox(currentWindow, width=25, height=5)
        player_entry.bind("<KeyRelease>", lambda event: App.search( player_entry, result_listbox, text_data))
        result_listbox.bind("<ButtonRelease-1>", lambda event: App.on_select(player_entry, result_listbox))
        return text_data,result_listbox, player_entry
    
    def insert_scorer(self,oldWindow, scored_entry,screen):
        """this method is a bridge that insertes the scorer into the data set 

            oldWindow: this is the scored window that we are putting the widget over
            scored_entry: the person who scored
            screen: the screen that will be deleted

            Returns: nothing

        
        """
        screen.destroy()
        self.stat_entry(scored_entry,20,1)
        oldWindow.destroy()
        
        

    def pop_up_screen_3(self,oldWindow, scored_entry):
        """this method creates the widget that confirms the user is ready to move forward
        Parameters:

            oldWindow: this is the scored window that we are putting the widget over
            scored_entry: the person who scored

            Returns: nothing

        
        """

        screen=tk.Toplevel(oldWindow)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Scorer Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.insert_scorer(oldWindow, scored_entry,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)



    
    def scored(self,original_window,score_entry):
        """this method creates the widgets for who scored the goal
        Parameters: original_window: this is the shot_chart window
                    score_entry: the score_entry from the shot_chart window
        Returns: nothing
        """
        App.fixEntry(score_entry,'Y')
        newWindow=tk.Toplevel(original_window)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Shot: Offense")
        instructions=tk.Label(newWindow, text='Enter who scored',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=700, y=10)

         #the inserter_entry
        score_data,score_listbox,score_entry=App.player_search(newWindow)
        score_label=tk.Label(newWindow, text='Enter Scorer', font=("Arial",30), fg='Black', background='Red')
        score_label.place(x=50, y=0)
        score_entry.place(x=50, y=120,)
        score_data.place(x=50, y=150)
        score_listbox.place(x=50, y=250)

        back_button=tk.Button(newWindow,text='Back', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:newWindow.destroy())
        
        back_button.place(x=10, y=550)

        submit_label=tk.Label(newWindow,text='Ready to Submit?', background='Black', fg='Red', font=("Arial",30))
        submit_label.place(x=500,y=300)
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",30), fg='Black', background='Red',command=lambda: self.pop_up_screen_3(newWindow,score_entry))
        submit_button.place(x=500, y=400)

        
        return
    

    def insert_shot_stat(self,tip_entry,ball_location,score_entry,oldWindow,screen):
        """
        this is the method to insert the shot on offense
        Parameters self: 
                    tip_entry: tip_entry. 
                    ball_location: ball_location, where the shot went initially
                    score_entry: score entry. whether we socred or not

        """
        screen.destroy()
        score=score_entry.get()
        if(score=='N' or score=='Recorner'):
            self.stat_entry(score_entry,20,1)
        
        self.stat_entry(tip_entry,17,1)
        self.stat_entry(ball_location,18,1)
        self.stat_entry(score_entry,19,1)
        oldWindow.destroy()
        return


    def pop_up_screen_4(self,tip_entry,ball_location,score_entry,oldWindow):

        """this method creates the widget that confirms the user is ready to move forward
        Parameters:

            oldWindow: this is the scored window that we are putting the widget over
            tip_entry: the is the tip entry
            ball_location: the entry of where the ball was shot initially
            score_entry: the entry if there was a score or not

            Returns: nothing

        
        """

        screen=tk.Toplevel(oldWindow)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Is the Shot Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.insert_shot_stat(tip_entry,ball_location,score_entry,oldWindow,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)



    
    
    
    def shot_chart(self,original_window, shot_entry):
        """this method creates the widges for shot input
        Parameters: original_window: this is penalty corner what happened window.
        Returns: nothing
        


        """
        App.fixEntry(shot_entry,'Y')
        newWindow=tk.Toplevel(original_window)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Shot: Defense")
        instructions=tk.Label(newWindow, text='Enter all the inputs \n from the penalty corner shot',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=700, y=10)

        #tip entry
        tip_label=tk.Label(newWindow,text='Was there a tip?', background='Black', fg='Red', font=("Arial",12))
        tip_label.place(x=10,y=10)
         
        tip_entry=tk.Entry(newWindow,width=20)
        tip_entry.place(x=50,y=60)

        #updating the ball entries

        tip_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(tip_entry,'Y'))
        tip_button.place(x=50, y=100)
        no_tip_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(tip_entry,'N'))

        no_tip_button.place(x=100, y=100)

        #where did the ball go

        ball_location_label=tk.Label(newWindow,text='Where did the shot go initially?', background='Black', fg='Red', font=("Arial",12))
        ball_location_label.place(x=250,y=10)
         
        ball_location_entry=tk.Entry(newWindow,width=20)
        ball_location_entry.place(x=250,y=60)

        #updating the ball entries

        right_button=tk.Button(newWindow,text='R of GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'R of GK'))
        right_button.place(x=250, y=100)
        left_button=tk.Button(newWindow,text='L of GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'L of Gk'))
        left_button.place(x=400, y=100)
        at_button=tk.Button(newWindow,text='at GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'at GK'))
        at_button.place(x=250, y=225)
        blocked_button=tk.Button(newWindow,text='Blocked', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'Blocked'))
        blocked_button.place(x=400, y=225)


        #Score
        score_label=tk.Label(newWindow,text='Did we score?', background='Black', fg='Red', font=("Arial",12))
        score_label.place(x=10,y=250)
        score_entry=tk.Entry(newWindow,width=20)
        score_entry.place(x=50,y=300)
        score_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',command=lambda: self.scored(newWindow,score_entry))
        score_button.place(x=50, y=350)
        no_score_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(score_entry,'N'))
        recorner_button=tk.Button(newWindow,text='Recorner', font=("Arial",20), fg='Black', background='Red',command=lambda: App.fixEntry(score_entry,'Recorner'))
        recorner_button.place(x=150, y=350)

        no_score_button.place(x=100, y=350)

        back_button=tk.Button(newWindow,text='Back', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:newWindow.destroy())
        
        back_button.place(x=10, y=550)

        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:self.pop_up_screen_4(tip_entry,ball_location_entry,score_entry,newWindow))
        
        submit_button.place(x=500, y=550)


    
    def insert_blocked_stat(self,blocked_entry, old_window, screen, choice):
        """
        inserts the blocked stat into the data
        Parameters: 
                    blocked_entry: the player who blocked the shot
                    old_window: the blocked shot window
                    screen: the former pop up screen (pop up screen_8)
                    schoice: if 1, then that menas we are inserting who blocked the shot
                            if 2, then that means we are inserting who tipped the shot
        Returns nothing
        
        """
        screen.destroy()
        if(choice==1):

            self.stat_entry(blocked_entry,16,0)
        if(choice==2):
            self.stat_entry(blocked_entry,18,0)
            
        old_window.destroy()


    def pop_up_screen_8(self,old_window,blocked_entry,choice):
        """
        pop up screen for the blocked shot to confirm if the user has everything
        Parameters: old_window: the window that was the blocked shot
                    blocked_entry: the entry of the player who blocked the shot
                    choice: if choice is 1, then 
        Returns: nothing
        """
        screen=tk.Toplevel(old_window)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Is the Shot Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.insert_blocked_stat(blocked_entry,old_window,screen,choice))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)



    def blocked_chart(self, original_window,ball_entry,tip_entry):
        """This is the widget that is made for the bloced shot
            Parameters: 
                self: self
                original_window: the window that was the defnese_shot_chart
                ball_entry, where the ball went
        
        """
        App.fixEntry(ball_entry, 'Blocked')
        App.fixEntry(tip_entry,"N")
        
        newWindow=tk.Toplevel(original_window)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Blocked: Defense")
        instructions=tk.Label(newWindow, text='Enter who blocked shot',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=700, y=10)

        #the blocked_entry
        score_data,score_listbox,score_entry=App.player_search(newWindow)
        score_label=tk.Label(newWindow, text='Enter Player', font=("Arial",30), fg='Black', background='Red')
        score_label.place(x=50, y=0)
        score_entry.place(x=50, y=120,)
        score_data.place(x=50, y=150)
        score_listbox.place(x=50, y=250)

        back_button=tk.Button(newWindow,text='Back', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:newWindow.destroy())
        
        back_button.place(x=10, y=550)

        submit_label=tk.Label(newWindow,text='Ready to Submit?', background='Black', fg='Red', font=("Arial",30))
        submit_label.place(x=500,y=300)
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",30), fg='Black', background='Red',command=lambda: self.pop_up_screen_8(newWindow,score_entry,1))
        submit_button.place(x=500, y=400)

        
        return
    
    def tip_chart(self,oldWindow,tip_entry):
        """This is the widget that is made for the bloced shot
            Parameters: 
                self: self
                original_window: the window that was the defnese_shot_chart
                ball_entry, where the ball went
        
        """
        App.fixEntry(tip_entry, 'Y')
        
        newWindow=tk.Toplevel(oldWindow)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Tipped: Defense")
        instructions=tk.Label(newWindow, text='Enter who tipped shot',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=700, y=10)

        #the blocked_entry
        score_data,score_listbox,score_entry=App.player_search(newWindow)
        score_label=tk.Label(newWindow, text='Enter Player', font=("Arial",30), fg='Black', background='Red')
        score_label.place(x=50, y=0)
        score_entry.place(x=50, y=120,)
        score_data.place(x=50, y=150)
        score_listbox.place(x=50, y=250)

        back_button=tk.Button(newWindow,text='Back', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:newWindow.destroy())
        
        back_button.place(x=10, y=550)

        submit_label=tk.Label(newWindow,text='Ready to Submit?', background='Black', fg='Red', font=("Arial",30))
        submit_label.place(x=500,y=300)
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",30), fg='Black', background='Red',command=lambda: self.pop_up_screen_8(newWindow,tip_entry,2))
        submit_button.place(x=500, y=400)

        
        return
    
    def insert_defense_shot(self,shot_entry,tip_entry,score_entry,old_window,screen):
            """this method enters what happened with the shot entries
                Parameters: self: self
                            shot_entry: the entry of the shot
                            tip_entry: the entry of the tip
                            score_entry: the entry of the score. wether the opponent scored on the goal or not
                            old_window: the window we were over. the defense_shot_chart
                            original_window: the offense or defense  
                            screen: the pop up screen 9
                returns: nothing

            
            """
            screen.destroy()
            shot=shot_entry.get()
            tip=tip_entry.get()
            score=score_entry.get()
            
            if(shot==''):
                App.fixEntry(shot_entry,'N')
            
            if(shot_entry.get()!='Blocked'):
                self.stat_entry(shot_entry,16,0)
                    
                
            if(tip=='N'or tip==''):
                if(tip==''):
                    App.fixEntry(tip_entry,'N')
                self.stat_entry(tip_entry,18,0)
                
            if(score==''):
                App.fixEntry(score_entry,'N')
            
            
            self.stat_entry(shot_entry,15,0 )
            self.stat_entry(tip_entry,17,0)
            self.stat_entry(score_entry,20,0)

            
            
            old_window.destroy()
            return
    
    def pop_up_screen_9(self,shot_entry,tip_entry,score_entry,old_window):
        """
        pop up screen for the blocked shot to confirm if the user has everything
        Parameters: old_window: the window that was the blocked shot
                    shot_entry: the entry of what happened to the shot
                    tip_entry: the entry of if there was a tip
                    old_window: the defense_shot_chart widget
                    orginal_window: the original widget

        Returns: nothing
        """
        screen=tk.Toplevel(old_window)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Is the Shot Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.insert_defense_shot(shot_entry, tip_entry, score_entry, old_window,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)




        
    
    def defense_shot_chart(self,original_window,shot_entry):
        """this method creates the widges for shot input
        Parameters: original_window: this is penalty corner what happened window.
        Returns: nothing
        


        """
        App.fixEntry(shot_entry,'Y')
        newWindow=tk.Toplevel(original_window)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Shot: Defense")
        instructions=tk.Label(newWindow, text='Enter all the inputs \n from the penalty corner shot',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=700, y=10)

        #where did the ball go

        ball_location_label=tk.Label(newWindow,text='Where did the shot go initially?', background='Black', fg='Red', font=("Arial",12))
        ball_location_label.place(x=50,y=10)
         
        ball_location_entry=tk.Entry(newWindow,width=20)
        ball_location_entry.place(x=50,y=60)

        #updating the ball entries

        right_button=tk.Button(newWindow,text='R of GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'R of GK'))
        right_button.place(x=50, y=100)
        left_button=tk.Button(newWindow,text='L of GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'L of Gk'))
        left_button.place(x=200, y=100)
        at_button=tk.Button(newWindow,text='at GK', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_location_entry,'at GK'))
        at_button.place(x=50, y=225)
        blocked_button=tk.Button(newWindow,text='Blocked', font=("Arial",20), fg='Black', background='Red',  command=lambda: self.blocked_chart(newWindow,ball_location_entry,tip_entry))
        blocked_button.place(x=200, y=225)

        #was there a tip
        tip_entry=tk.Entry(newWindow, width=20)
        tip_entry.place(x=400,y=60)
        tip_label=tk.Label(newWindow,text='Was there a tip?', background='Black', fg='Red', font=("Arial",12))
        tip_label.place(x=400,y=10)
        tip_button=tk.Button(newWindow,text='Yes', font=("Arial",20), fg='Black', background='Red',  command=lambda: self.tip_chart(newWindow,tip_entry))
        tip_button.place(x=450, y=100)
        no_tip_button=tk.Button(newWindow,text='No', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(tip_entry,'N'))
        no_tip_button.place(x=400, y=100)

        
        #was there score
        score_entry=tk.Entry(newWindow, width=20)
        score_entry.place(x=50,y=450)
        score_label=tk.Label(newWindow,text='Did They Score?', background='Black', fg='Red', font=("Arial",12))
        score_label.place(x=50,y=400)
        score_button=tk.Button(newWindow,text='Yes', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(score_entry,'Y'))
        score_button.place(x=50, y=500)
        no_score_button=tk.Button(newWindow,text='N0', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(score_entry,'N'))
        no_score_button.place(x=150, y=500)

        #submit button
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",40), fg='Black', background='Red', command=lambda:self.pop_up_screen_9(shot_entry,tip_entry,score_entry,newWindow))
        submit_button.place(x=600, y=500)








    def penalty_corner_insert(self,ball_entry,trap_entry, pass_entry, shot_entry, rebound_entry,oldWindow, original_window, screen):
        """
        This method inserts the data for the shot entry for offense
        Parameters: self: self
                    ball_entry: the entry of wher ethe ball went
                trap_entry: the entry of if we made a trap
                pass_entry: the entry if we passed or not
                shot_entry: the entry of if there was a shot
                oldWindow: the window the was the penalty_corner_offense
                screen: the previous pop up screen
        """
        screen.destroy()
        self.stat_entry(ball_entry,13,1)
        self.stat_entry(trap_entry,14,1)
        self.stat_entry(pass_entry,15,1)
        self.stat_entry(rebound_entry,21,1)
        entry=shot_entry.get()
        if(entry=='N'or entry=='' or entry=='Recorner'):
            if(shot_entry.get()==''):
                App.fixEntry(shot_entry,'N')
            
            for i in range(16,21):
                self.stat_entry(shot_entry,i,1)
        else: 
            self.stat_entry(shot_entry,16,1)
        oldWindow.destroy()
        if(entry=='Recorner'):
            self.start_corner(original_window,1)
        

    
    def defense_penalty_corner_insert(self,ball_entry,trap_entry,flier_entry,redraw_entry,shot_entry,original_window,old_window,screen):
        """
        This method inserts the data for the shot entry
        Parameters: 
            self: self
            oldWindow: this is the penalty_corner_start winodw that we are putting the widget over
            ball_entry: the entry of where the ball went
            trap_entry: the entry of if the flier made it to the ball
            flier_entry: the entry if the flier touch the ball
            redraw_entry: the entry of if there was a redraw
            shot_entry: the entry if there was a shot
            original_window: the window of the offense or defense
            old_window: the penaltyCorner_defense
            screen: the screen widget made 
        Returns: nothing
        """
        screen.destroy()
        self.stat_entry(ball_entry,11,0)
        self.stat_entry(trap_entry,12,0)
        self.stat_entry(flier_entry,13,0)
        self.stat_entry(redraw_entry,19,0)
        self.stat_entry(shot_entry,14,0)
        shot=shot_entry.get()
        if(shot=='N' or shot==''):
            if(shot==''):
                App.fixEntry(shot_entry,'N')
            for i in range(15,21):
                self.stat_entry(shot_entry,i,0)
        
        if(redraw_entry.get()=='Y'):
            old_window.destroy()
            self.start_corner(original_window,0)
        
        old_window.destroy()
        
        







    def pop_up_screen_7(self,ball_entry,trap_entry,flier_entry,redraw_entry,shot_entry,original_window,old_window):
        """
        this method creates the widget that confirms the user is ready to move forward
        Parameters:
            oldWindow: this is the penalty_corner_start winodw that we are putting the widget over
            ball_entry: the entry of where the ball went
            trap_entry: the entry of if the flier made it to the ball
            flier_entry: the entry if the flier touch the ball
            redraw_entry: the entry of if there was a redraw
            shot_entry: the entry if there was a shot
            original_window: the window of the offense or defense
            old_window: the penaltyCorner_defense
        Returns: nothing
        """
        screen=tk.Toplevel(old_window)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Confirm Information Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.defense_penalty_corner_insert(ball_entry, trap_entry, flier_entry, redraw_entry,shot_entry, original_window, old_window,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)

        return




    def pop_up_screen_5(self,ball_entry,trap_entry,pass_entry,shot_entry,rebound_entry,oldWindow,original_window):
        
        """this method creates the widget that confirms the user is ready to move forward
        Parameters:

            oldWindow: this is the penalty_corner_start window that we are putting the widget over
            ball_entry: the entry of wher ethe ball went
            trap_entry: the entry of if we made a trap
            pass_entry: the entry if we passed or not
            shot_entry: the entry of if there was a shot

            Returns: nothing

        
        """
        screen=tk.Toplevel(oldWindow)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Is the Shot Correct?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.penalty_corner_insert(ball_entry, trap_entry, pass_entry, shot_entry, rebound_entry, oldWindow,original_window,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)

        return


    def penaltyCorner_defense(self,oldWindow, original_window,formation_entry):
        """
        this method creates the widgets for the penaltyCorner defense
        Parameters: oldWindow: the window the will be destroyed. The former formation page
                    original_window: the window that will come back to after this method is done
                    formation_entry: the entry of the formation
        Returns: nothing
        
        """
        self.stat_entry(formation_entry,10,0)
        oldWindow.destroy()
        newWindow=tk.Toplevel(original_window)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("What happened on penalty corner")

        instructions=tk.Label(newWindow, text='Enter all the inputs from \n the penalty corner',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=600, y=10)


        #updating the ball entry
        ball_entry=tk.Entry(newWindow,width=20)
        ball_entry.place(x=10,y=60)
        ball_label=tk.Label(newWindow,text='Where did the ball go?', background='Black', fg='Red', font=("Arial",12))
        ball_label.place(x=10,y=10)
        #updating the ball entries
        l_button=tk.Button(newWindow,text='L', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_entry,'L'))
        l_button.place(x=10, y=100)
        one_button=tk.Button(newWindow,text='1', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_entry,'1'))
        one_button.place(x=60, y=100)
        two_button=tk.Button(newWindow,text='2', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(ball_entry,'2'))
        two_button.place(x=110, y=100)
        broken_button=tk.Button(newWindow,text='broken', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(ball_entry,'Broken'))
        broken_button.place(x=160, y=100)

        #updtating the flier if the made to the ball
        trap_entry=tk.Entry(newWindow,width=20)
        trap_entry.place(x=400,y=60)
        execute_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(trap_entry,'Y'))
        execute_button.place(x=400, y=100)
        no_execute_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(trap_entry,'N'))
        no_execute_button.place(x=450, y=100)
        trap_label=tk.Label(newWindow,text='Did the flier make it to the ball?', background='Black', fg='Red', font=("Arial",12))
        trap_label.place(x=350,y=10)

        #the flier touch the ball
        flier_entry=tk.Entry(newWindow,width=20)
        flier_entry.place(x=50,y=240)
        #updating the flier touch the ball
        flier_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(flier_entry,'Y'))
        flier_button.place(x=50, y=300)
        no_flier_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(flier_entry,'N'))
        no_flier_button.place(x=100, y=300)
        flier_label=tk.Label(newWindow,text='Did the flier touch the ball?', background='Black', fg='Red', font=("Arial",12))
        flier_label.place(x=50,y=200)

        #redraw entry
        redraw_entry=tk.Entry(newWindow, width=20)
        redraw_entry.place(x=400,y=240)
        redraw_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(redraw_entry,'Y'))
        redraw_button.place(x=400, y=300)
        no_redraw_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(redraw_entry,'N'))
        no_redraw_button.place(x=450, y=300)
        redraw_label=tk.Label(newWindow,text='Was There A Redraw?', background='Black', fg='Red', font=("Arial",12))
        redraw_label.place(x=400,y=200)

        #shot entry
        shot_entry=tk.Entry(newWindow, width=20)
        shot_entry.place(x=50,y=460)
        shot_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: self.defense_shot_chart(newWindow,shot_entry))
        shot_button.place(x=50, y=520)
        no_shot_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(shot_entry,'N'))
        no_shot_button.place(x=100, y=520)
        shot_label=tk.Label(newWindow,text='Was There A Shot?', background='Black', fg='Red', font=("Arial",12))
        shot_label.place(x=50,y=400)

        #back button
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",40), fg='Black', background='Red', width=10, command=lambda:self.pop_up_screen_7(ball_entry,trap_entry,flier_entry,redraw_entry,shot_entry,original_window,newWindow))
        
        submit_button.place(x=600, y=500)

        return











        
   
    def penalty_corner_offense(self,original_widnow):
        """this method creates the widgets for the penalty corner
        Parameters: original_widnow: the window that will come back to after this method is done
        Returns: nothing"""
        #updating the amount of penalty corners
        self.offense_total=self.offense_total+1
        self.offense_penalty_corners[2].append(self.offense_total )     
        print(self.offense_penalty_corners[2])
        newWindow=tk.Toplevel(original_widnow)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("What happened on penalty corner")

        instructions=tk.Label(newWindow, text='Enter all the inputs from \n the penalty corner',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=600, y=10)

        #the ball entry
        ball_entry=tk.Entry(newWindow,width=20)
        ball_entry.place(x=200,y=60)

        #updating the ball entries

        l_button=tk.Button(newWindow,text='L', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_entry,'L'))
        l_button.place(x=50, y=100)
        one_button=tk.Button(newWindow,text='1', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(ball_entry,'1'))
        one_button.place(x=100, y=100)
        
        two_button=tk.Button(newWindow,text='2', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(ball_entry,'2'))
        two_button.place(x=150, y=100)

        broken_button=tk.Button(newWindow,text='broken', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(ball_entry,'Broken'))
        broken_button.place(x=200, y=100)
        ball_label=tk.Label(newWindow,text='Where did the ball go initially', background='Black', fg='Red', font=("Arial",12))
        ball_label.place(x=10,y=10)

        #execute trap
        trap_entry=tk.Entry(newWindow,width=20)
        trap_entry.place(x=400,y=60)

        #updating the ball entries

        execute_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(trap_entry,'Y'))
        execute_button.place(x=400, y=100)
        no_execute_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(trap_entry,'N'))
        no_execute_button.place(x=450, y=100)
        trap_label=tk.Label(newWindow,text='Did we execute trap', background='Black', fg='Red', font=("Arial",12))
        trap_label.place(x=400,y=10)


         #the pass entry
        pass_entry=tk.Entry(newWindow,width=20)
        pass_entry.place(x=150,y=240)

        #updating the pass entries

        pass_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(pass_entry,'Y'))
        pass_button.place(x=50, y=300)
        no_pass_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(pass_entry,'N'))
        no_pass_button.place(x=100, y=300)
        dribble_button=tk.Button(newWindow,text='Dribble', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(pass_entry,'Dribble'))
        dribble_button.place(x=150, y=300)
        pass_label=tk.Label(newWindow,text='Was There A Pass?', background='Black', fg='Red', font=("Arial",12))
        pass_label.place(x=100,y=210)

        #updating shot 
        shot_entry=tk.Entry(newWindow,width=20)
        shot_entry.place(x=100,y=450)


        shot_label=tk.Label(newWindow,text='Was There A Shot?', background='Black', fg='Red', font=("Arial",12))
        shot_label.place(x=100,y=400)
        shot_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: self.shot_chart(newWindow,shot_entry))
        shot_button.place(x=100, y=500)
        no_shot_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(shot_entry,'N'))
        no_shot_button.place(x=150, y=500)
        shot_button=tk.Button(newWindow,text='Recorner', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(shot_entry,'Recorner'))
        shot_button.place(x=200, y=500)

        #updating shot 
        rebound_entry=tk.Entry(newWindow,width=20)
        rebound_entry.place(x=400,y=450)


        rebound_label=tk.Label(newWindow,text='Did we rebound?', background='Black', fg='Red', font=("Arial",12))
        rebound_label.place(x=400,y=400)
        rebound_button=tk.Button(newWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(rebound_entry,'Y'))
        rebound_button.place(x=400, y=500)
        no_rebound_button=tk.Button(newWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(rebound_entry,'N'))
        no_rebound_button.place(x=450, y=500)
        




        submit_label=tk.Label(newWindow,text='Ready to Submit?', background='Black', fg='Red', font=("Arial",30))
        submit_label.place(x=600,y=300)
        submit_button=tk.Button(newWindow,text='Submit', font=("Arial",30), fg='Black', background='Red', command=lambda: self.pop_up_screen_5(ball_entry,trap_entry,pass_entry,shot_entry, rebound_entry,newWindow,original_widnow))
        submit_button.place(x=600, y=400)

        
        return
    
    def penalty_corner_defense(self,originalWindow):
        """this is start of the defense penalty corner
            Parameters: self: self
                        originalWindow: the offense or defense window
            Returns: none
        
        """
        self.defense_total=self.defense_total+1
        self.defense_penalty_corners[2].append(self.defense_total)
    
        newWindow=tk.Toplevel(originalWindow)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
       
        newWindow.title("Defense Formation")

        instructions=tk.Label(newWindow, text='What formation did we run?',font=("Arial",40), fg='Black', background='Red' )
        instructions.place(x=600, y=10)
        formation_entry=tk.Entry(newWindow,width=20)
        formation_entry.place(x=400,y=10)
        one_three=App.insert_photo(newWindow,"1-3 Formation.jpeg")
        one_three.place(x=10,y=120)
        oneThree_button=tk.Button(newWindow,text="1:3", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1, command=lambda: App.fixEntry(formation_entry,"1:3"))
        oneThree_button.place(x=10, y=80)
        two_two=App.insert_photo(newWindow,"2-2 Formation.jpeg")
        two_two.place(x=400,y=120)
        two_two_button=tk.Button(newWindow,text="2:2", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1, command=lambda: App.fixEntry(formation_entry,"2:2"))
        two_two_button.place(x=400, y=80)
        lowBox=App.insert_photo(newWindow,"Low Box.jpg")
        lowBox.place(x=790,y=120)
        low_box_button=tk.Button(newWindow,text="low box", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1, command=lambda: App.fixEntry(formation_entry,"low box"))
        low_box_button.place(x=790, y=80)

        highBox=App.insert_photo(newWindow,"High Box.jpg")
        highBox.place(x=500,y=480)
        high_box_button=tk.Button(newWindow,text="high box", font=("Arial",20), fg="Red", background="Black" ,borderwidth=1, command=lambda: App.fixEntry(formation_entry,"high box"))

        high_box_button.place(x=500, y=440)
        
        submit_button=tk.Button(newWindow,text="Submit", font=("Arial",30), fg="Black", background="Red", command=lambda: self.penaltyCorner_defense(newWindow,originalWindow,formation_entry))
        
        submit_button.place(x=800, y=440)
        










    
    def offense_inputs(self,insert_entry,l_entry,ss1_entry,A_entry,ss2_entry,B_entry,R_entry,W_entry,original_window,old_window,screen):
        """this is the method that holds and submits all the entries to stat_entry method
        Parameters: insert_entry: the entry that holds the inserter
                    l_entry: the entry that holds the l 
                    ss1_entry: the entry that holds the ss1 entry
                    A_entry: the entry that holds the A entry
                    ss2_entry: the entry that holds the ss2 entry
                    b_entry: the entry that hold the b entry
                    r_entry: the entry that holds the r entry
                    w_entry: the entry that holds the w entry
                    old_window: the window where you inserted all the positions
                    original_window: the offense or defense window
        Returns: nothing
    
        
        """
        screen.destroy()
        self.stat_entry(insert_entry,5,1)
        self.stat_entry(l_entry,6,1)
        self.stat_entry(ss1_entry,7,1)
        self.stat_entry(A_entry,8,1)
        self.stat_entry(ss2_entry,9,1)
        self.stat_entry(B_entry,10,1)
        self.stat_entry(R_entry,11,1)
        self.stat_entry(W_entry,12,1)
        
        old_window.destroy()
        self.penalty_corner_offense(original_window)

        return

        
    def pop_up_screen_2(self,insert_entry,l_entry,ss1_entry,A_entry,ss2_entry,B_entry,R_entry,W_entry,original_window,old_window):
         """this is the method that holds and submits all the entries to stat_entry method
        Parameters: insert_entry: the entry that holds the inserter
                    l_entry: the entry that holds the l 
                    ss1_entry: the entry that holds the ss1 entry
                    A_entry: the entry that holds the A entry
                    ss2_entry: the entry that holds the ss2 entry
                    b_entry: the entry that hold the b entry
                    r_entry: the entry that holds the r entry
                    w_entry: the entry that holds the w entry
                    old_window: the window where you inserted all the positions
                    original_window: the offense or defense window
        Returns: nothing
    
        
        """
         screen=tk.Toplevel(old_window)
         screen.geometry("500x500")
         label=tk.Label(screen,text="Do you have everything?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
         label.place(x=10, y=10)
         yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.offense_inputs(insert_entry,l_entry,ss1_entry,A_entry,ss2_entry,B_entry,R_entry,W_entry,original_window,old_window,screen))
         yes_button.place(x=50, y=60)
         no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
         no_button.place(x=250, y=60)
         
    
    def offense_lineup(self,oldWindow):
        """this is the method that creates the lineup for the penalty corner
        Parameters: self: self
                    oldWindow: the offense or defense window
        Returns: nothing
        """
        newWindow=tk.Toplevel(oldWindow)
      
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo

        newWindow.title("Insert lineup Page")

        newWindow_instructions=tk.Label(newWindow, text='Please enter all the player lineups before hitting submit', fg='Red')
        newWindow_instructions.place(x=400, y=10)
        #the inserter_entry
        inserter_data,inserter_listbox,inserter_entry=App.player_search(newWindow)
        inserter_label=tk.Label(newWindow, text='Enter Inserter', fg='Red')
        inserter_label.place(x=10, y=0)
        inserter_entry.place(x=10, y=20)
        inserter_data.place(x=10, y=40)
        inserter_listbox.place(x=10, y=120)
        #the l entry
        l_data, l_listbox,l_entry=App.player_search(newWindow)
        l_label=tk.Label(newWindow, text='Enter L', fg='Red')
        l_label.place(x=210, y=0)
        l_entry.place(x=210,y=20)
        l_data.place(x=210, y=40)
        l_listbox.place(x=210, y=120)
        #the SS1 entry
        ss1_data, ss1_listbox,ss1_entry=App.player_search(newWindow)
        ss1_label=tk.Label(newWindow, text='Enter SS1', fg='Red')
        ss1_label.place(x=710, y=0)
        ss1_entry.place(x=710,y=20)
        ss1_data.place(x=710, y=40)
        ss1_listbox.place(x=710, y=120)
        #the a entry
       
        A_data, A_listbox,A_entry=App.player_search(newWindow)
        A_label=tk.Label(newWindow, text='Enter A', fg='Red')
        A_label.place(x=910, y=0)
        A_entry.place(x=910,y=20)
        A_data.place(x=910, y=40)
        A_listbox.place(x=910, y=120)

        #the SS2 entry
       
        ss2_data, ss2_listbox, ss2_entry=App.player_search(newWindow)
        ss2_label=tk.Label(newWindow, text='Enter SS2', fg='Red')
        ss2_label.place(x=10, y=250)
        ss2_entry.place(x=10,y=270)
        ss2_data.place(x=10, y=290)
        ss2_listbox.place(x=10, y=370)

        #the B entry
       
        B_data, B_listbox,B_entry=App.player_search(newWindow)
        B_label=tk.Label(newWindow, text='Enter B', fg='Red')
        B_label.place(x=210, y=250)
        B_entry.place(x=210,y=270)
        B_data.place(x=210, y=290)
        B_listbox.place(x=210, y=370)

       

        #the R entry
       
        R_data, R_listbox,R_entry=App.player_search(newWindow)
        R_label=tk.Label(newWindow, text='Enter R', fg='Red')
        R_label.place(x=710, y=250)
        R_entry.place(x=710,y=270)
        R_data.place(x=710, y=290)
        R_listbox.place(x=710, y=370)

        #the R entry
       
        W_data, W_listbox,W_entry=App.player_search(newWindow)
        W_label=tk.Label(newWindow, text='Enter W', fg='Red')
        W_label.place(x=910, y=250)
        W_entry.place(x=910,y=270)
        W_data.place(x=910, y=290)
        W_listbox.place(x=910, y=370)

        Submit_button=tk.Button(newWindow, text="Submit", fg='Red', background='Black', font=('Arial',40),command=lambda: self.pop_up_screen_2(inserter_entry,l_entry,ss1_entry,A_entry,ss2_entry,B_entry,R_entry,W_entry,oldWindow, newWindow))
        Submit_button.place(x=410,y=500)

        return
    
    def defense_inputs(self,rt_entry, GK_entry,flier_entry, LT_entry,Post_entry,original_window,old_window,screen):
        """this is the method that inputs the defense stats
            Parameters: self: self
                    oldWindow: the defense_lineup window
                    rt_entry: rt_entry
                    GK_entry: GK_ENTRY
                    flier_entry: flier_entry
                    LT_entry: Lt_entry
                    Post_entry: Post_entry
                    original_window: the defense or offense window
                    screen: the pop_up_screen
        Returns: nothing
        """
        screen.destroy()
        self.stat_entry(rt_entry,5,0)
        self.stat_entry(GK_entry,6,0)
        self.stat_entry(flier_entry,7,0)
        self.stat_entry(LT_entry,8,0)
        self.stat_entry(Post_entry,9,0)
        old_window.destroy()
        self.penalty_corner_defense(original_window)

        
        
    
    def pop_up_screen_6(self,rt_entry,GK_entry,flier_entry,LT_entry,Post_entry,original_window,old_window):
        """this is the method that creates the lineup for the penalty corner
        Parameters: self: self
                    oldWindow: the defense_lineup window
                    rt_entry: rt_entry
                    GK_entry: GK_ENTRY
                    flier_entry: flier_entry
                    LT_entry: Lt_entry
                    Post_entry: Post_entry
                    original_window: the defense or offense window
        Returns: nothing
        """
        screen=tk.Toplevel(old_window)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Do you have everything?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.defense_inputs(rt_entry, GK_entry,flier_entry, LT_entry,Post_entry,original_window,old_window,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=250, y=60)

    
    def defense_lineup(self,originalWindow):
    
        """this is the method that creates the lineup for the penalty corner
        Parameters: self: self
                    oldWindow: the offense or defense window
        Returns: nothing

        """
        
        newWindow=tk.Toplevel(originalWindow)
      
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo

        newWindow.title("Insert lineup Page")

        newWindow_instructions=tk.Label(newWindow, text='Please enter all the player lineups before hitting submit', fg='Red')
        newWindow_instructions.place(x=400, y=10)
        #the inserter_entry
        rt_data,rt_listbox,rt_entry=App.player_search(newWindow)
        rt_label=tk.Label(newWindow, text='Enter RT', fg='Red')
        rt_label.place(x=10, y=0)
        rt_entry.place(x=10, y=20)
        rt_data.place(x=10, y=40)
        rt_listbox.place(x=10, y=120)
        #the l entry
        GK_data, GK_listbox,GK_entry=App.player_search(newWindow)
        GK_label=tk.Label(newWindow, text='Enter GK', fg='Red')
        GK_label.place(x=210, y=0)
        GK_entry.place(x=210,y=20)
        GK_data.place(x=210, y=40)
        GK_listbox.place(x=210, y=120)
        #the SS1 entry
        flier_data, flier_listbox,flier_entry=App.player_search(newWindow)
        flier_label=tk.Label(newWindow, text='Enter Flier', fg='Red')
        flier_label.place(x=710, y=0)
        flier_entry.place(x=710,y=20)
        flier_data.place(x=710, y=40)
        flier_listbox.place(x=710, y=120)
        #the a entry
       
        LT_data, LT_listbox,LT_entry=App.player_search(newWindow)
        LT_label=tk.Label(newWindow, text='Enter LT', fg='Red')
        LT_label.place(x=910, y=0)
        LT_entry.place(x=910,y=20)
        LT_data.place(x=910, y=40)
        LT_listbox.place(x=910, y=120)

        #the SS2 entry
       
        Post_data, Post_listbox, Post_entry=App.player_search(newWindow)
        Post_label=tk.Label(newWindow, text='Enter Post', fg='Red')
        Post_label.place(x=10, y=250)
        Post_entry.place(x=10,y=270)
        Post_data.place(x=10, y=290)
        Post_listbox.place(x=10, y=370)

        Submit_button=tk.Button(newWindow, text="Submit", fg='Red', background='Black', font=('Arial',40),command=lambda: self.pop_up_screen_6(rt_entry,GK_entry,flier_entry,LT_entry,Post_entry,originalWindow, newWindow))
        Submit_button.place(x=410,y=500)



        
    
    
    def enter(self,quarter_entry, time_entry, player_entry,redraw_entry,path,oldWindow, originalWindow,pop_up):
        """
        this method enters all the inputs in the first offensive and defensive page
        parameters: self
                    quarter_entry: the quarter of the penalty corner
                    time_entry: the time of when the penalty corner happened in the quarter
                    player_entry: the player who caused or earned the penalty
                    oldWindow: the window that we just came from
                    originalWindow: the window that we need to go on top of
        Returns: Nothing
        """
        pop_up.destroy()
        
        self.stat_entry(quarter_entry,0,path)
        self.stat_entry(time_entry,1,path)
        self.stat_entry(player_entry,3,path)
        self.stat_entry(redraw_entry,4,path)
        oldWindow.destroy()
        if (path==1):
            self.offense_lineup(originalWindow)
        
        if(path==0):
            self.defense_lineup(originalWindow)
        
        

       
        
        return
    
    def pop_up_screen1(self,quarter_entry, time_entry, player_entry, redraw_entry, path, oldWindow, originalWindow):
        """
        this method makes a pop up screen to confirm the user has everything. 
        Parameters:
        self
                    quarter_entry: the quarter of the penalty corner
                    time_entry: the time of when the penalty corner happened in the quarter
                    player_entry: the player who caused or earned the penalty
                    oldWindow: the window that we just came from
                    originalWindow: the window that we need to go on top of
        Returns: Nothing
        
        """
        screen=tk.Toplevel(oldWindow)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Do you have everything?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.enter(quarter_entry, time_entry, player_entry, redraw_entry, path, oldWindow, originalWindow,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=250, y=60)

            
            

    def start_corner(self,oldWindow,path):
        """
        the start of the offense penalty corner process
        Parameters: self:
                    newWindow: the window we just came from which is the offense or defense window
        Returns: Nothing
        """
        currentWindow=tk.Toplevel(oldWindow)
        
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=currentWindow.winfo_screenwidth()
        screen_height=currentWindow.winfo_screenheight()
        
        
        currentWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(currentWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        

        back_button=tk.Button(currentWindow,text='Back', font=("Arial",30), fg='Black', background='Red', width=10, command=currentWindow.destroy)
        
        back_button.place(x=10, y=550)
        #the quarter entry
        quarter_entry=tk.Entry(currentWindow,width=20)
        quarter_entry.place(x=50,y=60)

        #updating the quarter entries

        one_button=tk.Button(currentWindow,text='1', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(quarter_entry,'1'))
        one_button.place(x=50, y=100)
        two_button=tk.Button(currentWindow,text='2', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(quarter_entry,'2'))
        two_button.place(x=100, y=100)
        
        three_button=tk.Button(currentWindow,text='3', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(quarter_entry,'3'))
        three_button.place(x=150, y=100)

        four_button=tk.Button(currentWindow,text='4', font=("Arial",20), fg='Black', background='Red', command=lambda: App.fixEntry(quarter_entry,'4'))
        four_button.place(x=200, y=100)
        quarter_label=tk.Label(currentWindow,text='Pick A Quarter', background='Black', fg='Red', font=("Arial",12))
        quarter_label.place(x=40,y=10)
        
        
        #making the time entry


        time_entry=tk.Entry(currentWindow, width=20)
        time_entry.place(x=10, y=250)
        time_entry_label=tk.Label(currentWindow,text='Input the time', background='Black', fg='Red', font=("Arial",12))
        time_entry_label.place(x=10, y=225)

        time_entry_instructions=tk.Label(currentWindow, text='Ex: 12:47', background='Black', fg='Red', font=("Arial",12))
        time_entry_instructions.place(x=150, y=250)

        #making who earned the corner

        
        text_label=tk.Label(currentWindow,text='Who Earned/Caused Penalty', background='Black', fg='Red', font=("Arial",12))
        text_label.place(x=400, y=10)
       
        text_data,result_listbox,player_entry=App.player_search(currentWindow)
        text_data.place(x=400, y=100)
        
        player_entry.place(x=400, y=50)
        
        result_listbox.place(x=400, y=200)

        #the quarter entry
        redraw_entry=tk.Entry(currentWindow,width=20)
        redraw_entry.place(x=800,y=100)

        #updating the quarter entries
        redraw_label=tk.Label(currentWindow,text='Was There A Redraw', background='Black', fg='Red', font=("Arial",12))
        redraw_label.place(x=800, y=10)

        redraw_button=tk.Button(currentWindow,text='Y', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(redraw_entry,'Y'))
        redraw_button.place(x=800, y=150)
        no_redraw_button=tk.Button(currentWindow,text='N', font=("Arial",20), fg='Black', background='Red',  command=lambda: App.fixEntry(redraw_entry,'N'))
        no_redraw_button.place(x=850, y=150)




        submit_button=tk.Button(currentWindow,text='SUBMIT', font=("Arial",40), fg='Black', background='Red', width=10, command= lambda: self.pop_up_screen1(quarter_entry,time_entry,player_entry,redraw_entry,path,currentWindow, oldWindow))
        submit_button.place(x=400, y=550)
        return
        
    def finish_game(self, old_window,screen):
        """
        this method creates the excel sheet 
        
        """
        screen.destroy()
        old_window.destroy()
        self.root.destroy()
        CreateStat(self.offense_penalty_corners_labels,self.offense_penalty_corners,self.defense_penalty_corners_labels,self.defense_penalty_corners,self.other_stats,self.offense_total,self.defense_total)


    def pop_up_screen_10(self,old_window):
        """
        this is the final pop up to conclude game. 
        Parameters: self
        Returns: nothing
        """

        screen=tk.Toplevel(old_window)
        screen.geometry("500x500")
        label=tk.Label(screen,text="Complete Game?", font=("Arial",30), fg="Red", background="Black" ,borderwidth=1)
        label.place(x=10, y=10)
        yes_button=tk.Button(screen,text="Yes", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda:self.finish_game(old_window,screen))
        yes_button.place(x=50, y=60)
        no_button=tk.Button(screen,text="No", font=("Arial",50), fg="Red", background="Black" ,borderwidth=1, command=lambda: screen.destroy())
        no_button.place(x=200, y=60)
        

        
        

    def chose_path(self):
        """
        this is one of the main pages. Each time you want to start a penalty corner, 
        it will be at this screen. This screen includes an offense, defense, or finish game button
        Parameters: self
        Returns: Nothing
        """
        newWindow=tk.Toplevel(self.root)
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        newWindow.title("Pick a Corner")
        
        offense_button=tk.Button(newWindow,text='OFFENSE',fg='Black', background='Red',font=("Arial",40), width=10, command=lambda:self.start_corner(newWindow,1))
        offense_button.place(x=10, y=10)
        newWindow_offense_instruction=tk.Label(newWindow,text='Start OFFENSE Corner', background='Black', fg='Red', font=("Arial",12))
        newWindow_offense_instruction.place(x=10, y=175)
        defense_button=tk.Button(newWindow, text='DEFENSE', fg='Black', background='Red', font=("Arial",40), width=10,command=lambda: self.start_corner(newWindow,0))
        defense_button.place(x=900,y=10)
        newWindow_defense_instruction=tk.Label(newWindow,text='Start DEFENSE Corner', background='Black', fg='Red', font=("Arial",12))
        newWindow_defense_instruction.place(x=900, y=175)
        submit_button=tk.Button(newWindow,text='SUBMIT',fg='Black', background='Red',font=("Arial",40), width=10,command=lambda: self.pop_up_screen_10(newWindow))
        submit_button.place(x=450, y=450)
        newWindow_submit_instruction=tk.Label(newWindow,text='Complete Game', background='Black', fg='Red', font=("Arial",12))
        newWindow_submit_instruction.place(x=450, y=600)
        return



    def other_stats_entry(self, date_entry, home_entry,away_entry, newWindow):
        """
        this is the method that inputs the game details into an array.
        Parameters: self
        Returns, the starter page
        
        """
        date_query=date_entry.get()
        home_query=home_entry.get()
        away_query=away_entry.get()
        self.other_stats[0]=date_query
        self.other_stats[1]=home_query
        self.other_stats[2]=away_query
        newWindow.destroy()
        self.chose_path()
        return
        

    
    def starter_page(self):
        """
        this is the page that has the game details
        Parameters: self
        Returns: the starter page
        
        """
        
        newWindow=tk.Toplevel(self.root)
        
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=newWindow.winfo_screenwidth()
        screen_height=newWindow.winfo_screenheight()
        
        
        newWindow.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        newWindow_label=tk.Label(newWindow,image=photo)
        newWindow_label.pack(fill="both", expand=True)
        #you need this although why I don't know

        newWindow_label.image=photo
        #date entry
        newWindow.title("Data Entry Page 1")
        date_title=tk.Label(newWindow, text='Enter Date of Match', width=40, height=2)
        date_title.place(x=50, y=10)
        #home team entry
        date_entry=tk.Entry(newWindow, width=25)
        date_entry.place(x=80, y=50)
        home_label=tk.Label(newWindow,text='Enter Home Team Name', width=40, height=2)
        home_label.place(x=50, y=90)
        home_entry=tk.Entry(newWindow, width=60 )
        home_entry.place(x=30, y=130)
        #away entry
        away_label=tk.Label(newWindow, text='Enter Away Team Name', width=40, height=2)
        away_label.place(x=50, y=160)
        away_entry=tk.Entry(newWindow, width=60 )
        away_entry.place(x=30, y=200)

        #submit/start button
        submit_button=tk.Button(newWindow,text='Start Game', font=("Arial",15), width=40, height=5, command=lambda:self.other_stats_entry(date_entry,home_entry,away_entry, newWindow) )
        submit_button.place(x=50, y=250)
        newWindow_instructions=tk.Label(newWindow, text='Please enter the date of the match \n home team \n and the away team before hitting the Start Game Button', fg='Red')
        newWindow_instructions.place(x=300, y=50)
        return





        



        
    @staticmethod
    def start_program(self):
        """
        this program starts the main background of the program. the entry screen
        Parameters: self
        Returns: the root of the image
        """
        root=tk.Tk()
        #first we neeed to make the dimensions of the program the size for any screen
        screen_width=root.winfo_screenwidth()
        screen_height=root.winfo_screenheight()
        
        
        root.geometry(f"{screen_width}x{screen_height}")
        image=Image.open("Wildcat logo.png").resize((screen_width,screen_height),Image.LANCZOS)
        #putting the background image. All background images in the program should be like this. 
        photo=ImageTk.PhotoImage(image)
        root_label=tk.Label(root,image=photo)
        root_label.pack(fill="both", expand=True)
        root_label.image=photo
        label=tk.Label(root, text='Press To Start Game:', width=20, height=2)
        label.place(x=400, y=200)                                        #the lambda is important
        root_button=tk.Button(root, text="Start Game", font=("Arial", 30),width=11, height=1,background='Red' ,command=lambda: self.starter_page())
        root_button.place(x=400, y=400)
        root.title("Field Hockey App")
        return root
    
    

        

    
app_instance=App()

    

       
        


