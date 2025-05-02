import streamlit as st
from pages.scraper_tool import scraper_main
from pages.pdf_converter_tool import pdf_converter_main

def main():
    st.set_page_config(page_title="Southern Script", layout="wide")
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if username == "strada" and password == "partners":
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.warning("Please log in to access the tools.")
            return

    st.sidebar.title("Southern Script")
    app_choice = st.sidebar.radio("Choose a tool", ["Email Scraper", "Balance Sheet Converter"])
    st.markdown("<div style='position: fixed; bottom: 10px; width: 100%; text-align: center; color: grey;'>Southern Script | Private Equity Tools</div>", unsafe_allow_html=True)

    if app_choice == "Email Scraper":
        scraper_main()
    elif app_choice == "Balance Sheet Converter":
        pdf_converter_main()

if __name__ == "__main__":
    main()