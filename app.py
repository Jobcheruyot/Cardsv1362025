import streamlit as st
import pandas as pd
from logic import reconcile_cards

st.set_page_config(page_title="Card Reconciliation App", layout="wide")
st.title("🧾 Card Transaction Reconciliation")

with st.sidebar:
    st.header("📥 Upload Files")
    kcb_file = st.file_uploader("Upload KCB File (.xlsx)", type=["xlsx"], key="kcb")
    equity_file = st.file_uploader("Upload Equity File (.xlsx)", type=["xlsx"], key="equity")
    aspire_file = st.file_uploader("Upload Aspire File (.csv)", type=["csv"], key="aspire")
    key_file = st.file_uploader("Upload Card Key File (.xlsx)", type=["xlsx"], key="key")

if all([kcb_file, equity_file, aspire_file, key_file]):
    with st.spinner("🔄 Processing reconciliation..."):
        df = reconcile_cards(kcb_file, equity_file, aspire_file, key_file)
        st.success("✅ Reconciliation complete.")

        st.download_button(
            label="📥 Download Report as Excel",
            data=df.to_excel(index=False, engine='openpyxl'),
            file_name="Reconciliation_Report.xlsx"
        )
        st.dataframe(df)
else:
    st.info("Please upload all 4 files in the sidebar to begin.")
