import streamlit as st
from analysis import run_analysis_from_upload


def main():
    st.title("DC Baseball Batter Analysis")

    st.subheader("Upload Trackman CSVs")
    st.markdown("Select one or more Trackman CSV files from the same date range.")
    trackman_files = st.file_uploader(
        "Trackman CSV Files",
        accept_multiple_files=True,
        type=["csv"]
    )

    st.subheader("Upload Tru Media CSV")
    st.markdown("Select the Tru Media CSV that contains batting data for the same date range.")
    trumedia_file = st.file_uploader(
        "Tru Media CSV File",
        accept_multiple_files=False,
        type=["csv"]
    )

    analyze_enabled = bool(trackman_files) and trumedia_file is not None

    if analyze_enabled:
        if st.button("Analyze"):
            try:
                with st.spinner("Running analysis..."):
                    analysis_df, excel_bytes, output_filename = run_analysis_from_upload(
                        trackman_files,
                        trumedia_file
                    )
                st.success("Analysis complete.")
                
                st.download_button(
                    label="Download Excel Report",
                    data=excel_bytes,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
    else:
        st.button("Analyze", disabled=True)
        if not trackman_files:
            st.info("Upload at least one Trackman CSV file to enable analysis.")
        if trumedia_file is None:
            st.info("Upload one Tru Media CSV file to enable analysis.")


if __name__ == "__main__":
    main()