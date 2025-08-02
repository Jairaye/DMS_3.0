# main.py
import streamlit as st

# Import setup and routing modules
from auth import authenticate_user
from importer import show_import_page
from dealer.manage import show_dealer_management
from dealer.add import show_add_dealer
from dealer.remove import show_remove_dealer
from dealer.uniform import show_uniform_return
from scheduler.shifts import show_shift_swap
from scheduler.carpool import show_carpool_management
from scheduler.temp_adjustments import show_temp_adjustments
from tournament.manage import show_tournament_manage
from scheduler.metrics import show_scheduling_metrics
from schedule import run_schedule_builder  # ✅ New import

# ----------------------
# 🧭 Streamlit Config
# ----------------------
st.set_page_config(page_title="Dealer Management System", layout="wide")

# ----------------------
# 🧠 Session Initialization
# ----------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# ----------------------
# 🔐 Phase 1: Login Page
# ----------------------
if not st.session_state.authenticated:
    authenticate_user()
    st.stop()

# ----------------------
# 📥 Phase 2: Import Page
# ----------------------
if not st.session_state.data_loaded:
    show_import_page()
    st.stop()

# ----------------------
# 🧭 Phase 3: Navigation UI
# ----------------------
st.sidebar.title("🔧 Navigation")

page_options = [
    "Dealer Management",
    "Add Dealer",
    "Remove Dealer",
    "Uniform Return",
    "Schedule Management",
    "Tournament Management",
    "Scheduling Metrics",
    "Schedule Generation"  # ✅ Added missing comma above
]

selected_page = st.sidebar.radio("Go to:", page_options)

# ----------------------
# 📦 Page Routing
# ----------------------
if selected_page == "Dealer Management":
    show_dealer_management()

elif selected_page == "Add Dealer":
    show_add_dealer()

elif selected_page == "Remove Dealer":
    show_remove_dealer()

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

elif selected_page == "Tournament Management":
    show_tournament_manage()

elif selected_page == "Scheduling Metrics":
    show_scheduling_metrics()

elif selected_page == "Schedule Generation":  # ✅ New route
    run_schedule_builder()