import pandas as pd

def process_cards(kcb_file, equity_file, aspire_file, key_file):
    """Process card data from KCB, Equity and Aspire sources.

    Parameters
    ----------
    kcb_file : file-like object
        Excel file containing KCB card transactions.
    equity_file : file-like object
        Excel file containing Equity card transactions.
    aspire_file : file-like object
        CSV file exported from Aspire.
    key_file : file-like object
        Excel file mapping store names to branches.

    Returns
    -------
    pandas.DataFrame
        Combined dataframe with reconciliation information.
    """

    # Load data
    kcb = pd.read_excel(kcb_file)
    equity = pd.read_excel(equity_file)
    aspire = pd.read_csv(aspire_file)
    key = pd.read_excel(key_file)

    # Standardise column names
    kcb.columns = kcb.columns.str.strip()
    equity.columns = equity.columns.str.strip()
    key.columns = key.columns.str.strip()

    # Rename KCB columns
    kcb = kcb.rename(
        columns={
            "Card No": "Card_Number",
            "Trans Date": "TRANS_DATE",
            "RRN": "R_R_N",
            "Amount": "Purchase",
            "Comm": "Commission",
            "NetPaid": "Settlement_Amount",
            "Merchant": "store",
        }
    )

    # Rename Equity columns
    equity = equity.rename(
        columns={
            "Card Number": "Card_Number",
            "DATE": "TRANS_DATE",
            "RRN": "R_R_N",
            "AMOUNT": "Purchase",
            "Commission": "Commission",
            "Net Paid": "Settlement_Amount",
            "Merchant": "store",
        }
    )

    # Add helper columns
    kcb["Source"] = "KCB"
    equity["Source"] = "EQUITY"

    # Cash back if purchase is negative
    kcb["Cash_Back"] = kcb["Purchase"].apply(lambda x: -x if x < 0 else 0)
    equity["Cash_Back"] = equity["Purchase"].apply(lambda x: -x if x < 0 else 0)

    merged_cards = pd.concat([kcb, equity], ignore_index=True)

    # Normalise store column and map to branch
    merged_cards["store"] = (
        merged_cards["store"].astype(str).str.strip().str.upper()
    )
    key["Col_1"] = key["Col_1"].astype(str).str.strip().str.upper()

    merged_cards = merged_cards.merge(
        key[["Col_1", "Col_2"]], how="left", left_on="store", right_on="Col_1"
    )
    merged_cards.rename(columns={"Col_2": "branch"}, inplace=True)
    merged_cards.drop(columns=["Col_1"], inplace=True)

    # card_check helper
    def _card_check(x: str) -> str:
        x = str(x).replace(" ", "").replace("*", "")
        return x[:4] + x[-4:] if len(x) >= 8 else ""

    merged_cards["card_check"] = merged_cards["Card_Number"].apply(_card_check)
    aspire["card_check"] = aspire["CARD_NUMBER"].apply(_card_check)

    # rrn_check from REF_NO
    aspire["rrn_check"] = aspire["REF_NO"].apply(
        lambda x: int(str(x).lstrip("0")) if pd.notna(x) and str(x).strip() else 0
    )

    # Merge on RRN and card_check
    final = aspire.merge(
        merged_cards[["R_R_N", "card_check", "Purchase", "branch", "Source"]],
        left_on=["rrn_check", "card_check"],
        right_on=["R_R_N", "card_check"],
        how="left",
    )

    final["val_check"] = final["AMOUNT"] - final["Purchase"]
    return final