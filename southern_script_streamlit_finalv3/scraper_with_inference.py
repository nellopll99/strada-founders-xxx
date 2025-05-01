import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import tldextract

COMMON_EMAILS = ["info", "contact", "amministrazione", "sales", "support", "help", "servizio.clienti"]

def clean_domain(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"
    except Exception:
        return ""

def scrape_emails_from_website(domain):
    try:
        response = requests.get(f"https://{domain}", timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        emails = set(re.findall(r"[\w\.\-]+@[\w\.\-]+", soup.get_text()))
        return list(emails)
    except:
        return []

def generate_possible_emails(name, domain):
    name_parts = name.lower().split()
    patterns = [
        f"{name_parts[0]}@{domain}",
        f"{name_parts[0]}.{name_parts[-1]}@{domain}",
        f"{name_parts[0][0]}{name_parts[-1]}@{domain}",
        f"{name_parts[-1]}@{domain}",
        f"{name_parts[-1]}.{name_parts[0]}@{domain}",
    ]
    return patterns

def run_scraper(file):
    df = pd.read_excel(file)
    if "Website" not in df.columns or "Founder Name" not in df.columns:
        return pd.DataFrame({"Error": ["Missing required columns 'Website' or 'Founder Name'"]})

    df["Domain"] = df["Website"].apply(clean_domain)

    best_emails = []
    alternatives = []
    generics = []

    for _, row in df.iterrows():
        domain = row["Domain"]
        founder = row["Founder Name"]
        emails = scrape_emails_from_website(domain)

        generated = generate_possible_emails(founder, domain)
        best = next((e for e in generated if e in emails), "")
        alt = [e for e in generated if e != best]
        common = [e for e in emails if any(g in e for g in COMMON_EMAILS)]

        best_emails.append(best if best else (generated[0] if generated else ""))
        alternatives.append(", ".join(alt))
        generics.append(", ".join(common))

    df["Best Email"] = best_emails
    df["Alternative Formats"] = alternatives
    df["Generic Emails"] = generics

    return df[["Website", "Founder Name", "Best Email", "Alternative Formats", "Generic Emails"]]
