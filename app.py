import streamlit as st
import pandas as pd
from io import BytesIO
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

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 Download Report as Excel",
            data=output.getvalue(),
            file_name="Reconciliation_Report.xlsx",
        )
        st.dataframe(df)
else:
    st.info("Please upload all 4 files in the sidebar to begin.")
