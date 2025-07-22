import streamlit as st
import pandas as pd

def show_add_dealer():
    st.title("➕ Add New Dealer")

    if "dealer_df" not in st.session_state or st.session_state.dealer_df is None:
        st.error("Dealer list not loaded. Please upload it on the import page.")
        return

    df = st.session_state.dealer_df

    with st.form("add_dealer_form"):
        st.markdown("**Core Info**")
        col1, col2, col3 = st.columns(3)
        first_name = col1.text_input("First Name")
        last_name = col2.text_input("Last Name")
        ee_number = col3.text_input("EE Number")

        col4, col5 = st.columns(2)
        nametag_id = col4.text_input("Nametag ID")
        email = col5.text_input("Email")
        phone = st.text_input("Phone")

        st.markdown("**Attributes**")
        attr1, attr2, attr3 = st.columns(3)
        ft_pt = attr1.selectbox("FT/PT", ["Full-Time", "Part-Time"])
        shift_type = attr2.selectbox("Shift Type", ["DAY", "SWING"])
        dealer_group = attr3.selectbox("Dealer Group", ["ANY", "LIVE", "HOLDEM"])

        st.markdown("**Weekly Availability**")
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        day_cols = st.columns(7)
        availability = {}
        for i, day in enumerate(days):
            availability[f"AVAIL-{day}"] = day_cols[i].checkbox(day, value=True)

        submitted = st.form_submit_button("➕ Add Dealer")

        if submitted:
            # Validate required fields
            if not first_name or not last_name or not ee_number:
                st.warning("First name, last name, and EE number are required.")
                return

            # Check for duplicates
            exists_by_ee = ee_number in df["ee_number"].astype(str).values
            exists_by_tag = nametag_id in df["nametag_id"].astype(str).values
            if exists_by_ee or exists_by_tag:
                st.error("Dealer with this EE Number or Nametag ID already exists.")
                return

            new_dealer = {
                "first_name": first_name,
                "last_name": last_name,
                "ee_number": ee_number,
                "nametag_id": nametag_id,
                "email": email,
                "phone": phone,
                "ft_pt": ft_pt,
                "shift_type": shift_type,
                "dealer_group": dealer_group
            }
            new_dealer.update({day: "YES" if val else "NO" for day, val in availability.items()})

            # Append and save
            st.session_state.dealer_df = pd.concat([df, pd.DataFrame([new_dealer])], ignore_index=True)
            st.success(f"Dealer {first_name} {last_name} added successfully!")
            st.rerun()