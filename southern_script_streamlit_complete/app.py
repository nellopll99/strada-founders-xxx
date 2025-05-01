
import streamlit as st
import pandas as pd
from scraper_with_inference import run_scraper
from pdf_to_excel_converter import convert_pdf_to_excel

st.set_page_config(page_title="Southern Script Suite", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_ui():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "strada" and password == "partners":
            st.session_state.authenticated = True
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    login_ui()
else:
    st.sidebar.title("Southern Script Suite")
    app_choice = st.sidebar.radio("Choose Tool", ["📧 Email Scraper", "📄 PDF Balance Sheet Extractor"])
    
    if app_choice == "📧 Email Scraper":
        st.title("Email Scraper Elite")
        uploaded_file = st.file_uploader("Upload Excel with columns: Name, Website", type=["xlsx"])
        if uploaded_file:
            try:
                df_input = pd.read_excel(uploaded_file)
                if "Website" not in df_input.columns or "Name" not in df_input.columns:
                    st.error("Excel must contain columns named 'Name' and 'Website'.")
                else:
                    df_result = run_scraper(uploaded_file)
                    st.success("Scraping Completed!")
                    st.dataframe(df_result)
                    st.download_button("Download Results", df_result.to_csv(index=False), "scraped_emails.csv")
            except Exception as e:
                st.error(f"Failed to process file: {e}")
                
    elif app_choice == "📄 PDF Balance Sheet Extractor":
        st.title("Balance Sheet PDF to Excel Converter")
        uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
        if uploaded_pdf:
            output_excel = convert_pdf_to_excel(uploaded_pdf)
            if output_excel:
                st.success("Conversion Complete!")
                st.download_button("Download Excel", data=output_excel.read(), file_name="converted.xlsx")
