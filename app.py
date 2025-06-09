import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="💼 US Job Directory", layout="wide")

st.title("💼 US Job Directory Demo")

# --- Upload Button with Icon ---
uploaded_file = st.file_uploader(
    label="📂 Upload Excel (.xlsx)", 
    type=["xlsx"], 
    label_visibility="visible"
)

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

        # --- Horizontal Filter Panel ---
        # Use columns layout for horizontal alignment
        filter_cols = st.columns([2, 2, 2, 2, 2, 2, 2])

        # Full Name filter (text search)
        full_name_search = filter_cols[0].text_input("🔎 Full Name")

        # Job Title multi-select
        job_filter = filter_cols[1].multiselect(
            "Job Title", options=sorted(df["Job Title"].dropna().unique())
        )

        # Website filter (text input, normalize URLs)
        website_search = filter_cols[2].text_input("🌐 Website URL")

        # Phone filter (text input)
        phone_search = filter_cols[3].text_input("📞 Phone Number")

        # City filter multi-select
        city_filter = filter_cols[4].multiselect(
            "City", options=sorted(df["City"].dropna().unique())
        )

        # State filter multi-select
        state_filter = filter_cols[5].multiselect(
            "State", options=sorted(df["State"].dropna().unique())
        )

        # Zip filter (text input)
        zip_search = filter_cols[6].text_input("🏷️ Zip Code")

        # Industry Tag filter multi-select below filters, full width
        industry_filter = st.multiselect(
            "Industry Tag", options=sorted(df["Industry Tag"].dropna().unique())
        )

        filtered_df = df.copy()

        # Apply Full Name filter (case-insensitive substring search)
        if full_name_search:
            filtered_df = filtered_df[
                filtered_df["Full Name"].str.contains(full_name_search, case=False, na=False)
            ]

        # Apply Job Title filter
        if job_filter:
            filtered_df = filtered_df[filtered_df["Job Title"].isin(job_filter)]

        # Apply Website filter (normalize & search substring)
        if website_search:
            def normalize_url(url):
                if pd.isna(url):
                    return ""
                url = url.lower().strip()
                url = re.sub(r"^https?://", "", url)
                url = url.rstrip("/")
                return url
            norm_website_search = normalize_url(website_search)
            filtered_df["norm_website"] = filtered_df["Website"].apply(normalize_url)
            filtered_df = filtered_df[
                filtered_df["norm_website"].str.contains(norm_website_search, na=False)
            ]

        # Apply Phone filter (substring, ignore formatting)
        if phone_search:
            def normalize_phone(phone):
                if pd.isna(phone):
                    return ""
                return re.sub(r"\D", "", str(phone))
            norm_phone_search = re.sub(r"\D", "", phone_search)
            filtered_df["norm_phone"] = filtered_df["Phone"].apply(normalize_phone)
            filtered_df = filtered_df[
                filtered_df["norm_phone"].str.contains(norm_phone_search, na=False)
            ]

        # Apply City filter
        if city_filter:
            filtered_df = filtered_df[filtered_df["City"].isin(city_filter)]

        # Apply State filter
        if state_filter:
            filtered_df = filtered_df[filtered_df["State"].isin(state_filter)]

        # Apply Zip filter (partial match)
        if zip_search:
            filtered_df = filtered_df[
                filtered_df["Zip"].astype(str).str.contains(zip_search, na=False)
            ]

        # Remove helper columns if added
        filtered_df = filtered_df.drop(columns=[c for c in ["norm_website", "norm_phone"] if c in filtered_df.columns])

        # Show summary stats in columns
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Records", len(filtered_df))
        c2.metric("🏙️ Cities", filtered_df["City"].nunique())
        c3.metric("🗺️ States", filtered_df["State"].nunique())
        c4.metric("🏢 Industries", filtered_df["Industry Tag"].nunique())

        # Data table with horizontal scroll
        st.dataframe(filtered_df, use_container_width=True)

        # Download button
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")

else:
    st.info("👆 Please upload a .xlsx file to start.")
