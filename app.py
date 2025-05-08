import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Data Referral Table Generator", layout="wide")
st.title("📊 Data Referral Table Generator")

def extract_stage_dates(history_series, stage_keyword):
    pattern = re.compile(rf"{re.escape(stage_keyword)}: (\d{{4}}-\d{{2}}-\d{{2}})", re.IGNORECASE)
    return history_series.apply(lambda x: pd.to_datetime(pattern.findall(str(x))[-1]) if pattern.search(str(x)) else pd.NaT)

uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        df['Submitted On'] = pd.to_datetime(df['Submitted On'], errors='coerce', dayfirst=True)
    else:
        df = pd.read_excel(uploaded_file)
        df['Submitted On'] = pd.to_datetime(df['Submitted On'], errors='coerce', dayfirst=True)

    # Ensure required columns exist
    required_cols = ['Submitted On', 'UTM Source', 'Qualification Bucket', 'Lead Stage History']
    if not all(col in df.columns for col in required_cols):
        st.error("Missing one or more required columns: Submitted On, UTM Source, Qualification Bucket, Lead Stage History")
    else:
        # Extract stage transition dates
        df['sent_to_site_date'] = extract_stage_dates(df['Lead Stage History'], 'Sent to Site')
        df['appointment_scheduled_date'] = extract_stage_dates(df['Lead Stage History'], 'Appointment Scheduled')
        df['signed_icf_date'] = extract_stage_dates(df['Lead Stage History'], 'Signed ICF')

        # Filters
        st.sidebar.header("🔍 Filters")
        date_cols = ['sent_to_site_date', 'appointment_scheduled_date', 'signed_icf_date']
        valid_dates = pd.concat([df[col].dropna() for col in date_cols])
        if not valid_dates.empty:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
        else:
            min_date = pd.to_datetime("2020-01-01")
            max_date = pd.to_datetime("today")
        date_range = st.sidebar.date_input("Stage Date range", [min_date, max_date])

        utm_sources = df['UTM Source'].dropna().unique().tolist()
        selected_sources = st.sidebar.multiselect("UTM Source", utm_sources, default=utm_sources)

        # Apply filters only if user sets them
        if selected_sources:
            df = df[df['UTM Source'].isin(selected_sources)]

        if date_range:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        else:
            start_date, end_date = pd.to_datetime("2020-01-01"), pd.to_datetime("today")

        # Compute values
        subs = len(df)
        quals_df = df[df['Qualification Bucket'].str.lower() != 'disqualified']
        quals = len(quals_df)
        qual_rate = quals / subs if subs else 0

        sts_total = df['Lead Stage History'].str.contains('Sent to Site', case=False, na=False).sum()
        qual_to_sts = sts_total / quals if quals else 0

        appts_total = df['Lead Stage History'].str.contains('Appointment Scheduled', case=False, na=False).sum()
        qual_to_appt = appts_total / quals if quals else 0

        signed_icf_total = df['Lead Stage History'].str.contains('Signed ICF', case=False, na=False).sum()
        screenfail_total = df['Lead Stage History'].str.contains('screenfailed', case=False, na=False).sum()
        qual_to_milestone = signed_icf_total / quals if quals else 0

        # Summary Table
        summary_data = {
            "Metric": [
                "Subs", "Quals", "Qual Rate", "Cost", "CPQL",
                "StS", "Qual to StS Rate", "Appts Total", "Qual to Appt Rate",
                "Signed ICF", "Screen Failed", "Total Milestones",
                "Qual to Milestone Rate", "Cost per Milestone", "Total Spend"
            ],
            "Value": [
        0,
        0,
        "0%",
        "—",
        "—",
        0,
        "0%",
        0,
        "0%",
        0,
        0,
        0,
        "0%",
        "—",
        "—"
    ]
        }

        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
