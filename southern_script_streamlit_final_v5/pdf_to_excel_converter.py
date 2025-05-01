import pdfplumber
import pandas as pd
import io

def convert_pdf_to_excel(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"

    lines = [line for line in all_text.split("\n") if line.strip()]
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            label = " ".join(parts[:-1])
            value = parts[-1]
            data.append((label, value))

    df = pd.DataFrame(data, columns=["Label", "Value"])
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer
