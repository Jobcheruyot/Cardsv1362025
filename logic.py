
import pandas as pd

def reconcile_cards(kcb_file, equity_file, aspire_file, key_file):
    # Load the Excel and CSV files
    kcb = pd.read_excel(kcb_file)
    equity = pd.read_excel(equity_file)
    aspire = pd.read_csv(aspire_file)
    key = pd.read_excel(key_file)

    # Standardize columns
    kcb.columns = kcb.columns.str.strip()
    equity.columns = equity.columns.str.strip()

    # Rename columns for consistency
    kcb = kcb.rename(columns={
        'Card No': 'Card_Number',
        'Trans Date': 'TRANS_DATE',
        'RRN': 'R_R_N',
        'Amount': 'Purchase',
        'Comm': 'Commission',
        'NetPaid': 'Settlement_Amount',
        'Merchant': 'store'
    })

    equity = equity.rename(columns={
        'Card Number': 'Card_Number',
        'DATE': 'TRANS_DATE',
        'RRN': 'R_R_N',
        'AMOUNT': 'Purchase',
        'Commission': 'Commission',
        'Net Paid': 'Settlement_Amount',
        'Merchant': 'store'
    })

    # Combine both banks
    kcb["Source"] = "KCB"
    equity["Source"] = "EQUITY"
    merged_cards = pd.concat([kcb, equity], ignore_index=True)

    # Clean 'store' for standardization
    merged_cards['store'] = merged_cards['store'].astype(str).str.strip().str.upper()
    key['Col_1'] = key['Col_1'].astype(str).str.strip().str.upper()

    # Map to branch names
    merged_cards = merged_cards.merge(key[['Col_1', 'Col_2']], how='left', left_on='store', right_on='Col_1')
    merged_cards.rename(columns={'Col_2': 'branch'}, inplace=True)
    merged_cards.drop(columns=['Col_1'], inplace=True)

    # Match Check
    merged_cards['card_check'] = merged_cards['Card_Number'].astype(str).str[:4] + merged_cards['Card_Number'].astype(str).str[-4:]
    aspire['card_check'] = aspire['CARD_NUMBER'].astype(str).str[:4] + aspire['CARD_NUMBER'].astype(str).str[-4:]

    aspire['rrn_check'] = aspire['REF_NO'].apply(lambda x: int(str(x).lstrip("0")) if pd.notna(x) else 0)

    # Merge based on RRN and card_check
    final = aspire.merge(
        merged_cards[['R_R_N', 'card_check', 'Purchase']],
        left_on=['rrn_check', 'card_check'],
        right_on=['R_R_N', 'card_check'],
        how='left'
    )

    final['val_check'] = final['AMOUNT'] - final['Purchase']
    return final
