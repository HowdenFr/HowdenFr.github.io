"""
This file is for analyzing trackman and truMedia csvs to grade
Davidson baseball players over a set of games. 
Client: Davidson Baseball Coaches
Author: Frank Howden 
Output: A CSV which grades the players
"""

import pandas as pd
import numpy as np 
import openpyxl as pxl
import os
import glob


def file_input():
    """
    This function takes in the trackman and truMedia csvs and returns them as dataframes. 
    """
    # Get the file paths for the trackman and truMedia csvs
    #trackman_path_input = input("Enter the file path for the trackman csv, can enter multiple: ")
    #truMedia_path_input = input("Enter the file path for the truMedia csv: ")

    # Read the csvs into dataframes
    trackman_df = pd.read_csv("trackman_test.csv")
    truMedia_df = pd.read_csv("Tru Media CSVs\Davidson - Cats Stats Player Stats.csv")

    #makes the trackman csvs into one csv, then reads it into a dataframe

    with open ('trackman_test.csv', 'w') as outputfile:
        inputFileList = glob.glob("Trackman CSVs/02-21-25 -- 02-23-25\*.csv")
        first_file = True
        for inputFile in inputFileList:
            with open(inputFile, 'r') as sourcefile:
                lines = sourcefile.readlines()
                if first_file:
                    # Write all lines including header for the first file
                    outputfile.writelines(lines)
                    first_file = False
                else:
                    # Skip the first line (header) for subsequent files
                    if len(lines) > 1:
                        outputfile.writelines(lines[1:])
            outputfile.write("\n")
    trackman_df=pd.read_csv("trackman_test.csv")

    return trackman_df, truMedia_df

def analyze_batting_performance(merge_df):
    """
    This function takes in the merged trackman and truMedia dataframe and analyzes the batting performance of the players. 
    input: merge_df: a dataframe containing the merged trackman and truMedia data
    output: a dataframe containing the analyzed batting performance of the players
    """
    # Perform analysis on the merged dataframe to evaluate batting performance
    # For example, you could calculate average exit speed, launch angle, etc. for each player
    dataset = merge_df.copy()
    dataset['PitchType'] = dataset['TaggedPitchType'].apply(
        lambda x: 'Fastball' if x == 'Fastball'
        else ('BreakingBall' if x == 'Curveball' or x == 'Slider'
                    else 'OffSpeed'))

    dataset['Outside'] = dataset[['PlateLocSide','PlateLocHeight']].apply(
        lambda x: 1 if((x[1]<=1.50000 or x[1]>=3.50000) or (x[0]<=-0.90000 or x[0]>=0.90000)) 
                    else 0, axis=1)
    
    dataset['LaRange'] = dataset['Angle'].apply(lambda x: 2 if x >= 10 and x <= 20
                                                else 1 if (x > 20 and x <= 25) or (x >= 5 and x < 10)
                                                else 0 if (x >= 0 and x < 5) or (x > 25 and x <= 30)
                                                else -1 if (x > 30 and x <= 40) or (x >= -10 and x < 0)
                                                else -2 if x < -10 or x > 40
                                                else 0)
    

    dataset['EVRange'] = dataset['ExitSpeed'].apply(lambda x: 3 if x > 95
                                                else 2 if x >= 90 and x < 95
                                                else 1 if x >= 85 and x < 90
                                                else 0 if x >= 75 and x < 85
                                                else -1 if x >= 70 and x < 75
                                                else -2 if x >= 65 and x < 70
                                                else -3 if x < 65
                                                else 0)
    
    dataset['DamageZone'] = dataset['LaRange'] + dataset['EVRange']

    dataset['DZoneTake']=dataset[['Outside','PitchType','PitchCall']].apply(lambda x: -2 if x[0] == 0 
                                                                        and x[1]=='Fastball' 
                                                                        and x[2]=='StrikeCalled'  else 0, axis=1)

    dataset['KScoring']=dataset['PitchCall'].apply(lambda x: -2 if x=='StrikeCalled' 
                                                   else -1.5 if x=='StrikeSwinging'
                                                   else 0)
    
    dataset['CZoneSwingPts']=dataset[['Outside','PitchCall']].apply(lambda x: -1 if x[0] == 1 and x[1]=='StrikeSwinging'
                                                                  else 0, axis=1)
    
    dataset['CZoneTakePts']=dataset[['Outside','PitchCall']].apply(lambda x: 0.25 if x[0] == 1
                                                                             and x[1]=='BallCalled' 
                                                                             else 0, axis=1)
    dataset['RScore']=dataset['RunsScored'] + dataset['PlayResult'].apply(lambda x: 1 if x=='Single' 
                                                                          else 2 if x=='Double'
                                                                          else 3 if x=='Triple'
                                                                          else 4 if x=='HomeRun' else 0) 
    + dataset['KorBB'].apply(lambda x: 1 if x=='Walk' or x=='Strikeout' else 0) 
    + dataset['PitchType'].apply(lambda x: 1 if x=='HitByPitch' else 0)

    dataset['PScore']=dataset['DamageZone'] + dataset['CZoneSwingPts'] + dataset['CZoneTakePts']
    dataset['TotalScore']=dataset['RScore'] + dataset['PScore']

    dataset['PAScore']=dataset['PlayResult'].apply(lambda x:1 if x =='Single' or x=='Double' or x=='Triple' or x=='HomeRun' or x=='Error' else 0) 
    
    dataset.to_csv('batter_analysis.csv', index=False)
    


def merge_datasets(trackman_df, truMedia_df):
    """
    This function takes in the trackman and truMedia dataframes and analyzes the batting performance of the players. 
    input: trackman_df: a dataframe containing the trackman data
           truMedia_df: a dataframe containing the truMedia data
    output: a dataframe containing the analyzed batting performance of the players
    """
    # Merge the trackman and truMedia dataframes on the appropriate columns (e.g., player name, date, etc.)
    batter_df_columns=['Batter', 'BatterTeam', 'BatterSide','PlateLocHeight', 'PlateLocSide', 'PitchCall', 'KorBB', 'PlayResult', 'ExitSpeed', 'Angle', 'TaggedPitchType','RunsScored']
    batter_df=trackman_df.loc[trackman_df['BatterTeam']=='DAV_WIL',batter_df_columns].copy()

    
    truMedia_df['trackman_name']=truMedia_df['player'] + ', ' + truMedia_df['playerFirstName']
    
    
    merge_df = pd.merge(batter_df, truMedia_df, left_on='Batter', right_on='trackman_name', how='inner')
   

    return merge_df

def create_excel_output(analysis_df):
    dataframe = analysis_df.copy()

    dataframe = dataframe[['Batter', 'TotalScore', 'RScore', 'PScore', 'PAScore',
                           'Chase%', 'InZoneWhiff%', 'MxExitVel',
                           '90thExitVel', 'ExitVel', 'Angle','xAVG']]

    dataframe['Chase%'] = pd.to_numeric(dataframe['Chase%'].str.replace('%', '', regex=False), errors='coerce')
    dataframe['InZoneWhiff%'] = pd.to_numeric(dataframe['InZoneWhiff%'].str.replace('%', '', regex=False), errors='coerce')

    dataframe = dataframe.groupby('Batter').agg({
        'TotalScore':'sum',
        'RScore':'sum',
        'PScore':'sum',
        'PAScore':'mean',
        'Chase%': 'mean',
        'InZoneWhiff%':'mean',
        'MxExitVel': 'max',
        '90thExitVel': 'mean',
        'ExitVel' : 'mean',
        'Angle':'mean',
        'xAVG' : 'mean'
    }).reset_index()

    styled_df = dataframe.style \
        .background_gradient(subset=['TotalScore'], cmap='RdYlGn', vmin=-10, vmax=10) \
        .background_gradient(subset=['PAScore'], cmap='RdYlGn', vmin=-1, vmax=1) \
        .background_gradient(subset=['Chase%'], cmap='RdYlGn_r', vmin=10, vmax=25) \
        .background_gradient(subset=['InZoneWhiff%'], cmap='RdYlGn_r', vmin=10, vmax=30) \
        .background_gradient(subset=['MxExitVel'], cmap='RdYlGn', vmin=70, vmax=115) \
        .background_gradient(subset=['90thExitVel'], cmap='RdYlGn', vmin=70, vmax=115) \
        .background_gradient(subset=['ExitVel'], cmap='RdYlGn', vmin=70, vmax=95) \
        .background_gradient(subset=['Angle'], cmap='RdYlGn', vmin=-20, vmax=40) \
        .background_gradient(subset=['xAVG'], cmap='RdYlGn', vmin=0.200, vmax=0.350)

    styled_df.to_excel('batter_analysis_graded.xlsx', engine='openpyxl', index=False)
    

def run_analysis():
    """
    This function runs the entire analysis process and outputs the final graded CSV.
    """
    trackman_df, truMedia_df =file_input()
    
    # trackman_df=pd.read_csv("trackman_test.csv")
    # truMedia_df=pd.read_csv("Tru Media CSVs\Davidson - Cats Stats Player Stats 02-21-25 -- 02-23-25.csv")
    batter_analysis_df = merge_datasets(trackman_df, truMedia_df)  
    analyze_batting_performance(batter_analysis_df)

    dataframe=pd.read_csv('batter_analysis.csv')
    create_excel_output(dataframe)
    
    

if __name__ == "__main__":
    run_analysis()  

