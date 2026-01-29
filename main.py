import streamlit as st
import pandas as pd
import consolidateScript  # your consolidation logic

st.title("My LLFSI Projects")

# Tabs for features
tab1, tab2 = st.tabs(["Consolidation", "BIR PDF Filler"])

# --- Tab 1: Consolidation workflow ---
with tab1:
    st.header("Use Case: Import → Run → Export")

    # Step 1: Import
    uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx"])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        # Step 2: Run
        if st.button("Run Consolidation"):
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Call your function
            result_df = consolidateScript.consolidate_inventory(temp_path)

            st.success("Consolidation complete!")
            st.dataframe(result_df)  # show results in the app

            # Step 3: Export
            # Provide download link for processed file
            processed_file = f"processed_{uploaded_file.name}"
            result_df.to_excel(processed_file, index=False)

            with open(processed_file, "rb") as f:
                st.download_button(
                    label="Download Processed File",
                    data=f,
                    file_name=processed_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# --- Tab 2: Placeholder ---
with tab2:
    st.header("Future Feature")
    st.write("This is a placeholder for another feature.")
    st.info("Coming soon...")