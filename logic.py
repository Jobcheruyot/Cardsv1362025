
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

    # --- Build summary table similar to the notebook ---
    # Use unique store names from the aspire file
    card_summary = (
        aspire['STORE_NAME']
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
        .to_frame(name='STORE_NAME')
    )
    card_summary.index = card_summary.index + 1
    card_summary.reset_index(inplace=True)
    card_summary.rename(columns={'index': 'No'}, inplace=True)

    # Sum of amount per store from aspire
    aspire_sums = (
        aspire.groupby('STORE_NAME')['AMOUNT']
        .sum()
        .reset_index()
        .rename(columns={'AMOUNT': 'Aspire_Zed'})
    )
    card_summary = card_summary.merge(aspire_sums, on='STORE_NAME', how='left')

    # Sum of purchases by branch for KCB and Equity
    kcb_grouped = (
        merged_cards[merged_cards['Source'] == 'KCB']
        .groupby('branch')['Purchase']
        .sum()
        .reset_index()
        .rename(columns={'branch': 'STORE_NAME', 'Purchase': 'kcb_paid'})
    )
    card_summary = card_summary.merge(kcb_grouped, on='STORE_NAME', how='left')

    equity_grouped = (
        merged_cards[merged_cards['Source'] == 'EQUITY']
        .groupby('branch')['Purchase']
        .sum()
        .reset_index()
        .rename(columns={'branch': 'STORE_NAME', 'Purchase': 'equity_paid'})
    )
    card_summary = card_summary.merge(equity_grouped, on='STORE_NAME', how='left')

    # Fill NaNs with 0 for numeric columns
    numeric_cols = ['Aspire_Zed', 'kcb_paid', 'equity_paid']
    card_summary[numeric_cols] = card_summary[numeric_cols].fillna(0)

    # Compute totals
    card_summary['Gross_Banking'] = card_summary['kcb_paid'] + card_summary['equity_paid']
    card_summary['Variance'] = card_summary['Gross_Banking'] - card_summary['Aspire_Zed']

    totals = {
        'No': '',
        'STORE_NAME': 'TOTAL',
        'Aspire_Zed': card_summary['Aspire_Zed'].sum(),
        'kcb_paid': card_summary['kcb_paid'].sum(),
        'equity_paid': card_summary['equity_paid'].sum(),
        'Gross_Banking': card_summary['Gross_Banking'].sum(),
        'Variance': card_summary['Variance'].sum(),
    }
    card_summary = pd.concat([card_summary, pd.DataFrame([totals])], ignore_index=True)

    return card_summary
