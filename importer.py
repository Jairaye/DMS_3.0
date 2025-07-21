import streamlit as st
import pandas as pd

def show_import_page():
    st.title("📥 Data Import Setup")
    st.markdown("Please upload the following files. All are optional, but missing files may limit functionality.")

    # Initialize session storage for datasets
    if "dealer_df" not in st.session_state:
        st.session_state.dealer_df = None
    if "tournament_df" not in st.session_state:
        st.session_state.tournament_df = None
    if "employee_df" not in st.session_state:
        st.session_state.employee_df = None

    # --------------------------
    # 🧍 Dealer List Upload
    # --------------------------
    st.header("🧍 Dealer List")
    dealer_file = st.file_uploader("Upload Dealer List (.csv or .xlsx)", type=["csv", "xlsx"])

    if dealer_file is not None:
        try:
            dealer_df = pd.read_csv(dealer_file) if dealer_file.name.endswith(".csv") else pd.read_excel(dealer_file)
            st.session_state.dealer_df = dealer_df
            st.success("Dealer List loaded successfully!")
            st.dataframe(dealer_df.head())
        except Exception as e:
            st.error(f"Dealer List error: {e}")

    # --------------------------
    # ♠️ Tournament Schedule Upload
    # --------------------------
    st.header("♠️ Tournament Schedule")
    tourney_file = st.file_uploader("Upload Tournament Schedule (.csv or .xlsx)", type=["csv", "xlsx"])

    if tourney_file is not None:
        try:
            tourney_df = pd.read_csv(tourney_file) if tourney_file.name.endswith(".csv") else pd.read_excel(tourney_file)
            st.session_state.tournament_df = tourney_df
            st.success("Tournament Schedule loaded successfully!")
            st.dataframe(tourney_df.head())
        except Exception as e:
            st.error(f"Tournament Schedule error: {e}")

    # --------------------------
    # 👥 Employee Schedule Upload
    # --------------------------
    st.header("👥 Employee Schedule")
    employee_file = st.file_uploader("Upload Employee Schedule (.csv or .xlsx)", type=["csv", "xlsx"])

    if employee_file is not None:
        try:
            employee_df = pd.read_csv(employee_file) if employee_file.name.endswith(".csv") else pd.read_excel(employee_file)
            st.session_state.employee_df = employee_df
            st.success("Employee Schedule loaded successfully!")
            st.dataframe(employee_df.head())
        except Exception as e:
            st.error(f"Employee Schedule error: {e}")

    # --------------------------
    # ✅ Continue Button
    # --------------------------
    st.divider()
    if st.button("Proceed to System"):
        st.session_state.data_loaded = True
        st.experimental_rerun()

    # 🛑 Advisory if any data is missing
    missing = []
    if st.session_state.dealer_df is None:
        missing.append("Dealer List")
    if st.session_state.tournament_df is None:
        missing.append("Tournament Schedule")
    if st.session_state.employee_df is None:
        missing.append("Employee Schedule")

    if missing:
        st.warning(f"The following files were not uploaded: {', '.join(missing)}. Some features may be unavailable.")