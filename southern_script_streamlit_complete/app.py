import streamlit as st
import pandas as pd
from scraper_with_inference import run_scraper

st.set_page_config(page_title="Southern Script Suite", layout="wide")

# Basic login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def check_login(username, password):
    return username == "strada" and password == "partners"

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
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