
import pdfplumber
import pandas as pd
import os

def convert_pdf_to_excel(pdf_path):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                rows.extend(table)

    df = pd.DataFrame(rows)
    df = df.dropna(how='all').dropna(axis=1, how='all')
    output_path = os.path.splitext(pdf_path)[0] + ".xlsx"
    df.to_excel(output_path, index=False)
    return output_path
