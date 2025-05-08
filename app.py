
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Data Referral Table Generator", layout="wide")
st.title("📊 Data Referral Table Generator")

uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Date filter input
    st.markdown("### 🔍 Filter by Date Range")
    date_range = st.date_input(
        "Select a date range:",
        [pd.to_datetime("today") - pd.Timedelta(days=6), pd.to_datetime("today")],
        key="main_date_input"
    )

    # Define function to get first date from Lead Stage History
    def get_first_lead_stage_date(text):
        pattern = re.compile(r"(\d{2}/\d{2}/\d{2})")
        matches = pattern.findall(str(text))
        for match in matches:
            try:
                date = pd.to_datetime(match, format="%m/%d/%y", errors='coerce')
                if pd.notna(date):
                    return date
            except:
                continue
        return pd.NaT

    df["first_stage_date"] = df["Lead Stage History"].apply(get_first_lead_stage_date)

    # Filter only rows where the first Lead Stage History date falls within the range
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[(df["first_stage_date"] >= start_date) & (df["first_stage_date"] <= end_date)]

    # Table with filtered 'Subs' count and empty other metrics
    data = {
        "Metric": [
            "Subs", "Quals", "Qual Rate", "Cost", "CPQL",
            "StS", "Qual to StS Rate", "Appts Total", "Qual to Appt Rate",
            "Signed ICF", "Screen Failed", "Total Milestones",
            "Qual to Milestone Rate", "Cost per Milestone", "Total Spend"
        ],
        "Value": [
        filtered_df.shape[0],
        filtered_df[filtered_df['Qualification Bucket'].str.lower() != 'disqualified'].shape[0],
        "", "—", "—",
        "", "", "", "",
        "", "", "", "",
        "—", "—"
    ]
    }
    display_df = pd.DataFrame(data)
    st.dataframe(display_df.set_index("Metric"), use_container_width=True)
else:
    st.info("Please upload a file to begin.")
