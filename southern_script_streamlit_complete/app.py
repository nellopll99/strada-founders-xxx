
import streamlit as st
import pandas as pd
from scraper_with_inference import run_scraper

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
    st.sidebar.success("Logged in as strada")
    st.title("Email Scraper Elite")

    uploaded_file = st.file_uploader("Upload Excel with columns: Name, Website", type=["xlsx"])
    if uploaded_file:
        df_result = run_scraper(uploaded_file)
        st.success("Scraping Completed!")
        st.dataframe(df_result)
        st.download_button("Download Results", df_result.to_csv(index=False), "scraped_emails.csv")
