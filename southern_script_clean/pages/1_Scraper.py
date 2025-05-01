
import streamlit as st
import pandas as pd
import re
import requests
import dns.resolver
from bs4 import BeautifulSoup
from io import BytesIO
import smtplib
import socket
import time

st.set_page_config(page_title="Southern Script V2 – Email Discovery Tool", layout="wide")
st.title("Southern Script V2 – Email Discovery Tool")

uploaded_file = st.file_uploader("Upload Excel file with 'Domain' and 'Full Name'", type=["xlsx"])

def clean_domain(url):
    return url.replace("http://", "").replace("https://", "").replace("www.", "").strip().strip("/")

def build_email_patterns(name, domain):
    first, last = name.lower().split()[0], name.lower().split()[-1]
    return [
        (f"{first}.{last}@{domain}", 10),
        (f"{first}@{domain}", 8),
        (f"{first[0]}.{last}@{domain}", 7),
        (f"{first}{last}@{domain}", 6),
        (f"{first[0]}{last}@{domain}", 5),
        (f"{last}@{domain}", 4),
    ]

def verify_mx(email):
    try:
        domain = email.split('@')[1]
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def smtp_probe(email):
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo(socket.gethostname())
        server.mail("me@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def duck_search(name, email):
    query = f'{name} "{email}"'
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return bool(soup.find_all("a", class_="result__a"))
    except:
        return False

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []
    for _, row in df.iterrows():
        name = row["Full Name"].strip()
        domain = clean_domain(row["Domain"])
        best_score = 0
        best_email = ""
        for email, weight in build_email_patterns(name, domain):
            score = 0
            signals = []
            if verify_mx(email):
                score += 5
            if smtp_probe(email):
                score += 15
            if duck_search(name, email):
                score += 10
            score += weight
            if score > best_score:
                best_score = score
                best_email = email
        results.append({
            "Full Name": name,
            "Domain": domain,
            "Best Email": best_email,
            "Confidence Score": best_score,
        })

    out_df = pd.DataFrame(results)
    st.dataframe(out_df)
    buf = BytesIO()
    out_df.to_excel(buf, index=False)
    buf.seek(0)
    st.download_button("Download Results", buf, "email_results.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
