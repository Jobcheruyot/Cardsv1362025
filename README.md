# Cardsv1362025

This repository provides a simple Streamlit application for reconciling card
transactions from multiple sources. The logic mirrors the calculations in
`FinalCards_V1362025_1_07.ipynb` and outputs a summary table per store.

## Running the app

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit server:

   ```bash
   streamlit run app.py
   ```

3. Upload the four required files (KCB, Equity, Aspire and the card key) using
   the sidebar and download the generated Excel report when processing
   completes.
