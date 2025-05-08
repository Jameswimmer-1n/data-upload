import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Referral Table Generator", layout="wide")
st.title("Upload Your Excel File")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully!")
        st.write("### Preview of your data:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload a file to begin.")
