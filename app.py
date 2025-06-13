import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="File Upload & Download", layout="centered")

st.title("📂 Upload Aspire CSV or Card Key Excel")

# Step 1: Upload the file
uploaded_file = st.file_uploader(
    "Upload your file (CSV or Excel)", 
    type=["csv", "xlsx"], 
    help="Accepted formats: .csv, .xlsx (Max 200MB)"
)

# Step 2: Read and display
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            st.error("Unsupported file format.")
            st.stop()

        st.success(f"✅ Uploaded `{uploaded_file.name}` successfully!")
        st.write("### 📊 Preview of uploaded data:")
        st.dataframe(df.head())

        # Step 3: Convert to CSV and allow download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name="processed_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload a CSV or Excel file to get started.")
