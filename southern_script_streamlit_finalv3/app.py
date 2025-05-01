import streamlit as st
from scraper_with_inference import run_scraper
from pdf_to_excel_converter import convert_pdf_to_excel
import pandas as pd

st.set_page_config(page_title="Southern Script Suite", layout="centered")

# Simple login mechanism
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "strada" and password == "partners":
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
else:
    st.sidebar.title("Southern Script Suite")
    app_mode = st.sidebar.radio("Choose a tool", ["Email Scraper", "PDF to Excel Converter"])

    if app_mode == "Email Scraper":
        st.title("Founder Email Scraper")
        uploaded_file = st.file_uploader("Upload Excel file with columns: Website, Founder Name", type=["xlsx"])
        if uploaded_file is not None:
            df_result = run_scraper(uploaded_file)
            st.dataframe(df_result)
            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results CSV", csv, "email_scraper_results.csv", "text/csv")

    elif app_mode == "PDF to Excel Converter":
        st.title("PDF Balance Sheet to Excel Converter")
        uploaded_pdf = st.file_uploader("Upload Balance Sheet PDF", type=["pdf"])
        if uploaded_pdf is not None:
            output_path = convert_pdf_to_excel(uploaded_pdf)
            with open(output_path, "rb") as f:
                st.download_button("Download Excel File", f, file_name="converted_balance_sheet.xlsx")
