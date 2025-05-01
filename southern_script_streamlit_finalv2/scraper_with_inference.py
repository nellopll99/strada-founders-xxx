
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def clean_domain(url):
    return url.replace("http://", "").replace("https://", "").split("/")[0].strip()

def extract_emails_from_website(url):
    try:
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.get_text()))
        return list(emails)
    except Exception:
        return []

def generate_possible_emails(name, domain):
    name_parts = name.strip().lower().split()
    possible_emails = []
    if len(name_parts) == 2:
        first, last = name_parts
        formats = [
            f"{first}@{domain}", f"{last}@{domain}", f"{first}.{last}@{domain}",
            f"{first[0]}{last}@{domain}", f"{first}{last}@{domain}",
            f"{first[0]}.{last}@{domain}", f"{first}.{last[0]}@{domain}"
        ]
        possible_emails = list(set(formats))
    return possible_emails

def run_scraper(file):
    df = pd.read_excel(file)
    df["Domain"] = df["Website"].apply(clean_domain)
    results = []

    for _, row in df.iterrows():
        name = row["Founder"]
        domain = row["Domain"]
        website = row["Website"]

        possible_emails = generate_possible_emails(name, domain)
        scraped_emails = extract_emails_from_website(website)

        validated_email = None
        for email in possible_emails:
            if email in scraped_emails:
                validated_email = email
                break

        results.append({
            "Founder": name,
            "Best Guess Email": validated_email or (possible_emails[0] if possible_emails else "N/A"),
            "Less Recommended Emails": ", ".join([e for e in possible_emails if e != validated_email]),
            "Scraped Emails from Website": ", ".join(scraped_emails)
        })

    return pd.DataFrame(results)
