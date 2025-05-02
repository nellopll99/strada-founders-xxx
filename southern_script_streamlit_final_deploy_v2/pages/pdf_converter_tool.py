
import streamlit as st
import pandas as pd
import pdfplumber
import io

def pdf_converter_main():
    st.header("PDF to Excel Converter (Optimized for Balance Sheets)")

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with pdfplumber.open(uploaded_pdf) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # Parsing semplificato: estraiamo righe con numeri e testo (molto basilare)
        lines = text.splitlines()
        records = []
        for line in lines:
            parts = line.rsplit(" ", 1)
            if len(parts) == 2 and parts[1].replace(",", "").replace(".", "").isdigit():
                records.append({"Description": parts[0].strip(), "Value": parts[1].strip()})

        df = pd.DataFrame(records)
        st.dataframe(df)
        to_download = io.BytesIO()
        df.to_excel(to_download, index=False)
        st.download_button("Download Excel", to_download.getvalue(), file_name="balance_sheet.xlsx")
