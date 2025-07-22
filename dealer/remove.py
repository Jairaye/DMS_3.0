import streamlit as st
import pandas as pd
import datetime

def show_remove_dealer():
    st.title("❌ Remove Dealer")

    if "dealer_df" not in st.session_state or st.session_state.dealer_df is None:
        st.error("Dealer list not loaded. Please upload it on the import page.")
        return

    df = st.session_state.dealer_df

    st.subheader("🔍 Search for Dealer to Remove")
    search_by = st.selectbox("Search by:", ["ee_number", "nametag_id", "first_name", "last_name"])
    search_term = st.text_input(f"Enter {search_by}:")

    match_df = pd.DataFrame()
    if search_term:
        mask = df[search_by].astype(str).str.contains(search_term, case=False, na=False)
        match_df = df[mask]

    if search_term and match_df.empty:
        st.warning("No matching dealers found.")

    elif not match_df.empty:
        match_df = match_df.copy()
        match_df["label"] = match_df.apply(
            lambda row: f"{row['last_name']}, {row['first_name']} (EE# {row['ee_number']})", axis=1
        )
        selected_label = st.selectbox("Select a dealer to remove:", match_df["label"])
        selected_dealer = match_df[match_df["label"] == selected_label].iloc[0]

        st.markdown("### Selected Dealer Info")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Name:** {selected_dealer['first_name']} {selected_dealer['last_name']}")
        col2.markdown(f"**EE Number:** {selected_dealer['ee_number']}")
        col3.markdown(f"**Nametag ID:** {selected_dealer['nametag_id']}")

        effective_date = st.date_input("Select effective removal date", value=datetime.date.today())
        confirm = st.checkbox("I understand that this will mark the dealer as removed on the selected date.")

        if st.button("❌ Confirm Removal") and confirm:
            row_index = df[df["ee_number"].astype(str) == str(selected_dealer["ee_number"])].index[0]
            df.at[row_index, "removal_effective_date"] = effective_date.isoformat()
            st.session_state.dealer_df = df
            st.success(
                f"Dealer {selected_dealer['first_name']} {selected_dealer['last_name']} marked for removal "
                f"(effective {effective_date.isoformat()})."
            )
            st.rerun()