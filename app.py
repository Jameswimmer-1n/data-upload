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
        df = pd.read_csv(uploaded_file, parse_dates=['Submitted On'], dayfirst=True, errors='coerce')
    else:
        df = pd.read_excel(uploaded_file, parse_dates=['Submitted On'], dayfirst=True, errors='coerce')

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
        min_date = pd.to_datetime(df[['sent_to_site_date', 'appointment_scheduled_date', 'signed_icf_date']].min().min())
        max_date = pd.to_datetime(df[['sent_to_site_date', 'appointment_scheduled_date', 'signed_icf_date']].max().max())
        date_range = st.sidebar.date_input("Stage Date range", [min_date, max_date])

        utm_sources = df['UTM Source'].dropna().unique().tolist()
        selected_sources = st.sidebar.multiselect("UTM Source", utm_sources, default=utm_sources)

        # Filtered DataFrame
        df = df[df['UTM Source'].isin(selected_sources)]
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

        # Subs and Quals based on original submission
        subs = len(df)
        quals_df = df[df['Qualification Bucket'].str.lower() != 'disqualified']
        quals = len(quals_df)

        # Stage-specific filters using extracted transition dates
        sts = quals_df[(quals_df['sent_to_site_date'] >= start_date) & (quals_df['sent_to_site_date'] <= end_date)]
        appts = quals_df[(quals_df['appointment_scheduled_date'] >= start_date) & (quals_df['appointment_scheduled_date'] <= end_date)]
        signed_icf = quals_df[(quals_df['signed_icf_date'] >= start_date) & (quals_df['signed_icf_date'] <= end_date)]
        screenfails = quals_df['Lead Stage History'].str.contains('screenfailed', case=False, na=False).sum()

        # Display KPI counts only
        st.subheader("📊 Totals Summary")
        st.write(f"**Subs:** {subs}")
        st.write(f"**Quals:** {quals}")
        st.write(f"**Sent to Site:** {len(sts)}")
        st.write(f"**Appointments:** {len(appts)}")
        st.write(f"**Signed ICF:** {len(signed_icf)}")
        st.write(f"**Screenfails:** {screenfails}")
        st.write(f"**Total Milestones (Signed ICF):** {len(signed_icf)}")
        st.write(f"**Cost per Qual:** —")
        st.write(f"**Cost per Milestone:** —")
        st.write(f"**Total Spend:** —")
