
import io
import fitz  # PyMuPDF
import pandas as pd

def convert_pdf_to_excel(uploaded_pdf):
    try:
        pdf = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        text_data = ""
        for page in pdf:
            text_data += page.get_text()
        pdf.close()

        lines = [line.strip() for line in text_data.split("\n") if line.strip()]
        rows = []
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                rows.append(parts)

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error: {e}")
        return None
