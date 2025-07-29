import streamlit as st
import pandas as pd
import calendar
from datetime import datetime


def show_calendar_view(daily_df, value_col):
    st.subheader("🗓 Monthly Calendar View")

    daily_df["Day"] = pd.to_datetime(daily_df["Day"])
    selected_month = st.selectbox(
        "Select Month:",
        sorted(set(daily_df["Day"].dt.strftime("%B %Y")))
    )

    dt_filter = datetime.strptime(selected_month, "%B %Y")
    month_df = daily_df[daily_df["Day"].dt.month == dt_filter.month]

    days_in_month = calendar.monthrange(dt_filter.year, dt_filter.month)[1]
    start_padding = calendar.monthrange(dt_filter.year, dt_filter.month)[0]
    calendar_data = [""] * start_padding

    for day in range(1, days_in_month + 1):
        d = datetime(dt_filter.year, dt_filter.month, day)
        val = month_df[month_df["Day"] == d][value_col].sum()
        if val != 0:
            val_int = int(round(val))
            display = f"**{day}**\n{val_int}"
        else:
            display = f"**{day}**"
        calendar_data.append(display)

    weeks = [calendar_data[i:i + 7] for i in range(0, len(calendar_data), 7)]
    for week in weeks:
        cols = st.columns(7)
        for idx, day_val in enumerate(week):
            with cols[idx]:
                st.markdown(
                    f"<div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 6px; font-size: 14px;'>{day_val}</div>",
                    unsafe_allow_html=True
                )


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
        single_df = df[df["is_restart"] == False].copy()
        time_window = st.radio("Time Window:", ["Total", "Day Shift", "Swing Shift"])

        # Extract start hour
        if "start_time" in single_df.columns:
            single_df["start_hour"] = pd.to_datetime(single_df["start_time"], errors="coerce").dt.hour

            if time_window == "Day Shift":
                single_df = single_df[single_df["start_hour"].between(7, 14)]
            elif time_window == "Swing Shift":
                single_df = single_df[single_df["start_hour"].between(15, 21)]

        weekly = single_df.groupby(["week", single_df["date"].dt.date])["dealer_projection"].sum().reset_index()
        weekly.columns = ["Week", "Day", "Projected Dealers"]
        st.dataframe(weekly, use_container_width=True)
        show_calendar_view(weekly, "Projected Dealers")

    else:
        restart_df = df[df["is_restart"] == True].copy()
        restart_df = restart_df.sort_values("date")
        taper_factors = [1.0, 0.5, 0.3, 0.1]

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
        show_calendar_view(weekly, "Adjusted Dealers")

    st.markdown("---")
    st.caption("Dealer projections are based on current tournament data and restart taper assumptions.")