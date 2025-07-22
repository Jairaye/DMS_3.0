import streamlit as st
import pandas as pd
import datetime

def show_uniform_return():
    st.title("👕 Uniform Return")

    if "dealer_df" not in st.session_state or st.session_state.dealer_df is None:
        st.error("Dealer list not loaded. Please upload it on the import page.")
        return

    df = st.session_state.dealer_df.copy()

    # -----------------------------------
    # 🔍 Dealer Lookup
    # -----------------------------------
    st.subheader("Lookup Dealer")
    search_by = st.selectbox("Search by:", ["ee_number", "first_name", "last_name"])
    search_term = st.text_input(f"Enter {search_by}:")

    match_df = pd.DataFrame()
    if search_term:
        mask = df[search_by].astype(str).str.contains(search_term, case=False, na=False)
        match_df = df[mask]

    if search_term and match_df.empty:
        st.warning("No matching dealers found.")

    elif not match_df.empty:
        match_df["label"] = match_df.apply(
            lambda row: f"{row['last_name']}, {row['first_name']} (EE# {row['ee_number']})", axis=1
        )
        selected_label = st.selectbox("Select dealer:", match_df["label"])
        selected_dealer = match_df[match_df["label"] == selected_label].iloc[0]

        row_index = df[df["ee_number"].astype(str) == str(selected_dealer["ee_number"])].index[0]
        # 🧾 Check for prior return
    already_returned = pd.notnull(selected_dealer.get("uniform_return_date")) and str(selected_dealer.get("uniform_return_date")).strip()

    if already_returned:
        confirm_id = selected_dealer.get("uniform_return_confirm_id", "N/A")
        return_date = selected_dealer.get("uniform_return_date", "N/A")
        st.success(f"✅ Shirt was already returned on {return_date} — Confirmation #{confirm_id}")
    else:
        with st.form("uniform_return_form"):
            submitted = st.form_submit_button("✅ Confirm Shirt Return")
            ...

        st.markdown("### Selected Dealer Info")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Name:** {selected_dealer['first_name']} {selected_dealer['last_name']}")
        col2.markdown(f"**EE Number:** {selected_dealer['ee_number']}")
        col3.markdown(f"**Shift Type:** {selected_dealer.get('shift_type', 'N/A')}")

        removal_date = selected_dealer.get("removal_effective_date", "")
        if removal_date and str(removal_date).strip():
            st.info(f"⚠️ This dealer is marked for removal on {removal_date}.")

        with st.form("uniform_return_form"):
            submitted = st.form_submit_button("✅ Confirm Shirt Return")

            if submitted:
                for col in ["uniform_return_date", "uniform_return_items", "uniform_return_confirm_id"]:
                    if col not in df.columns:
                        df[col] = ""

                confirm_id = pd.to_datetime("now").strftime("%m%d%H%M")
                return_date = datetime.date.today().isoformat()

                df.at[row_index, "uniform_return_date"] = return_date
                df.at[row_index, "uniform_return_items"] = "Shirt"
                df.at[row_index, "uniform_return_confirm_id"] = confirm_id

                st.session_state.dealer_df = df
                st.success(f"🧾 Shirt return logged — Confirmation #{confirm_id}")
                st.rerun()

    # -----------------------------------
    # 📋 Missing Shirt Return Report
    # -----------------------------------
    st.markdown("---")
    st.subheader("📝 Missing Uniform Returns")

    show_removed = st.checkbox("Include removed dealers", value=False)

    report_df = st.session_state.dealer_df.copy()

    if not show_removed and "removal_effective_date" in report_df.columns:
        report_df = report_df[report_df["removal_effective_date"].isna()]

    if "uniform_return_date" not in report_df.columns:
        report_df["uniform_return_date"] = ""
    if "uniform_return_items" not in report_df.columns:
        report_df["uniform_return_items"] = ""

    missing_df = report_df[
        (report_df["uniform_return_date"] == "") &
        (report_df["uniform_return_items"] == "")
    ]

    if missing_df.empty:
        st.success("✅ All dealers have logged their shirt return.")
    else:
        st.caption(f"{len(missing_df)} dealer(s) have not returned their shirt.")
        st.dataframe(
            missing_df[["first_name", "last_name", "ee_number", "shift_type", "dealer_group"]],
            use_container_width=True
        )

        csv = missing_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Report", data=csv, file_name="missing_shirt_returns.csv", mime="text/csv")