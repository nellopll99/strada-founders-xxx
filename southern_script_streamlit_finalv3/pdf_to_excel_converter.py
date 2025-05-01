import pdfplumber
import pandas as pd
import os

def convert_pdf_to_excel(uploaded_pdf):
    with pdfplumber.open(uploaded_pdf) as pdf:
        rows = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                rows.extend(table)
    clean_rows = [row for row in rows if row and any(cell for cell in row)]
    df = pd.DataFrame(clean_rows)
    output_path = "/tmp/converted_balance_sheet.xlsx"
    df.to_excel(output_path, index=False, header=False)
    return output_path
