import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dynamic Job Directory", layout="wide")

st.title("📄 US Job Directory Filter (Dynamic Upload Demo)")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Validate expected columns
        expected_columns = [
            "Full Name", "First Name", "Last Name", "Email Address", "Job Title",
            "Office Name", "Phone", "Street Address", "City", "State",
            "Zip", "Website", "Industry Tag"
        ]

        if not all(col in df.columns for col in expected_columns):
            st.error("❌ Uploaded file is missing required columns.")
            st.stop()

        # Sidebar Filters
        with st.sidebar:
            st.header("🔍 Filter Options")
            job = st.selectbox("Job Title", [""] + sorted(df["Job Title"].dropna().unique()))
            city = st.selectbox("City", [""] + sorted(df["City"].dropna().unique()))
            state = st.selectbox("State", [""] + sorted(df["State"].dropna().unique()))
            industry = st.selectbox("Industry Tag", [""] + sorted(df["Industry Tag"].dropna().unique()))

        # Filtering Logic
        filtered_df = df.copy()
        if job:
            filtered_df = filtered_df[filtered_df["Job Title"] == job]
        if city:
            filtered_df = filtered_df[filtered_df["City"] == city]
        if state:
            filtered_df = filtered_df[filtered_df["State"] == state]
        if industry:
            filtered_df = filtered_df[filtered_df["Industry Tag"] == industry]

        st.subheader(f"🧾 Filtered Results ({len(filtered_df)} matches)")
        st.dataframe(filtered_df.head(100), use_container_width=True)

        # Download Button
        st.download_button(
            "📥 Download Filtered Data",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")

else:
    st.info("👆 Upload a .xlsx file to get started.")
