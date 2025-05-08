
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Referral Table Generator", layout="wide")
st.title("📊 Data Referral Table Generator")

uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    st.success("File uploaded successfully.")
else:
    st.info("Please upload a file to begin.")

# Date range filter with manual input enabled
st.markdown("### 🔍 Filter by Date Range")
date_range = st.date_input(
    "Select a date range:",
    [pd.to_datetime("today") - pd.Timedelta(days=6), pd.to_datetime("today")],
    key="main_date_input"
)

# Display a 2-column, 15-row table
data = {
    "Metric": [
        "Subs", "Quals", "Qual Rate", "Cost", "CPQL",
        "StS", "Qual to StS Rate", "Appts Total", "Qual to Appt Rate",
        "Signed ICF", "Screen Failed", "Total Milestones",
        "Qual to Milestone Rate", "Cost per Milestone", "Total Spend"
    ],
    "Value": ["" for _ in range(15)]
}
df = pd.DataFrame(data)
st.dataframe(df.set_index("Metric"), use_container_width=True)
