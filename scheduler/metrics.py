import streamlit as st
import pandas as pd

def show_scheduling_metrics():
    st.title("📊 Scheduling Metrics")

    if "tournament_df" not in st.session_state or st.session_state.tournament_df is None:
        st.error("Tournament data not loaded. Please import it on the import page.")
        return

    df = st.session_state.tournament_df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "date" not in df.columns or "dealer_projection" not in df.columns:
        st.warning("Tournament data missing required columns.")
        return

    # 🗂 Split regular and restart events
    df["is_restart"] = df["event_number"].astype(str).str.contains("R", case=False)
    df["week"] = df["date"].dt.isocalendar().week

    st.subheader("📅 Weekly Dealer Forecast")

    view_type = st.radio("Event Type:", ["Single-Day", "Restart"])

    if view_type == "Single-Day":
        single_df = df[df["is_restart"] == False]
        weekly = single_df.groupby(["week", df["date"].dt.date])["dealer_projection"].sum().reset_index()
        weekly.columns = ["Week", "Day", "Projected Dealers"]
        st.dataframe(weekly, use_container_width=True)

    else:  # 🔁 Restart taper logic
        restart_df = df[df["is_restart"] == True].copy()
        restart_df = restart_df.sort_values("date")
        taper_factors = [1.0, 0.6, 0.6, 0.55]

        def apply_taper(group):
            group = group.copy()
            for i in range(len(group)):
                factor = taper_factors[min(i, len(taper_factors) - 1)]
                group.iloc[i, group.columns.get_loc("dealer_projection")] *= factor
            return group

        restart_df["event_base"] = restart_df["event_number"].str.extract(r"(\d+)")
        grouped = restart_df.groupby("event_base", group_keys=False).apply(apply_taper)
        grouped["adjusted_dealer_projection"] = grouped["dealer_projection"].round().astype(int)

        weekly = grouped.groupby(["week", grouped["date"].dt.date])["adjusted_dealer_projection"].sum().reset_index()
        weekly.columns = ["Week", "Day", "Adjusted Dealers"]
        st.dataframe(weekly, use_container_width=True)

    st.markdown("---")
    st.caption("Dealer projections are based on current tournament data and restart taper assumptions.")