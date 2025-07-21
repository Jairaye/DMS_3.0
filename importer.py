import streamlit as st
import pandas as pd

# ---- HARD-CODED SCHEMA ----
DEALER_COLUMNS = [
    "first_name", "last_name", "nametag_id", "ee_number", "email", "phone", "ft_pt", "shift_type",
    "dealer_group", "AVAIL-SUN", "AVAIL-MON", "AVAIL-TUE", "AVAIL-WED",
    "AVAIL-THU", "AVAIL-FRI", "AVAIL-SAT"
]

TOURNAMENT_COLUMNS = [
    "Date", "Time", "Event Number", "Event Name",
    "Buy-in Amount", "Starting Chips", "Projection", "Longest Break (Dinner Break)"
]

def show_import_page():
    st.title("📥 Import Dealer System Data")
    st.markdown("Upload all applicable files. You may proceed without some, but certain features will be disabled.")

    # Initialize placeholders
    if "dealer_df" not in st.session_state:
        st.session_state.dealer_df = None
    if "tournament_df" not in st.session_state:
        st.session_state.tournament_df = None
    if "employee_df" not in st.session_state:
        st.session_state.employee_df = None

    # ---- Dealer Upload ----
    st.subheader("🧍 Dealer List")
    dealer_file = st.file_uploader("Upload Dealer List (.csv or .xlsx)", type=["csv", "xlsx"], key="dealer")
    if dealer_file:
        try:
            df = pd.read_csv(dealer_file) if dealer_file.name.endswith(".csv") else pd.read_excel(dealer_file)
            missing = [col for col in DEALER_COLUMNS if col not in df.columns]
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
            else:
                st.success("✅ Dealer List uploaded successfully.")
                st.session_state.dealer_df = df
                st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error loading Dealer List: {e}")

    # ---- Tournament Upload ----
    st.subheader("♠️ Tournament Schedule")
    tourney_file = st.file_uploader("Upload Tournament Schedule (.csv or .xlsx)", type=["csv", "xlsx"], key="tourney")
    if tourney_file:
        try:
            df = pd.read_csv(tourney_file) if tourney_file.name.endswith(".csv") else pd.read_excel(tourney_file)
            missing = [col for col in TOURNAMENT_COLUMNS if col not in df.columns]
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
            else:
                st.success("✅ Tournament Schedule uploaded successfully.")
                st.session_state.tournament_df = df
                st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error loading Tournament Schedule: {e}")

    # ---- Employee Upload (No Schema Yet) ----
    st.subheader("👥 Employee Schedule")
    employee_file = st.file_uploader("Upload Employee Schedule (.csv or .xlsx)", type=["csv", "xlsx"], key="employee")
    if employee_file:
        try:
            df = pd.read_csv(employee_file) if employee_file.name.endswith(".csv") else pd.read_excel(employee_file)
            st.success("✅ Employee Schedule uploaded.")
            st.session_state.employee_df = df
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error loading Employee Schedule: {e}")

    # ---- Continue Button ----
    st.divider()
    if st.button("Proceed to System"):
        st.session_state.data_loaded = True
        st.rerun()

    # ---- Warning if Missing ----
    if st.session_state.dealer_df is None or st.session_state.tournament_df is None:
        missing = []
        if not st.session_state.dealer_df:
            missing.append("Dealer List")
        if not st.session_state.tournament_df:
            missing.append("Tournament Schedule")
        st.warning(f"Missing: {', '.join(missing)}. Related features will be unavailable.")