
import streamlit as st
import pandas as pd
import re
import requests
import socket
import dns.resolver
from validate_email_address import validate_email
from io import BytesIO

st.set_page_config(page_title="Southern Script – Email Discovery Tool", layout="centered")
st.title("Southern Script – Email Discovery Tool")
st.write("Upload a .xlsx file with columns 'Domain' and 'Full Name'. The app will generate possible emails, verify them, and return the result.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

def clean_domain(raw_url):
    return raw_url.replace("http://", "").replace("https://", "").replace("www.", "").strip().strip("/")

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

def extract_valid_emails(text, domain):
    raw_emails = re.findall(r"[A-Za-z0-9._%+-]+@" + re.escape(domain), text)
    return [email for email in raw_emails if "http" not in email and email.count("@") == 1]

def scrape_site_emails(domain):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "http://" + domain
        res = requests.get(url, headers=headers, timeout=10)
        return extract_valid_emails(res.text, domain)
    except:
        return []

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    st.write("⏳ Processing, please wait a moment...")
    for _, row in df.iterrows():
        raw_domain = str(row["Domain"]).strip()
        domain = clean_domain(raw_domain)
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
    st.success("✅ Emails generated and verified.")
    st.dataframe(output_df)

    buffer = BytesIO()
    output_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download the Excel results",
        data=buffer,
        file_name="hunter_like_emails.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# Reset button
if st.button("🔁 Restart"):
    st.experimental_rerun()
