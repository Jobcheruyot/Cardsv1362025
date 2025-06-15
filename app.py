import streamlit as st
import pandas as pd
from logic_v1 import process_cards

st.set_page_config(page_title="Card Reconciliation v1", layout="wide")
st.title("🧾 Card Transaction Reconciliation v1")

with st.sidebar:
    st.header("📥 Upload Files")
    kcb_file = st.file_uploader("KCB File (.xlsx)", type=["xlsx"], key="kcb")
    equity_file = st.file_uploader("Equity File (.xlsx)", type=["xlsx"], key="equity")
    aspire_file = st.file_uploader("Aspire File (.csv)", type=["csv"], key="aspire")
    key_file = st.file_uploader("Card Key File (.xlsx)", type=["xlsx"], key="key")

if kcb_file and equity_file and aspire_file and key_file:
    with st.spinner("Processing data..."):
        df = process_cards(kcb_file, equity_file, aspire_file, key_file)
    st.success("Reconciliation complete")

    st.download_button(
        label="Download Excel",
        data=df.to_excel(index=False, engine="openpyxl"),
        file_name="reconciliation_v1.xlsx",
    )
    st.dataframe(df)
else:
    st.info("Upload all required files to start")
