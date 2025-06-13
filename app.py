import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Card Reconciliation V136", layout="wide")
st.title("💳 Final Cards Reconciliation App V136")

# --- Upload section ---
st.header("📂 Upload Files")
kcb_file = st.file_uploader("Upload KCB Excel File", type=["xlsx"])
equity_file = st.file_uploader("Upload Equity Excel File", type=["xlsx"])
aspire_file = st.file_uploader("Upload Aspire CSV File", type=["csv"])
key_file = st.file_uploader("Upload Card Key Excel File", type=["xlsx"])

if kcb_file and equity_file and aspire_file and key_file:
    try:
        # --- Load Data ---
        kcb = pd.read_excel(kcb_file)
        equity = pd.read_excel(equity_file)
        aspire = pd.read_csv(aspire_file)
        key = pd.read_excel(key_file)

        # --- Clean Column Names ---
        kcb.columns = kcb.columns.str.strip()
        equity.columns = equity.columns.str.strip()

        # --- Rename for consistency ---
        kcb = kcb.rename(columns={"Card No": "Card_Number", "Purchase Amount": "Purchase"})
        equity = equity.rename(columns={"Card No": "Card_Number", "Purchase Amount": "Purchase"})

        kcb["Source"] = "KCB"
        equity["Source"] = "EQUITY"

        # --- Combine bank data ---
        merged_cards = pd.concat([kcb, equity], ignore_index=True)
        merged_cards["Card_Number"] = merged_cards["Card_Number"].astype(str)
        merged_cards["card_check"] = merged_cards["Card_Number"].str[:4] + merged_cards["Card_Number"].str[-4:]

        # --- Drop duplicates ---
        merged_cards.drop_duplicates(inplace=True)

        # --- Map branches from Card Key ---
        merged_cards["store"] = merged_cards["store"].astype(str).str.strip().str.upper()
        key["Col_1"] = key["Col_1"].astype(str).str.strip().str.upper()

        merged_cards = merged_cards.merge(key[["Col_1", "Col_2"]], left_on="store", right_on="Col_1", how="left")
        merged_cards.rename(columns={"Col_2": "branch"}, inplace=True)
        merged_cards.drop(columns=["Col_1"], inplace=True)

        # --- Add Check_Two column ---
        merged_cards["branch"] = merged_cards["branch"].astype(str)
        merged_cards["Purchase"] = merged_cards["Purchase"].astype(str)
        merged_cards["Check_Two"] = merged_cards["branch"] + merged_cards["Purchase"]
        merged_cards["Check_Two"] = (
            merged_cards.groupby("Check_Two").cumcount() + 1
        ).astype(str) + merged_cards["Check_Two"]

        # --- Clean aspire & generate Check_Two ---
        aspire["Check_Two"] = aspire["STORE_NAME"].astype(str) + aspire["AMOUNT"].map('{:.2f}'.format)
        aspire["Check_Two"] = (
            aspire.groupby("Check_Two").cumcount() + 1
        ).astype(str) + aspire["Check_Two"]

        # --- Match transactions ---
        aspire_available = aspire["Check_Two"].tolist()
        def match_check(val):
            if val in aspire_available:
                aspire_available.remove(val)
                return "Okay"
            else:
                return "False"

        merged_cards["Amount_check"] = merged_cards["Check_Two"].apply(match_check)
        merged_cards["Cheked_rows"] = merged_cards["Amount_check"].apply(lambda x: "Yes" if x == "Okay" else "No")

        st.success("✅ Files processed successfully!")
        st.subheader("🔍 Reconciled Data Preview")
        st.dataframe(merged_cards.head(50))

        # --- Download processed file ---
        buffer = io.StringIO()
        merged_cards.to_csv(buffer, index=False)
        st.download_button(
            label="📥 Download Final Reconciled CSV",
            data=buffer.getvalue(),
            file_name="final_reconciled_cards.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error processing files: {e}")
else:
    st.warning("Please upload all 4 required files to proceed.")
