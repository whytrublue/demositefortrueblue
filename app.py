import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="💼 US Job Directory", layout="wide")

st.markdown(
    """
    <style>
    /* Background color */
    .stApp {
        background-color: #40e0d0;
        color: #111111;
    }
    /* Title style */
    .css-1d391kg h1 {
        color: #1a73e8;
    }
    /* Filter labels */
    label {
        color: #1a237e;
        font-weight: bold;
    }
    /* Dataframe header */
    .stDataFrame thead tr th {
        background-color: #0d47a1 !important;
        color: white !important;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #e3f2fd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💼 US Job Directory Demo")

if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file)
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Now proceed with filtering, pagination, etc. on combined_df


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

        filter_cols = st.columns([2, 2, 2, 2, 2, 2, 2])

        full_name_search = filter_cols[0].text_input("🔎 Full Name")
        job_filter = filter_cols[1].multiselect(
            "Job Title", options=sorted(df["Job Title"].dropna().unique())
        )
        website_search = filter_cols[2].text_input("🌐 Website URL")
        phone_search = filter_cols[3].text_input("📞 Phone Number")
        city_filter = filter_cols[4].multiselect(
            "City", options=sorted(df["City"].dropna().unique())
        )
        state_filter = filter_cols[5].multiselect(
            "State", options=sorted(df["State"].dropna().unique())
        )
        zip_search = filter_cols[6].text_input("🏷️ Zip Code")

        industry_filter = st.multiselect(
            "Industry Tag", options=sorted(df["Industry Tag"].dropna().unique())
        )

        filtered_df = df.copy()

        if full_name_search:
            filtered_df = filtered_df[
                filtered_df["Full Name"].str.contains(full_name_search, case=False, na=False)
            ]

        if job_filter:
            filtered_df = filtered_df[filtered_df["Job Title"].isin(job_filter)]

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

        if city_filter:
            filtered_df = filtered_df[filtered_df["City"].isin(city_filter)]

        if state_filter:
            filtered_df = filtered_df[filtered_df["State"].isin(state_filter)]

        if zip_search:
            filtered_df = filtered_df[
                filtered_df["Zip"].astype(str).str.contains(zip_search, na=False)
            ]

        filtered_df = filtered_df.drop(columns=[c for c in ["norm_website", "norm_phone"] if c in filtered_df.columns])

        PAGE_SIZE = 100
        total_rows = len(filtered_df)
        total_pages = (total_rows - 1) // PAGE_SIZE + 1

        if "page" not in st.session_state:
            st.session_state.page = 0

        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button("⬅️ Prev") and st.session_state.page > 0:
                st.session_state.page -= 1
        with col3:
            if st.button("Next ➡️") and st.session_state.page < total_pages - 1:
                st.session_state.page += 1

        start_idx = st.session_state.page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE

        st.markdown(f"Showing rows {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}")

        page_df = filtered_df.iloc[start_idx:end_idx].copy()
        page_df.reset_index(drop=True, inplace=True)
        page_df.index += 1  # start numbering from 1

        styled_df = page_df.style.set_table_styles([
            {'selector': 'th', 'props': [('font-weight', 'bold'), ('color', '#0d47a1')]}
        ])

        st.dataframe(styled_df, use_container_width=True, height=600)

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
