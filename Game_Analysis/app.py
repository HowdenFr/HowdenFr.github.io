import streamlit as st
import pandas as pd
import io
from analysis import merge_datasets, analyze_batting_performance

def create_excel_output_in_memory(analysis_df):
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

    # Create Excel in memory
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Analysis')
        workbook = writer.book
        worksheet = writer.sheets['Analysis']

        # Apply conditional formatting (simplified, as styling is complex in openpyxl)
        # For full styling, we'd need to use openpyxl directly, but this is a basic version
        # You can expand this if needed

    buffer.seek(0)
    return buffer

st.title("Baseball Player Analysis")

st.header("Upload Files")

# Upload multiple Trackman Excel files
trackman_files = st.file_uploader("Upload Trackman Excel files", type=['xlsx', 'xls'], accept_multiple_files=True)

# Upload multiple TruMedia Excel files
truMedia_files = st.file_uploader("Upload TruMedia Excel files", type=['xlsx', 'xls'], accept_multiple_files=True)

if st.button("Analyze"):
    if not trackman_files or not truMedia_files:
        st.error("Please upload both Trackman and TruMedia files.")
    else:
        # Concatenate Trackman files
        trackman_dfs = []
        for file in trackman_files:
            df = pd.read_excel(file)
            trackman_dfs.append(df)
        trackman_df = pd.concat(trackman_dfs, ignore_index=True)

        # Concatenate TruMedia files
        truMedia_dfs = []
        for file in truMedia_files:
            df = pd.read_excel(file)
            truMedia_dfs.append(df)
        truMedia_df = pd.concat(truMedia_dfs, ignore_index=True)

        # Merge datasets
        merged_df = merge_datasets(trackman_df, truMedia_df)

        # Analyze
        analysis_df = analyze_batting_performance(merged_df)

        # Create Excel output in memory
        excel_buffer = create_excel_output_in_memory(analysis_df)

        # Provide download button
        st.download_button(
            label="Download Analysis Excel",
            data=excel_buffer,
            file_name="batter_analysis_graded.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Analysis complete! Click the button above to download the Excel file.")