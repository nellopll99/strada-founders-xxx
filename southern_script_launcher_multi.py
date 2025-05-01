
import streamlit as st

st.set_page_config(page_title="Southern Script Launcher", layout="centered")

st.title("🧭 Southern Script – Multi-Tool Launcher")
st.markdown("""
Welcome to **Southern Script**, your AI-powered productivity suite for Private Equity professionals.

Choose the tool you want to use:
- 📬 Contact Scraper (Email Finder)
- 🧠 AI PE Investor (Strategic Target Evaluator)
- 📝 AI NoteTaker (Meeting Assistant)
""")

tool = st.selectbox(
    "Select a module to continue:",
    ("-- Select --", "📬 Contact Scraper", "🧠 AI PE Investor", "📝 AI NoteTaker")
)

if tool == "📬 Contact Scraper":
    st.warning("Please select this page from the left sidebar.")

elif tool == "🧠 AI PE Investor":
    st.warning("Please select this page from the left sidebar.")

elif tool == "📝 AI NoteTaker":
    st.warning("Please select this page from the left sidebar.")

st.markdown("---")
st.caption("Built for Private Equity analysts, associates, and deal teams.")
