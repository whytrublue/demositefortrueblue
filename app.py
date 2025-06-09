import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    return df

df = load_data()

st.title("US Job Directory Filter Demo")

# Sidebar Filters
with st.sidebar:
    st.header("Filter Options")
    job_titles = [""] + sorted(df["Job Title"].dropna().unique())
    cities = [""] + sorted(df["City"].dropna().unique())
    states = [""] + sorted(df["State"].dropna().unique())
    industries = [""] + sorted(df["Industry Tag"].dropna().unique())

    selected_job = st.selectbox("Job Title", job_titles)
    selected_city = st.selectbox("City", cities)
    selected_state = st.selectbox("State", states)
    selected_industry = st.selectbox("Industry", industries)

# Filtering
filtered_df = df.copy()
if selected_job:
    filtered_df = filtered_df[filtered_df["Job Title"] == selected_job]
if selected_city:
    filtered_df = filtered_df[filtered_df["City"] == selected_city]
if selected_state:
    filtered_df = filtered_df[filtered_df["State"] == selected_state]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry Tag"] == selected_industry]

# Display Results
st.subheader(f"Filtered Results ({len(filtered_df)} matches)")
st.dataframe(filtered_df.head(100), use_container_width=True)  # Show top 100 results

# Optional: Download filtered results
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)
