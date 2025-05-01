
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
    st.page_link("southern_script_v2.py", label="➡ Go to Contact Scraper")

elif tool == "🧠 AI PE Investor":
    st.page_link("ai_pe_investor.py", label="➡ Go to AI PE Investor")

elif tool == "📝 AI NoteTaker":
    st.page_link("southern_script_notetaker_live.py", label="➡ Go to AI NoteTaker")

st.markdown("---")
st.caption("Built for Private Equity analysts, associates, and deal teams.")
