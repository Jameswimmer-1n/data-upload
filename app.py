
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        df['Submitted On'] = pd.to_datetime(df['Submitted On'], errors='coerce', dayfirst=True)
    else:
        df = pd.read_excel(uploaded
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
                subs,
                quals,
                f"{qual_rate:.2%}",
                "—",
                "—",
                sts_total,
                f"{qual_to_sts:.2%}",
                appts_total,
                f"{qual_to_appt:.2%}",
                signed_icf_total,
                screenfail_total,
                signed_icf_total,
                f"{qual_to_milestone:.2%}",
                "—",
                "—"
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
