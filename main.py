# main.py
import streamlit as st
from auth import authenticate_user
from importer import show_import_page
from dealer.manage import show_dealer_management
from dealer.uniform import show_uniform_return
from scheduler.shifts import show_shift_swap
from scheduler.carpool import show_carpool_management
from scheduler.temp_adjustments import show_temp_adjustments
from tournament.forecast import show_forecasting

st.set_page_config(page_title="Dealer Management System", layout="wide")

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Login"

# ----------------------
# Authentication section
# ----------------------
if not st.session_state.authenticated:
    authenticate_user()  # Auth function will set authenticated state
    st.stop()

# ----------------------
# Navigation sidebar
# ----------------------
st.sidebar.title("🔧 Navigation")
page_options = [
    "Import Data",
    "Dealer Management",
    "Uniform Return",
    "Schedule Management",
    "Tournament Forecasting"
]
selected_page = st.sidebar.radio("Go to:", page_options)

# ----------------------
# Page routing
# ----------------------
if selected_page == "Import Data":
    show_import_page()

elif selected_page == "Dealer Management":
    show_dealer_management()

elif selected_page == "Uniform Return":
    show_uniform_return()

elif selected_page == "Schedule Management":
    st.subheader("🚗 Schedule Management")
    subtab = st.radio("Choose a task:", ["Shift Swap", "Carpool", "Temporary Adjustments"])
    if subtab == "Shift Swap":
        show_shift_swap()
    elif subtab == "Carpool":
        show_carpool_management()
    else:
        show_temp_adjustments()

elif selected_page == "Tournament Forecasting":
    show_forecasting()