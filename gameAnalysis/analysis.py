"""
This file is for analyzing trackman and truMedia csvs to grade
Davidson baseball players over a set of games. 
Client: Davidson Baseball Coaches
Author: Frank Howden 
Output: A CSV which grades the players
"""

import pandas as pd
import numpy as np 
import os
import glob
import jinja2 
import sys
import io

print(sys.executable)


def file_input():
    """
    This function takes in multiple trackman and truMedia csvs and returns them as dataframes. 
    """
    trackman_path = input("Enter the directory path containing your Trackman CSVs: ")

    # Get a list of all CSV files in the directory
    files = glob.glob(trackman_path + "\*.csv")
    print(f"Found {len(files)} CSV files: {files}")

    # Read each CSV file into a list of DataFrames
    trackman_dfs = []
    for file in files:
        df = pd.read_csv(file)
        trackman_dfs.append(df)
    
    # Concatenate all DataFrames into one, using only the header from the first file
    # ignore_index=True ensures row numbers are reset sequentially
    if trackman_dfs:
        trackman_df = pd.concat(trackman_dfs, ignore_index=True)
    else:
        raise ValueError("No CSV files found in the specified directory.")
    
    # Get the file path for the truMedia csv
    truMedia_path_input = input("Enter the file path for the truMedia csv: ")
    truMedia_df = pd.read_csv(truMedia_path_input)

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
    lambda x: 1 if ((x['PlateLocHeight'] <= 1.5 or x['PlateLocHeight'] >= 3.5) or
                    (x['PlateLocSide'] <= -0.9 or x['PlateLocSide'] >= 0.9))
    else 0,
    axis=1
)
    
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

    dataset['DZoneTake']=dataset[['Outside','PitchType','PitchCall']].apply(lambda x: -2 if x['Outside'] == 0 
                                                                        and x['PitchType']=='Fastball' 
                                                                        and x['PitchCall']=='StrikeCalled'  else 0, axis=1)

    dataset['KScoring']=dataset['PitchCall'].apply(lambda x: -2 if x=='StrikeCalled' 
                                                   else -1.5 if x=='StrikeSwinging'
                                                   else 0)
    
    dataset['CZoneSwingPts']=dataset[['Outside','PitchCall']].apply(lambda x: -1 if x['Outside'] == 1 and x['PitchCall']=='StrikeSwinging'
                                                                  else 0, axis=1)
    
    dataset['CZoneTakePts']=dataset[['Outside','PitchCall']].apply(lambda x: 0.25 if x['Outside'] == 1
                                                                             and x['PitchCall']=='BallCalled' 
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
    
    return dataset
   
    


def merge_datasets(trackman_df, truMedia_df):
    """
    This function takes in the trackman and truMedia dataframes and analyzes the batting performance of the players. 
    input: trackman_df: a dataframe containing the trackman data
           truMedia_df: a dataframe containing the truMedia data
    output: a dataframe containing the analyzed batting performance of the players
    """
    # Merge the trackman and truMedia dataframes on the appropriate columns (e.g., player name, date, etc.)
    
    # make new trackman name based on columns of trackman df and trumedia df
    trackman_df['Batter_Name'] = trackman_df['Batter'].str.split(', ').str[1].str[0] + '. ' + trackman_df['Batter'].str.split(', ').str[0]

    date=trackman_df['Date'].unique()
    print(date)

    batter_df_columns=['Batter_Name', 'BatterTeam', 'BatterSide','PlateLocHeight', 'PlateLocSide', 'PitchCall', 'KorBB', 'PlayResult', 'ExitSpeed', 'Angle', 'TaggedPitchType','RunsScored','Date']
    
    batter_df=trackman_df.loc[trackman_df['BatterTeam']=='DAV_WIL',batter_df_columns].copy()

    
    #truMedia_df['trackman_name']=truMedia_df['player'] + ', ' + truMedia_df['playerFirstName']
   
    
    merge_df = pd.merge(batter_df, truMedia_df, left_on='Batter_Name', right_on='entityKey', how='inner')
   

    return merge_df,date


def create_excel_output(analysis_df,date):
    dataframe = analysis_df.copy()

    print(dataframe.dtypes)

    dataframe = dataframe[['Batter_Name', 'TotalScore', 'RScore', 'PScore', 'PAScore',
                           'Chase%', 'InZoneWhiff%', 'MxExitVel',
                           '90thExitVel', 'ExitVel', 'Angle','xAVG']]

    dataframe['Chase%'] = pd.to_numeric(dataframe['Chase%'].str.replace('%', '', regex=False), errors='coerce')
    dataframe['InZoneWhiff%'] = pd.to_numeric(dataframe['InZoneWhiff%'].str.replace('%', '', regex=False), errors='coerce')

    dataframe['PAScore'] = pd.to_numeric(dataframe['PAScore'], errors='coerce')
    dataframe['MxExitVel'] = pd.to_numeric(dataframe['MxExitVel'], errors='coerce')
    dataframe['90thExitVel'] = pd.to_numeric(dataframe['90thExitVel'], errors='coerce')
    dataframe['ExitVel'] = pd.to_numeric(dataframe['ExitVel'], errors='coerce')
    dataframe['Angle'] = pd.to_numeric(dataframe['Angle'], errors='coerce')
    dataframe['xAVG'] = pd.to_numeric(dataframe['xAVG'], errors='coerce')
    dataframe['TotalScore'] = pd.to_numeric(dataframe['TotalScore'], errors='coerce')
    dataframe['RScore'] = pd.to_numeric(dataframe['RScore'], errors='coerce')
    dataframe['PScore'] = pd.to_numeric(dataframe['PScore'], errors='coerce')

    dataframe = dataframe.groupby('Batter_Name').agg({
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

    title =  f"DC Baseball Batter Analysis - {date[0]} -- {date[-1]}.xlsx"
    styled_df.to_excel(title, engine='openpyxl', index=False)
    return title


def create_excel_output_bytes(analysis_df, date):
    dataframe = analysis_df.copy()

    dataframe = dataframe[['Batter_Name', 'TotalScore', 'RScore', 'PScore', 'PAScore',
                           'Chase%', 'InZoneWhiff%', 'MxExitVel',
                           '90thExitVel', 'ExitVel', 'Angle','xAVG']]

    dataframe['Chase%'] = pd.to_numeric(dataframe['Chase%'].str.replace('%', '', regex=False), errors='coerce')
    dataframe['InZoneWhiff%'] = pd.to_numeric(dataframe['InZoneWhiff%'].str.replace('%', '', regex=False), errors='coerce')

    dataframe['PAScore'] = pd.to_numeric(dataframe['PAScore'], errors='coerce')
    dataframe['MxExitVel'] = pd.to_numeric(dataframe['MxExitVel'], errors='coerce')
    dataframe['90thExitVel'] = pd.to_numeric(dataframe['90thExitVel'], errors='coerce')
    dataframe['ExitVel'] = pd.to_numeric(dataframe['ExitVel'], errors='coerce')
    dataframe['Angle'] = pd.to_numeric(dataframe['Angle'], errors='coerce')
    dataframe['xAVG'] = pd.to_numeric(dataframe['xAVG'], errors='coerce')
    dataframe['TotalScore'] = pd.to_numeric(dataframe['TotalScore'], errors='coerce')
    dataframe['RScore'] = pd.to_numeric(dataframe['RScore'], errors='coerce')
    dataframe['PScore'] = pd.to_numeric(dataframe['PScore'], errors='coerce')

    dataframe = dataframe.groupby('Batter_Name').agg({
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

    output = io.BytesIO()
    styled_df.to_excel(output, engine='openpyxl', index=False)
    output.seek(0)
    title = f"DC Baseball Batter Analysis - {date[0]} -- {date[-1]}.xlsx"
    return output.read(), title


def run_analysis_from_upload(trackman_files, truMedia_file):
    trackman_dfs = []
    for uploaded_file in trackman_files:
        trackman_dfs.append(pd.read_csv(uploaded_file))

    if not trackman_dfs:
        raise ValueError("No Trackman CSV files were provided.")

    trackman_df = pd.concat(trackman_dfs, ignore_index=True)
    truMedia_df = pd.read_csv(truMedia_file)

    batter_analysis_df, date = merge_datasets(trackman_df, truMedia_df)
    analysis_df = analyze_batting_performance(batter_analysis_df)
    excel_bytes, output_filename = create_excel_output_bytes(analysis_df, date)
    return analysis_df, excel_bytes, output_filename


def run_analysis():
    """
    This function runs the entire analysis process and outputs the final graded CSV.
    """
    trackman_df, truMedia_df = file_input()
    
    # trackman_df=pd.read_csv("trackman_test.csv")
    # truMedia_df=pd.read_csv("Tru Media CSVs\Davidson - Cats Stats Player Stats 02-21-25 -- 02-23-25.csv")
    batter_analysis_df, date = merge_datasets(trackman_df, truMedia_df)  
    dataframe = analyze_batting_performance(batter_analysis_df)
    output_path = create_excel_output(dataframe, date)
    print(f"Analysis complete. Output saved to {output_path}")
    
    
if __name__ == "__main__":
    run_analysis()

