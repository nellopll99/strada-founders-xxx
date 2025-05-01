
import streamlit as st
import pandas as pd
import re
import requests
import socket
import dns.resolver
from validate_email_address import validate_email
from io import BytesIO

st.set_page_config(page_title="Hunter-like Email Finder", layout="centered")
st.title("Hunter-style Email Finder")
st.write("Carica un file .xlsx con le colonne 'Domain' e 'Full Name'. L'app genererà email possibili, le verificherà e restituirà il risultato.")

uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx"])

def build_email_patterns(full_name, domain):
    full_name = full_name.strip().lower()
    parts = full_name.split()
    if len(parts) < 2:
        return []
    first, last = parts[0], parts[-1]
    patterns = [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}.{last}@{domain}",
        f"{last}@{domain}"
    ]
    return patterns

def verify_email_mx(email):
    try:
        domain = email.split('@')[1]
        answers = dns.resolver.resolve(domain, 'MX')
        return True if answers else False
    except:
        return False

def scrape_site_emails(domain):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "http://" + domain if not domain.startswith("http") else domain
        res = requests.get(url, headers=headers, timeout=10)
        emails = list(set(re.findall(r"[A-Za-z0-9._%+-]+@" + re.escape(domain.split('//')[-1]) + r"", res.text)))
        return emails
    except:
        return []

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    st.write("⏳ Elaborazione in corso, attendi qualche secondo...")
    for _, row in df.iterrows():
        domain = row["Domain"].strip().lower()
        full_name = row["Full Name"].strip()

        possible_emails = build_email_patterns(full_name, domain)
        verified = [e for e in possible_emails if verify_email_mx(e)]
        scraped_emails = scrape_site_emails(domain)

        results.append({
            "Domain": domain,
            "Full Name": full_name,
            "Email Pattern 1": possible_emails[0] if len(possible_emails) > 0 else "",
            "Email Pattern 2": possible_emails[1] if len(possible_emails) > 1 else "",
            "Email Pattern 3": possible_emails[2] if len(possible_emails) > 2 else "",
            "Verified Email": verified[0] if verified else "",
            "Scraped Emails": ", ".join(scraped_emails)
        })

    output_df = pd.DataFrame(results)
    st.success("✅ Email generate e verificate.")
    st.dataframe(output_df)

    buffer = BytesIO()
    output_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Scarica il file Excel con i risultati",
        data=buffer,
        file_name="hunter_like_emails.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
