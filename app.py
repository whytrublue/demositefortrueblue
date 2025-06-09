import streamlit as st
import pandas as pd

st.set_page_config(page_title="💼 Job Directory Dashboard", layout="wide")

st.title("💼 US Job Directory Dashboard")

uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        expected_columns = [
            "Full Name", "First Name", "Last Name", "Email Address", "Job Title",
            "Office Name", "Phone", "Street Address", "City", "State",
            "Zip", "Website", "Industry Tag"
        ]

        if not all(col in df.columns for col in expected_columns):
            st.error("❌ Uploaded file is missing required columns.")
            st.stop()

        # Sidebar filters with multiselects
        with st.sidebar:
            st.header("🎛️ Filter Panel")
            jobs = st.multiselect("Job Titles", sorted(df["Job Title"].dropna().unique()))
            cities = st.multiselect("Cities", sorted(df["City"].dropna().unique()))
            states = st.multiselect("States", sorted(df["State"].dropna().unique()))
            industries = st.multiselect("Industry Tags", sorted(df["Industry Tag"].dropna().unique()))

        # Apply filters
        filtered_df = df.copy()
        if jobs:
            filtered_df = filtered_df[filtered_df["Job Title"].isin(jobs)]
        if cities:
            filtered_df = filtered_df[filtered_df["City"].isin(cities)]
        if states:
            filtered_df = filtered_df[filtered_df["State"].isin(states)]
        if industries:
            filtered_df = filtered_df[filtered_df["Industry Tag"].isin(industries)]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📋 Records", len(filtered_df))
        col2.metric("🏙️ Cities", filtered_df["City"].nunique())
        col3.metric("🗺️ States", filtered_df["State"].nunique())
        col4.metric("🏢 Industries", filtered_df["Industry Tag"].nunique())

        # Data preview
        with st.expander("🔍 View Filtered Data", expanded=True):
            st.dataframe(filtered_df, use_container_width=True)

        # Download option
        st.download_button(
            label="📥 Download Filtered CSV",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

else:
    st.info("👆 Upload a .xlsx file to begin exploring the data.")
