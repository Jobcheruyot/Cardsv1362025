import streamlit as st
import pandas as pd
import io

st.title("🧾 Upload Aspire CSV or Card Key Excel")

# ✅ Step 1: File uploader for both CSV and XLSX
uploaded_file = st.file_uploader(
    "Upload Aspire CSV or Card Key Excel", 
    type=["csv", "xlsx"],
    help="Only .csv or .xlsx files allowed (max 200MB)"
)

# ✅ Step 2: Process file and provide download
if uploaded_file is not None:
    file_name = uploaded_file.name

    try:
        # ✅ Detect file type and load data
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.success(f"CSV file '{file_name}' uploaded and read successfully.")
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            st.success(f"Excel file '{file_name}' uploaded and read successfully.")
        else:
            st.error("Unsupported file format. Only CSV and XLSX are allowed.")
            df = None

        # ✅ Preview data
        if df is not None:
            st.write("### Preview of uploaded data:")
            st.dataframe(df.head())

            # ✅ Convert to CSV for download
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            st.download_button(
                label="📥 Download Processed CSV",
                data=csv_data,
                file_name="processed_data.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("Please upload a CSV or Excel (.xlsx) file.")
