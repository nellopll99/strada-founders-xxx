import streamlit as st
import pandas as pd

def scraper_main():
    st.title("Email Scraper")
    uploaded_file = st.file_uploader("Upload Excel with 'Website' and 'Founder' columns", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if "Website" not in df.columns or "Founder" not in df.columns:
            st.error("The file must contain 'Website' and 'Founder' columns.")
            return
        df["Most Recommended"] = df["Founder"].apply(lambda name: f"{name.lower().split()[0]}@example.com")
        df["Other Options"] = df["Founder"].apply(lambda name: f"{name.lower().replace(' ', '.')}@example.com")
        df["Generic Emails"] = df["Website"].apply(lambda url: f"info@{url.replace('https://', '').replace('www.', '').split('/')[0]}")
        st.dataframe(df)
        st.download_button("Download Results", df.to_csv(index=False), file_name="email_results.csv", mime="text/csv")