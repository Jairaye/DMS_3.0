import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os
import re


def format_date(d):
    fmt = '%-m/%-d' if os.name != 'nt' else '%m/%d'
    return d.strftime(fmt)


def show_calendar_view(daily_df, value_col):
    st.subheader("🗓 Monthly Calendar View")

    daily_df["Day"] = pd.to_datetime(daily_df["Day"])
    month_options = sorted(set(daily_df["Day"].dt.strftime("%B %Y")))
    if not month_options:
        st.warning("No valid dates found for calendar view.")
        return

    selected_month = st.selectbox("Select Month:", month_options, index=0)
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


def show_summary_metrics(daily_df, value_col):
    st.subheader("🔍 Summary Stats")

    if daily_df.empty:
        st.info("No data for selected time window.")
        return

    df = daily_df.copy()
    df["Day"] = pd.to_datetime(df["Day"])

    avg = df[value_col].mean()
    max_row = df.loc[df[value_col].idxmax()]
    min_row = df.loc[df[value_col].idxmin()]

    df["week_num"] = df["Day"].dt.isocalendar().week
    week_groups = df.groupby("week_num")

    def get_week_range(g):
        days = sorted(g["Day"])
        if len(days) == 0:
            return "N/A"
        return f"{format_date(days[0])}–{format_date(days[-1])}"

    weekly_sums = week_groups[value_col].sum()
    busiest_week_num = weekly_sums.idxmax()
    lightest_week_num = weekly_sums.idxmin()

    busiest_label = get_week_range(week_groups.get_group(busiest_week_num))
    lightest_label = get_week_range(week_groups.get_group(lightest_week_num))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Average Dealers per Day", f"{avg:.1f}")
        st.metric("📈 Busiest Week", f"{busiest_label} ({int(weekly_sums[busiest_week_num])})")
        st.metric("📉 Lightest Week", f"{lightest_label} ({int(weekly_sums[lightest_week_num])})")

    with col2:
        st.metric("🔺 Max Day", f"{max_row['Day'].strftime('%b %d')} ({int(max_row[value_col])})")
        st.metric("🔻 Min Day", f"{min_row['Day'].strftime('%b %d')} ({int(min_row[value_col])})")


def show_single_day_metrics(df):
    st.subheader("🗓 Single-Day Scheduling Metrics")

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "date" not in df.columns or "time" not in df.columns or "projection" not in df.columns:
        st.warning("Missing required columns: date, time, projection")
        return

    df["is_restart"] = df["event_number"].astype(str).str.contains("r", case=False)
    single_df = df[df["is_restart"] == False].copy()

    shift = st.radio("Time Window:", ["Total", "Day Shift", "Swing Shift"])
    single_df["start_hour"] = pd.to_datetime(single_df["time"], format="%H:%M:%S", errors="coerce").dt.hour

    if shift == "Day Shift":
        single_df = single_df[single_df["start_hour"].between(7, 14)]
    elif shift == "Swing Shift":
        single_df = single_df[single_df["start_hour"].between(15, 21)]

    single_df["Day"] = pd.to_datetime(single_df["date"]).dt.date
    single_df["Week"] = pd.to_datetime(single_df["date"]).dt.isocalendar().week

    weekly = single_df.groupby(["Week", "Day"])["dealer_projection"].sum().reset_index()
    weekly.columns = ["Week", "Day", "Projected Dealers"]

    st.dataframe(weekly, use_container_width=True)
    show_calendar_view(weekly, "Projected Dealers")
    show_summary_metrics(weekly, "Projected Dealers")


def show_restart_metrics(df):
    st.subheader("🔁 Restart Scheduling Metrics")

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "date" not in df.columns or "event_number" not in df.columns or "dealer_projection" not in df.columns:
        st.warning("Missing required columns for restart metrics.")
        return

    # Use base event logic to identify restarts
    df["event_number_str"] = df["event_number"].astype(str).str.strip()

    def base_event(ev):
        match = re.match(r"(\d+)", str(ev).strip())
        return match.group(1) if match else str(ev).strip()

    df["event_base"] = df["event_number_str"].apply(base_event)
    base_counts = df["event_base"].value_counts()
    df["is_restart"] = df["event_base"].apply(lambda x: base_counts.get(x, 0) > 1)

    restart_df = df[df["is_restart"] == True].copy()

    restart_df["Day"] = pd.to_datetime(restart_df["date"]).dt.date
    restart_df["Week"] = pd.to_datetime(restart_df["date"]).dt.isocalendar().week

    weekly = restart_df.groupby(["Week", "Day"])["dealer_projection"].sum().reset_index()
    weekly.columns = ["Week", "Day", "Restart Dealer Load"]

    st.dataframe(weekly, use_container_width=True)
    show_summary_metrics(weekly, "Restart Dealer Load")

    st.markdown("### 🔍 Restart Lineage Explorer")

    # Step 1: Get all base events with restarts
    restart_df["event_number_str"] = restart_df["event_number"].astype(str).str.strip()

    def base_event(ev):
        match = re.match(r"(\d+)", str(ev).strip())
        return match.group(1) if match else str(ev).strip()

    restart_df["event_base"] = restart_df["event_number_str"].apply(base_event)
    base_events = sorted(restart_df["event_base"].unique())

    selected_base = st.selectbox("Select Base Event Number:", base_events)

    lineage_df = df[df["event_base"] == selected_base].copy()
    lineage_df["Day"] = pd.to_datetime(lineage_df["date"]).dt.date
    lineage_df = lineage_df.sort_values("date")

    st.markdown(f"#### Events for Base `{selected_base}`")
    display_cols = [
        "Day", "time", "event_number", "event_name", "projection", "dealer_projection", "game_type"
    ]
    st.dataframe(lineage_df[display_cols], use_container_width=True)


def show_scheduling_metrics():
    st.title("📊 Scheduling Metrics")

    if "tournament_df" not in st.session_state or st.session_state.tournament_df is None:
        st.error("Tournament data not loaded. Please import it on the import page.")
        return

    df = st.session_state.tournament_df.copy()

    tab1, tab2 = st.tabs(["Single-Day Metrics", "Restart Metrics"])
    with tab1:
        show_single_day_metrics(df)
    with tab2:
        show_restart_metrics(df)

    st.markdown("---")
    st.caption("Dealer projections are based on current tournament data and scheduling assumptions.")