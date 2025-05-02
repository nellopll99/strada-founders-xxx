
import streamlit as st
import pandas as pd

def generate_emails(name, domain):
    first = name.split()[0].lower()
    last = name.split()[-1].lower()
    return [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"info@{domain}"
    ]

def scraper_main():
    st.header("Email Scraper Tool")
    uploaded_file = st.file_uploader("Upload Excel with 'Website' and 'Founder' columns", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'Website' not in df.columns or 'Founder' not in df.columns:
            st.error("Excel must contain 'Website' and 'Founder' columns.")
            return

        results = []
        for _, row in df.iterrows():
            domain = row['Website'].split("//")[-1].replace("www.", "").strip().strip('/')
            founder = row['Founder']
            emails = generate_emails(founder, domain)
            results.append({
                "Website": row['Website'],
                "Founder": founder,
                "Most Recommended": emails[1],
                "Other Options": ", ".join(emails[::2])  # es. primo e terzo
            })

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)
        st.download_button("Download Results", result_df.to_csv(index=False), file_name="emails.csv")

