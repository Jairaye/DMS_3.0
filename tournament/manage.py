import streamlit as st
import pandas as pd
import math
import datetime
import re

def show_tournament_manage():
    st.title("🃏 Tournament Management")

    if "tournament_df" not in st.session_state or st.session_state.tournament_df is None:
        st.error("Tournament data not loaded. Please import it on the import page.")
        return

    df = st.session_state.tournament_df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 📅 Date & Time parsing
    if df["date"].dtype != "datetime64[ns]":
        df["date"] = pd.to_datetime(df["date"], unit="D", origin="1899-12-30")

    def safe_parse_time(val):
        try:
            return pd.to_datetime(str(val), errors="coerce").time()
        except:
            return None

    df["time"] = df["time"].apply(safe_parse_time)
    df["projection"] = pd.to_numeric(df["projection"], errors="coerce")

    # 🧬 Game Type tagging
    def classify_game(name):
        name = str(name).lower()
        mixed_tags = [
            "mixed", "razz", "stud", "plo", "omaha", "horse", "big o", "draw",
            "badugi", "limit", "triple", "dealer's choice", "eight game", "seven card"
        ]
        if any(tag in name for tag in mixed_tags):
            return "Mixed"
        return "Hold'em"

    df["game_type"] = df["event_name"].apply(classify_game)

    # ✋ Detect handedness
    def detect_handedness(row):
        name = str(row["event_name"]).lower()
        if "6-handed" in name or "6 max" in name:
            return 6
        if "8-handed" in name or "8 max" in name:
            return 8
        if row["game_type"] == "Mixed":
            if "triple draw" in name:
                return 6
            return 8
        return 9

    df["handedness"] = df.apply(detect_handedness, axis=1)

    # 🧮 Forecast dealers
    def forecast_dealers(projection, handedness):
        if pd.isnull(projection) or pd.isnull(handedness):
            return None
        est = projection / handedness * 1.175
        return int(math.ceil(est / 10) * 10)

    df["dealer_projection"] = df.apply(
        lambda row: forecast_dealers(row["projection"], row["handedness"]),
        axis=1
    )

    # 🔁 Restart detection via event number repetition or suffix
    df["event_number_str"] = df["event_number"].astype(str).str.strip()

    def base_event(ev):
        match = re.match(r"(\d+)", str(ev).strip())
        return match.group(1) if match else str(ev).strip()

    df["event_base"] = df["event_number_str"].apply(base_event)
    base_counts = df["event_base"].value_counts()
    df["is_restart"] = df["event_base"].apply(lambda x: base_counts.get(x, 0) > 1)

    # 🗂 Tabbed View
    tab1, tab2 = st.tabs(["🔵 Single-Day Events", "🔁 Restart Events"])

    # 🔵 Tab 1: Regular Events
    with tab1:
        single_df = df[df["is_restart"] == False]
        available_dates = sorted(single_df["date"].dt.date.dropna().unique())

        if available_dates:
            selected_day = st.date_input(
                "📅 Select Tournament Day",
                value=available_dates[0],
                min_value=available_dates[0],
                max_value=available_dates[-1],
                key="date_picker_single"
            )

            day_df = single_df[single_df["date"].dt.date == selected_day]
            st.subheader(f"📋 Events on {selected_day.strftime('%A, %B %d, %Y')}")

            editable_cols = [
                "time", "event_number", "event_name", "buy-in_amount",
                "projection", "dealer_projection", "game_type"
            ]

            edited_df = st.data_editor(
                day_df[editable_cols],
                column_config={
                    "projection": st.column_config.NumberColumn(disabled=False),
                    "dealer_projection": st.column_config.NumberColumn(disabled=True),
                    "time": st.column_config.TimeColumn(disabled=True),
                    "event_number": st.column_config.TextColumn(disabled=True),
                    "event_name": st.column_config.TextColumn(disabled=True),
                    "buy-in_amount": st.column_config.NumberColumn(disabled=True),
                    "game_type": st.column_config.TextColumn(disabled=True)
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_single_{selected_day}"
            )

            day_df.update(edited_df)
            day_df["projection"] = pd.to_numeric(day_df["projection"], errors="coerce")
            day_df["dealer_projection"] = day_df.apply(
                lambda row: forecast_dealers(row["projection"], row["handedness"]),
                axis=1
            )

            df.update(day_df)

            st.markdown("### 🔵 7-Day Regular Dealer Projection Summary")
            summary_days = [selected_day + datetime.timedelta(days=i) for i in range(7)]
            summary_data = []
            for day in summary_days:
                events = df[(df["is_restart"] == False) & (df["date"].dt.date == day)]
                total = events["dealer_projection"].sum(skipna=True)
                summary_data.append({
                    "Date": day.strftime("%Y-%m-%d"),
                    "Regular Dealers": int(total) if pd.notnull(total) else 0
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        else:
            st.warning("No single-day tournament dates available.")

    # 🔁 Tab 2: Restart Events
    with tab2:
        restart_df = df[df["is_restart"] == True]
        restart_dates = sorted(restart_df["date"].dt.date.dropna().unique())

        if restart_dates:
            selected_day_restart = st.date_input(
                "📅 Select Tournament Day",
                value=restart_dates[0],
                min_value=restart_dates[0],
                max_value=restart_dates[-1],
                key="date_picker_restart"
            )

            day_df = restart_df[restart_df["date"].dt.date == selected_day_restart]
            st.subheader(f"📋 Restart Events on {selected_day_restart.strftime('%A, %B %d, %Y')}")

            editable_cols = [
                "time", "event_number", "event_name", "buy-in_amount",
                "projection", "dealer_projection", "game_type"
            ]

            edited_df = st.data_editor(
                day_df[editable_cols],
                column_config={
                    "projection": st.column_config.NumberColumn(disabled=False),
                    "dealer_projection": st.column_config.NumberColumn(disabled=True),
                    "time": st.column_config.TimeColumn(disabled=True),
                    "event_number": st.column_config.TextColumn(disabled=True),
                    "event_name": st.column_config.TextColumn(disabled=True),
                    "buy-in_amount": st.column_config.NumberColumn(disabled=True),
                    "game_type": st.column_config.TextColumn(disabled=True)
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_restart_{selected_day_restart}"
            )

            day_df.update(edited_df)
            day_df["projection"] = pd.to_numeric(day_df["projection"], errors="coerce")
            day_df["dealer_projection"] = day_df.apply(
                lambda row: forecast_dealers(row["projection"], row["handedness"]),
                axis=1
            )

            df.update(day_df)

            st.markdown("### 🔁 7-Day Restart Dealer Projection Summary")
            summary_days = [selected_day_restart + datetime.timedelta(days=i) for i in range(7)]
            summary_data = []
            for day in summary_days:
                events = df[(df["is_restart"] == True) & (df["date"].dt.date == day)]
                total = events["dealer_projection"].sum(skipna=True)
                summary_data.append({
                    "Date": day.strftime("%Y-%m-%d"),
                    "Restart Dealers": int(total) if pd.notnull(total) else 0
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        else:
            st.warning("No restart tournament dates available.")