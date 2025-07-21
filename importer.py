# importer.py
import streamlit as st

def show_import_page():
    st.title("📥 Import Page")
    st.info("This page will allow data upload and validation later.")
    st.file_uploader("Upload dealer list (CSV):", type=["csv"])