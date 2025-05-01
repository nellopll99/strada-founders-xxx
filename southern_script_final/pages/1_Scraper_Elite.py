
import streamlit as st
import pandas as pd
import re
import requests
import dns.resolver
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import smtplib
import socket
from io import BytesIO

st.set_page_config(page_title="Southern Script – Elite Scraper", layout="wide")
st.title("📬 Southern Script – Scraper ELITE")

st.markdown("Upload an Excel file with **'Domain'** and **'Full Name'** columns. This tool will scrape, verify, and score email addresses with enriched logic.")

uploaded_file = st.file_uploader("📁 Upload file", type=["xlsx"])

def clean_domain(domain):
    parsed = urlparse(domain)
    if parsed.netloc:
        domain = parsed.netloc
    domain = domain.replace("www.", "").replace("http://", "").replace("https://", "").strip("/")
    return domain

def extract_emails_from_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        found = set(re.findall(r"[\w\.-]+\s?\@\s?[\w\.-]+", text))
        cleaned = [re.sub(r"\s?", "", email.lower()) for email in found if "@" in email]
        return list(set(cleaned))
    except:
        return []

def generate_email_patterns(name, domain):
    first, last = name.lower().split()[0], name.lower().split()[-1]
    patterns = [
        (f"{first}.{last}@{domain}", "first.last", 10),
        (f"{first}@{domain}", "first", 8),
        (f"{first[0]}.{last}@{domain}", "f.last", 7),
        (f"{first}{last}@{domain}", "firstlast", 6),
        (f"{first[0]}{last}@{domain}", "flast", 5),
        (f"{last}@{domain}", "last", 4),
    ]
    return patterns

def verify_mx(domain):
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def smtp_check(email):
    domain = email.split('@')[1]
    try:
        mx = dns.resolver.resolve(domain, 'MX')[0].exchange.to_text()
        server = smtplib.SMTP(timeout=10)
        server.connect(mx)
        server.helo(socket.gethostname())
        server.mail("me@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def duckduckgo_check(name, email):
    query = f"{name} {email}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return bool(soup.find_all("a", class_="result__a"))
    except:
        return False

def score_email(email, signals):
    score = 0
    if signals["smtp"]: score += 15
    if signals["mx"]: score += 5
    if signals["found_on_site"]: score += 10
    if signals["found_on_web"]: score += 10
    return score

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    results = []

    for _, row in df.iterrows():
        full_name = str(row["Full Name"]).strip()
        domain_raw = str(row["Domain"]).strip()
        domain = clean_domain(domain_raw)
        website_url = f"http://{domain}"
        scraped_emails = extract_emails_from_website(website_url)

        candidates = []
        patterns = generate_email_patterns(full_name, domain)
        for email, method, weight in patterns:
            signals = {
                "mx": verify_mx(domain),
                "smtp": smtp_check(email),
                "found_on_site": email in scraped_emails,
                "found_on_web": duckduckgo_check(full_name, email)
            }
            score = score_email(email, signals) + weight
            candidates.append({
                "Full Name": full_name,
                "Domain": domain,
                "Email": email,
                "Method": method,
                "Score": score,
                "Signals": ", ".join([k for k, v in signals.items() if v])
            })

        best = max(candidates, key=lambda x: x["Score"], default={})
        if best:
            results.append(best)

    result_df = pd.DataFrame(results)
    st.success("✅ Processing complete.")
    st.dataframe(result_df)

    buf = BytesIO()
    result_df.to_excel(buf, index=False)
    buf.seek(0)
    st.download_button("📥 Download Results", data=buf, file_name="elite_scraper_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
