
import streamlit as st
import pandas as pd
import re
import requests
import socket
import dns.resolver
from io import BytesIO
from bs4 import BeautifulSoup

st.set_page_config(page_title="Southern Script – Email Discovery Tool", layout="centered")
st.title("Southern Script – Email Discovery Tool")
st.write("Upload a .xlsx file with columns 'Domain' and 'Full Name'. The app will generate email candidates, test them, and return the best match with a confidence score.")

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

def search_google_like(name, email):
    query = f'{name} "{email}"'
    try:
        ddg_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ddg_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a")
        return len(results) > 0
    except:
        return False

def scrape_site_emails(domain):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "http://" + domain
        res = requests.get(url, headers=headers, timeout=10)
        raw_emails = re.findall(r"[A-Za-z0-9._%+-]+@" + re.escape(domain), res.text)
        return list(set([e for e in raw_emails if "http" not in e and e.count("@") == 1]))
    except:
        return []

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    st.write("⏳ Processing... this may take some time.")
    for _, row in df.iterrows():
        raw_domain = str(row["Domain"]).strip()
        domain = clean_domain(raw_domain)
        full_name = row["Full Name"].strip()

        possible_emails = build_email_patterns(full_name, domain)
        verified_mx = [e for e in possible_emails if verify_email_mx(e)]
        scraped_emails = scrape_site_emails(domain)

        # Determine best match with confidence
        final_email = ""
        confidence = "Low"
        for email in verified_mx:
            if search_google_like(full_name, email):
                final_email = email
                confidence = "High"
                break
        if not final_email and verified_mx:
            final_email = verified_mx[0]
            confidence = "Medium"
        elif not final_email and scraped_emails:
            final_email = scraped_emails[0]
            confidence = "Low"

        results.append({
            "Domain": domain,
            "Full Name": full_name,
            "Generated Emails": ", ".join(possible_emails),
            "Scraped Emails": ", ".join(scraped_emails),
            "Final Email": final_email,
            "Confidence": confidence
        })

    output_df = pd.DataFrame(results)
    st.success("✅ Emails processed and scored.")
    st.dataframe(output_df)

    buffer = BytesIO()
    output_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Excel Results",
        data=buffer,
        file_name="southern_script_verified_emails.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.button("🔁 Restart"):
    st.experimental_rerun()
