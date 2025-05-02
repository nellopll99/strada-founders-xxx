
import streamlit as st
from pages import scraper_tool, pdf_converter_tool

def main():
    st.set_page_config(page_title="Southern Script", layout="wide")

    st.sidebar.title("App")
    tool = st.sidebar.radio("Select Tool", ["Email Scraper", "PDF to Excel Converter"])

    if tool == "Email Scraper":
        scraper_tool.scraper_main()
    elif tool == "PDF to Excel Converter":
        pdf_converter_tool.pdf_converter_main()

if __name__ == "__main__":
    main()
