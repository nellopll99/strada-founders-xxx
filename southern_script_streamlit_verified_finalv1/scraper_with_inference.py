
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def clean_domain(url):
    try:
        domain = re.findall(r"https?://([^/]+)", url)[0]
        return domain.replace("www.", "")
    except:
        return ""

def infer_email_patterns(name, domain):
    name = name.strip().lower()
    parts = name.split()
    if len(parts) == 1:
        return [f"{parts[0]}@{domain}"]
    first, last = parts[0], parts[-1]
    patterns = [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{last}@{domain}",
        f"{first[0]}.{last}@{domain}"
    ]
    return list(set(patterns))

def score_email(email, known_patterns):
    if email in known_patterns:
        return 1.0
    if "." in email or "_" in email:
        return 0.8
    return 0.6

def extract_generic_emails(website):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            found_emails = list(set(re.findall(r"[\w\.-]+@[\w\.-]+", text)))
            generic_emails = [email for email in found_emails if re.match(r"(?i)(info|contact|support|sales)[^@]*@", email)]
            return ", ".join(generic_emails[:3]) if generic_emails else ""
    except:
        return ""
    return ""

def run_scraper(file):
    df = pd.read_excel(file)
    df["Domain"] = df["Website"].apply(clean_domain)
    best_emails = []
    less_recommended = []
    confidence_scores = []
    generic_emails = []

    for _, row in df.iterrows():
        name = row["Name"]
        domain = row["Domain"]
        website = row["Website"]
        possible_emails = infer_email_patterns(name, domain)
        sorted_emails = sorted(possible_emails, key=lambda e: score_email(e, possible_emails), reverse=True)
        best_emails.append(sorted_emails[0])
        less_recommended.append(", ".join(sorted_emails[1:3]))
        confidence_scores.append(round(score_email(sorted_emails[0], possible_emails), 2))
        generic_emails.append(extract_generic_emails(website))

    df["Best Email"] = best_emails
    df["Less Recommended Emails"] = less_recommended
    df["Confidence Score"] = confidence_scores
    df["Generic Emails Found"] = generic_emails

    return df
