
import streamlit as st
import pandas as pd
from logic import reconcile_cards

st.set_page_config(page_title="Card Reconciliation App", layout="wide")

st.title("🧾 Card Transaction Reconciliation Tool")

with st.sidebar:
    st.header("📁 Upload Required Files")
    kcb_file = st.file_uploader("Upload KCB Excel", type=["xlsx"])
    equity_file = st.file_uploader("Upload Equity Excel", type=["xlsx"])
    aspire_file = st.file_uploader("Upload Aspire CSV", type=["csv"])
    key_file = st.file_uploader("Upload Card Key Excel", type=["xlsx"])

if all([kcb_file, equity_file, aspire_file, key_file]):
    with st.spinner("Processing and reconciling transactions..."):
        df = reconcile_cards(kcb_file, equity_file, aspire_file, key_file)
        st.success("✅ Reconciliation Complete")

        st.download_button("📥 Download Reconciliation Report", df.to_excel(index=False, engine='openpyxl'), file_name="Reconciliation_Report.xlsx")

        st.dataframe(df)
else:
    st.info("Please upload all required files from the sidebar to begin.")
