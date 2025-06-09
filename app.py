import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="\U0001F4BC US Job Directory", layout="wide")

# CSS Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #A4D4FF; color: #111111; }
    .css-1d391kg h1 { color: #1a73e8; }
    label { color: #1a237e; font-weight: bold; }
    .stDataFrame thead tr th { background-color: #0d47a1 !important; color: white !important; }
    .css-1d391kg { background-color: #e3f2fd; }
    .horizontal-scroll-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: -40px;
        margin-bottom: 10px;
    }
    .scroll-btn {
        background-color: #0d47a1;
        color: white;
        border: none;
        padding: 8px 12px;
        font-size: 14px;
        cursor: pointer;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("\U0001F4BC US Job Directory Demo")

uploaded_files = st.file_uploader(
    label="\U0001F4C2 Upload Excel (.xlsx) files", 
    type=["xlsx"], 
    accept_multiple_files=True
)

# Define alias mapping
COLUMN_ALIASES = {
    "Full Name": ["full name", "name"],
    "First Name": ["first name", "fname", "first"],
    "Last Name": ["last name", "lname", "last"],
    "Email Address": ["email", "email address", "e-mail"],
    "Job Title": ["job title", "position", "title", "license type"],
    "Office Name": ["office", "office name", "company"],
    "Office Phone": ["phone", "phone number", "telephone","Office Number"],
    "Mobile": ["mobile", "mobile number", "cell", "cell phone"],
    "Street Address": ["address", "street address", "street", "office address1"],
    "City": ["city", "town", "office city"],
    "State": ["state", "province", "office state"],
    "Zip": ["zip", "zipcode", "postal code", "office zip"],
    "Website": ["website", "url"],
    "Industry Tag": ["industry", "tag", "category"]
}

# Column auto-mapping function
def auto_map_columns(df, alias_dict):
    mapped_cols = {}
    df_cols_lower = {col.lower(): col for col in df.columns}
    for std_col, aliases in alias_dict.items():
        found = next((df_cols_lower[alias] for alias in aliases if alias in df_cols_lower), None)
        if found:
            mapped_cols[found] = std_col
        else:
            df[std_col] = ""  # Add missing columns as empty
    return df.rename(columns=mapped_cols)

if uploaded_files:
    try:
        dfs = []
        for uploaded_file in uploaded_files:
            df_temp = pd.read_excel(uploaded_file)
            df_temp = auto_map_columns(df_temp, COLUMN_ALIASES)
            dfs.append(df_temp)

        combined_df = pd.concat(dfs, ignore_index=True)

        expected_columns = list(COLUMN_ALIASES.keys())
        if not all(col in combined_df.columns for col in expected_columns):
            st.error("❌ Uploaded files are missing required columns.")
            st.stop()

        # Filters
        filter_cols = st.columns([2, 2, 2, 2, 2, 2, 2])

        full_name_search = filter_cols[0].text_input("\U0001F50E Full Name")
        job_filter = filter_cols[1].multiselect(
            "Job Title", options=sorted(combined_df["Job Title"].dropna().unique())
        )
        website_search = filter_cols[2].text_input("\U0001F310 Website URL")
        phone_search = filter_cols[3].text_input("\U0001F4DE Phone Number")
        city_filter = filter_cols[4].multiselect(
            "City", options=sorted(combined_df["City"].dropna().unique())
        )
        state_filter = filter_cols[5].multiselect(
            "State", options=sorted(combined_df["State"].dropna().unique())
        )
        zip_search = filter_cols[6].text_input("🏷️ Zip Code")

        industry_filter = st.multiselect(
            "Industry Tag", options=sorted(combined_df["Industry Tag"].dropna().unique())
        )

        filtered_df = combined_df.copy()

        if full_name_search:
            filtered_df = filtered_df[
                filtered_df["Full Name"].str.contains(full_name_search, case=False, na=False)
            ]

        if job_filter:
            filtered_df = filtered_df[filtered_df["Job Title"].isin(job_filter)]

        if website_search:
            def normalize_url(url):
                if pd.isna(url): return ""
                url = url.lower().strip()
                url = re.sub(r"^https?://", "", url)
                return url.rstrip("/")
            norm_website_search = normalize_url(website_search)
            filtered_df["norm_website"] = filtered_df["Website"].apply(normalize_url)
            filtered_df = filtered_df[
                filtered_df["norm_website"].str.contains(norm_website_search, na=False)
            ]

        if phone_search:
            def normalize_phone(phone):
                if pd.isna(phone): return ""
                return re.sub(r"\D", "", str(phone))
            norm_phone_search = re.sub(r"\D", "", phone_search)
            filtered_df["norm_phone"] = filtered_df["Office Phone"].apply(normalize_phone)
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

        if industry_filter:
            filtered_df = filtered_df[filtered_df["Industry Tag"].isin(industry_filter)]

        filtered_df = filtered_df.drop(columns=[c for c in ["norm_website", "norm_phone"] if c in filtered_df.columns])

        PAGE_SIZE = 30
        total_rows = len(filtered_df)
        total_pages = (total_rows - 1) // PAGE_SIZE + 1 if total_rows > 0 else 1

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
        page_df.index += 1

        page_df = page_df.fillna("")

        # Scroll buttons HTML + JS added here BEFORE dataframe
        scroll_controls = """
        <div class="horizontal-scroll-buttons">
            <button class="scroll-btn" onclick="scrollTable(-1)">⬅ Scroll Left</button>
            <button class="scroll-btn" onclick="scrollTable(1)">Scroll Right ➡</button>
        </div>
        <script>
        function scrollTable(dir) {
            const container = window.parent.document.querySelector('div[data-testid="stDataFrameResizable"] > div[role="grid"]');
            if (container) {
                container.scrollBy({ left: dir * 200, behavior: 'smooth' });
            }
        }
        </script>
        """

        components.html(scroll_controls, height=50)

        st.dataframe(page_df, use_container_width=True, height=600)

        st.download_button(
            label="\U0001F4E5 Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"⚠️ Error processing uploaded files: {e}")

else:
    st.info("\U0001F446 Please upload one or more .xlsx files to start.")
