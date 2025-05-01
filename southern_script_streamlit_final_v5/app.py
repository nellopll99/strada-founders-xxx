import streamlit as st
from scraper_with_inference import run_scraper
from pdf_to_excel_converter import convert_pdf_to_excel
import pandas as pd
import base64
import io

st.set_page_config(page_title="Southern Script Suite", layout="wide")

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "strada" and pw == "partners":
            st.session_state.authenticated = True
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    st.title("🔒 Southern Script Suite Login")
    login()
    st.stop()

# --- APP MENU ---
st.sidebar.title("Southern Script Tools")
app_mode = st.sidebar.radio("Choose a tool", ["📬 Email Scraper", "📊 PDF Balance Sheet Extractor"])

st.title("Southern Script Suite")

if app_mode == "📬 Email Scraper":
    st.subheader("Upload Excel with Websites and Founders")
    uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])
    if uploaded_file:
        df_result = run_scraper(uploaded_file)
        st.dataframe(df_result)
        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Results CSV", data=csv, file_name="scraped_emails.csv", mime="text/csv")

elif app_mode == "📊 PDF Balance Sheet Extractor":
    st.subheader("Upload a PDF Balance Sheet")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        excel_data = convert_pdf_to_excel(pdf_file)
        st.success("✅ PDF successfully converted!")
        st.download_button("⬇ Download Excel", data=excel_data, file_name="converted_balance_sheet.xlsx")
