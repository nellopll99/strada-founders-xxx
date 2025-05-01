
import streamlit as st
from scraper_with_inference import run_scraper
from pdf_to_excel_converter import convert_pdf_to_excel
import pandas as pd
import os

st.set_page_config(page_title="Southern Script", layout="wide")

# Simple login
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
    st.sidebar.title("Tool Menu")
    app_selection = st.sidebar.radio("Choose a tool:", ["Email Scraper", "PDF Balance Sheet Converter"])

    if app_selection == "Email Scraper":
        st.title("Founder Email Scraper")
        uploaded_file = st.file_uploader("Upload Excel with 'Website' and 'Founder' columns", type=["xlsx"])
        if uploaded_file:
            df_result = run_scraper(uploaded_file)
            st.dataframe(df_result)
            st.download_button("Download Results", df_result.to_csv(index=False), "scraped_emails.csv")

    elif app_selection == "PDF Balance Sheet Converter":
        st.title("Balance Sheet PDF to Excel Converter")
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            output_excel = convert_pdf_to_excel(uploaded_pdf.name)
            with open(output_excel, "rb") as f:
                st.download_button("Download Excel", f, output_excel)
