import streamlit as st
import pdfplumber
import pandas as pd

def pdf_converter_main():
    st.title("PDF to Excel - Balance Sheet Converter")
    uploaded_pdf = st.file_uploader("Upload Balance Sheet PDF", type="pdf")
    if uploaded_pdf:
        with pdfplumber.open(uploaded_pdf) as pdf:
            text_data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    text_data.extend(table)
        if text_data:
            df = pd.DataFrame(text_data)
            st.dataframe(df)
            st.download_button("Download Excel", df.to_excel(index=False), file_name="balance_sheet.xlsx")
        else:
            st.warning("No tabular data detected in the PDF.")