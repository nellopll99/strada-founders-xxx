
import streamlit as st
import pandas as pd
import re
import requests
import smtplib
import socket
import dns.resolver
import whois
from bs4 import BeautifulSoup
from io import BytesIO

st.set_page_config(page_title="Southern Script V2 – Precision Email Intelligence", layout="wide")
st.title("Southern Script V2 – Precision Email Intelligence")
st.write("Upload a .xlsx file with columns 'Domain' and 'Full Name'. The app will generate, verify, and rank the most likely correct email with confidence scoring.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

def clean_domain(raw_url):
    return raw_url.replace("http://", "").replace("https://", "").replace("www.", "").strip().strip("/")

def build_email_patterns(full_name, domain):
    first, last = full_name.lower().strip().split()[0], full_name.lower().strip().split()[-1]
    patterns = [
        (f"{first}.{last}@{domain}", 10),
        (f"{first}@{domain}", 8),
        (f"{first[0]}.{last}@{domain}", 7),
        (f"{first}{last}@{domain}", 6),
        (f"{first[0]}{last}@{domain}", 5),
        (f"{last}@{domain}", 4)
    ]
    return patterns

def verify_email_mx(email):
    try:
        domain = email.split('@')[1]
        answers = dns.resolver.resolve(domain, 'MX')
        return True if answers else False
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
        server.mail('probe@domain.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def duckduckgo_check(name, email):
    query = f'{name} "{email}"'
    try:
        ddg_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ddg_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return len(soup.find_all("a", class_="result__a")) > 0
    except:
        return False

def whois_check(domain, name):
    try:
        w = whois.whois(domain)
        name_parts = name.lower().split()
        text = str(w)
        return all(part in text.lower() for part in name_parts)
    except:
        return False

def score_email(email, name, domain):
    score = 0
    signals = []

    if verify_email_mx(email):
        score += 5
        signals.append("MX valid")

    if smtp_probe(email):
        score += 15
        signals.append("SMTP OK")

    if duckduckgo_check(name, email):
        score += 10
        signals.append("Found on web")

    if whois_check(domain, name):
        score += 5
        signals.append("WHOIS match")

    return score, ", ".join(signals)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    st.write("🧠 Processing each entry... This may take several minutes based on file size.")
    for _, row in df.iterrows():
        raw_domain = str(row["Domain"]).strip()
        domain = clean_domain(raw_domain)
        full_name = row["Full Name"].strip()

        patterns = build_email_patterns(full_name, domain)
        best_email = ""
        best_score = 0
        best_signals = ""

        for email, weight in patterns:
            score, signals = score_email(email, full_name, domain)
            total_score = score + weight
            if total_score > best_score:
                best_email = email
                best_score = total_score
                best_signals = signals

        results.append({
            "Full Name": full_name,
            "Domain": domain,
            "Best Email": best_email,
            "Confidence Score": best_score,
            "Signals": best_signals
        })

    output_df = pd.DataFrame(results)
    st.success("✅ Processing complete. Results below:")
    st.dataframe(output_df)

    buffer = BytesIO()
    output_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Excel Results",
        data=buffer,
        file_name="southern_script_v2_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.button("🔁 Restart", key="restart_button"):
    st.experimental_rerun()
