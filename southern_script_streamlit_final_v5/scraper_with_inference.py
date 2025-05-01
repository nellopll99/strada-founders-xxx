import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def clean_domain(url):
    return re.sub(r"https?://(www\.)?", "", url).split("/")[0]

def extract_emails_from_text(text):
    emails = re.findall(r"[\w\.-]+@[\w\.-]+", text)
    return list(set([e for e in emails if not e.startswith("noreply")]))

def generate_email_variants(name, domain):
    name = name.lower().replace(" ", ".").replace("-", "")
    first, *rest = name.split(".")
    last = rest[-1] if rest else ""
    variants = [f"{first}@{domain}", f"{first}.{last}@{domain}", f"{first[0]}{last}@{domain}", f"{first[0]}.{last}@{domain}"]
    return list(set([v for v in variants if len(v) > 5]))

def run_scraper(file):
    df = pd.read_excel(file)
    if "Website" not in df.columns or "Founder" not in df.columns:
        raise ValueError("Excel must contain 'Website' and 'Founder' columns.")
    df["Domain"] = df["Website"].apply(clean_domain)

    all_results = []

    for _, row in df.iterrows():
        domain = row["Domain"]
        founder = row["Founder"]
        founder_emails = generate_email_variants(founder, domain)

        try:
            response = requests.get(f"https://{domain}", timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            found_emails = extract_emails_from_text(soup.get_text())
        except:
            found_emails = []

        # Check if any generated email matches found emails
        best = [email for email in founder_emails if email in found_emails]
        alt = [email for email in found_emails if email not in best]

        # Add generic fallback
        generics = [e for e in found_emails if e.startswith("info") or "contact" in e or "client" in e]

        all_results.append({
            "Website": row["Website"],
            "Founder": founder,
            "Best Match": best[0] if best else "",
            "Other Valid Emails": ", ".join(alt + generics)
        })

    return pd.DataFrame(all_results)
