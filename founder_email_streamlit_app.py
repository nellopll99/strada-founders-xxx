
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from io import BytesIO

st.set_page_config(page_title="Founder Email Finder", layout="centered")

st.title("Founder Email Finder")
st.write("Carica un file CSV con le colonne 'Website' e 'Founder'. Ti restituiremo un file Excel con le email trovate.")

uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

def extract_emails(text):
    return list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))

def match_email_to_founder(emails, founder_name):
    if not emails:
        return None
    name_parts = founder_name.lower().split()
    for email in emails:
        lower_email = email.lower()
        if all(part in lower_email for part in name_parts):
            return email
    return emails[0]

def scrape_founder_email(website, founder):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(website, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text()
        emails = extract_emails(text)
        match = match_email_to_founder(emails, founder)
        return {
            "Website": website,
            "Founder": founder,
            "Email": match,
            "Source": website if match else "Not Found"
        }
    except Exception as e:
        return {
            "Website": website,
            "Founder": founder,
            "Email": None,
            "Source": f"ERROR: {str(e)}"
        }

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = []
    with st.spinner("Scraping in corso..."):
        for _, row in df.iterrows():
            result = scrape_founder_email(row["Website"], row["Founder"])
            results.append(result)
            time.sleep(1)
    output_df = pd.DataFrame(results)

    st.success("Scraping completato!")
    st.dataframe(output_df)

    buffer = BytesIO()
    output_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="Scarica il file Excel",
        data=buffer,
        file_name="founder_emails.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
