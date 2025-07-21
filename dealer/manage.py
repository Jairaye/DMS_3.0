import streamlit as st
import pandas as pd

def show_dealer_management():
    st.title("🧍 Dealer Management")

    # Check if data was uploaded
    if "dealer_df" not in st.session_state or st.session_state.dealer_df is None:
        st.error("Dealer list not loaded. Please upload it on the import page.")
        return

    df = st.session_state.dealer_df

    # ---- 🔍 Lookup Section ----
    st.subheader("🔍 Lookup Dealer")
    search_by = st.selectbox("Search by:", ["ee_number", "nametag_id", "first_name", "last_name"])
    search_term = st.text_input(f"Enter {search_by}:")

    match_df = pd.DataFrame()
    if search_term:
        mask = df[search_by].astype(str).str.contains(search_term, case=False, na=False)
        match_df = df[mask]

    if not match_df.empty:
        st.success(f"Found {len(match_df)} match{'es' if len(match_df) > 1 else ''}.")
        selected = st.selectbox("Select a dealer to view/edit:", match_df[search_by].astype(str))
        dealer_row = match_df[match_df[search_by].astype(str) == selected].iloc[0]

        st.markdown("### Dealer Details")
        st.dataframe(pd.DataFrame(dealer_row).transpose())

        # ---- 📝 Edit Toggle ----
        st.markdown("#### ✏️ Edit This Dealer")
        with st.expander("Toggle to Edit Dealer Info"):
            updated = {}
            for col in df.columns:
                # Skip availability and ID fields if you want—this is customizable
                default = dealer_row[col]
                updated[col] = st.text_input(f"{col}", value=str(default))

            if st.button("Save Changes"):
                # Locate row in original df and update it
                row_index = df[df[search_by].astype(str) == selected].index[0]
                for col in df.columns:
                    df.at[row_index, col] = updated[col]
                st.session_state.dealer_df = df  # Save back to session
                st.success("Dealer info updated!")
                st.rerun()

    elif search_term:
        st.warning("No matching dealers found.")