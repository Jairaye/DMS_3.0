# auth.py
import streamlit as st

def authenticate_user():
    st.title("🔑 Dealer Management Login")
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == "admin123":  # Change to secure method later
            st.session_state.authenticated = True
        else:
            st.error("Incorrect password. Try again.")