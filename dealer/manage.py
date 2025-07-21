import streamlit as st
import pandas as pd

def show_dealer_management():
    st.title("🧍 Dealer Management")

    # Check if data was uploaded
    if "dealer_df" not in st.session_state or st.session_state.dealer_df is None:
        st.error("Dealer list not loaded. Please upload it on the import page.")
        return

    df = st.session_state.dealer_df

    # ---- Lookup Section ----
    st.subheader("🔍 Lookup Dealer")
    search_by = st.selectbox("Search by:", ["ee_number", "nametag_id", "first_name", "last_name"])
    search_term = st.text_input(f"Enter {search_by}:")

    match_df = pd.DataFrame()
    if search_term:
        mask = df[search_by].astype(str).str.contains(search_term, case=False, na=False)
        match_df = df[mask]

    if not match_df.empty:
        st.success(f"Found {len(match_df)} match{'es' if len(match_df) > 1 else ''}.")

        # Build unique labels
        match_df = match_df.copy()
        match_df["label"] = match_df.apply(
            lambda row: f"{row['last_name']}, {row['first_name']} (EE# {row['ee_number']})", axis=1
        )
        selection = st.selectbox("Select a dealer to view/edit:", options=match_df["label"])

        # Get full dealer row based on label
        selected_dealer = match_df[match_df["label"] == selection].iloc[0]

        st.markdown("### Dealer Details")
        st.dataframe(pd.DataFrame(selected_dealer).transpose())

        # ---- 📝 Edit Section ----
    st.markdown("#### ✏️ Edit This Dealer")

    with st.form("edit_dealer_form"):
        st.markdown("**Core Info**")
        col1, col2, col3 = st.columns(3)
        updated_first = col1.text_input("First Name", value=selected_dealer["first_name"])
        updated_last = col2.text_input("Last Name", value=selected_dealer["last_name"])
        updated_ee = col3.text_input("EE Number", value=str(selected_dealer["ee_number"]))

        col4, col5 = st.columns(2)
        updated_nametag = col4.text_input("Nametag ID", value=selected_dealer["nametag_id"])
        updated_email = col5.text_input("Email", value=selected_dealer["email"])

        updated_phone = st.text_input("Phone", value=selected_dealer["phone"])

        # ---- Smart Select Inputs ----
        st.markdown("**Attributes**")
        attr1, attr2, attr3 = st.columns(3)
        updated_schedule = attr1.selectbox("Shift Type", ["DAY", "SWING"], index=0 if selected_dealer.get("schedule", "").upper() == "DAY" else 1)
        updated_ftpt = attr2.selectbox("FT/PT", ["Full-Time", "Part-Time"], index=0 if selected_dealer.get("ft_pt", "").lower().startswith("f") else 1)
        updated_group = attr3.selectbox("Dealer Group", ["ANY", "LIVE", "HOLDEM"], index=["ANY", "LIVE", "HOLDEM"].index(selected_dealer.get("dealer_group", "ANY").upper()))

        # ---- Availability Grid ----
        st.markdown("**Weekly Availability**")
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        day_cols = st.columns(7)
        avail_updates = {}

        for i, day in enumerate(days):
            field = f"AVAIL-{day}"
            current = str(selected_dealer.get(field, "YES")).strip().upper()
            avail_updates[field] = day_cols[i].checkbox(day, value=(current == "YES"))

        # ---- Submit Button ----
        submitted = st.form_submit_button("💾 Save Changes")
        if submitted:
            row_index = df[df["ee_number"].astype(str) == str(selected_dealer["ee_number"])].index[0]
            df.at[row_index, "first_name"] = updated_first
            df.at[row_index, "last_name"] = updated_last
            df.at[row_index, "ee_number"] = updated_ee
            df.at[row_index, "nametag_id"] = updated_nametag
            df.at[row_index, "email"] = updated_email
            df.at[row_index, "phone"] = updated_phone
            df.at[row_index, "schedule"] = updated_schedule
            df.at[row_index, "ft_pt"] = updated_ftpt
            df.at[row_index, "dealer_group"] = updated_group

            for field, value in avail_updates.items():
                df.at[row_index, field] = "YES" if value else "NO"

            st.session_state.dealer_df = df
            st.success("Dealer info updated successfully!")
            st.rerun()