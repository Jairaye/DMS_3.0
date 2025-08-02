import pandas as pd
import streamlit as st
import datetime

# ---- Helper: Standard Eligibility ----
def get_eligible_dealers(dealers_df, tournament, scheduled_dealers):
    # Normalize dealer column names
    dealers_df.columns = dealers_df.columns.str.strip().str.lower()

    start_hour = tournament["time"].hour
    game_type = tournament["event_name"].lower()
    tournament_date = tournament["date"]

    # Remove already scheduled dealers
    already_scheduled = set()
    for dealer_list in scheduled_dealers.values():
        already_scheduled.update(dealer_list)
    unscheduled = dealers_df[~dealers_df["ee_number"].isin(already_scheduled)]

    # Filter by availability
    weekday_abbr = pd.to_datetime(tournament_date).strftime("%a").upper()  # e.g., MON, TUE
    avail_col = f"avail-{weekday_abbr}"

    if avail_col not in unscheduled.columns:
        st.warning(f"⚠️ Missing availability column: '{avail_col}'. Skipping tournament.")
        return pd.DataFrame(columns=dealers_df.columns)

    available = unscheduled[unscheduled[avail_col] == "Y"]

    # Prioritize mixed dealers for mixed games
    if "mixed" in game_type:
        available = available.sort_values(by="shift_type", key=lambda x: x != "mixed")

    # Shift-based filtering
    if start_hour >= 15:
        swing = available[available["shift_type"] == "swing"]
        day = available[available["shift_type"] == "day"]
        mixed = available[available["shift_type"] == "mixed"]
        eligible = pd.concat([swing, day, mixed])
    else:
        eligible = available[available["shift_type"].isin(["day", "mixed"])]

    return eligible.sort_values("ee_number")

# ---- Helper: Flexible Eligibility for TBD ----
def get_flexible_dealers(dealers_df, tournament, scheduled_dealers):
    # Normalize dealer column names
    dealers_df.columns = dealers_df.columns.str.strip().str.lower()

    game_type = tournament["event_name"].lower()
    tournament_date = tournament["date"]

    already_scheduled = set()
    for dealer_list in scheduled_dealers.values():
        already_scheduled.update(dealer_list)
    unscheduled = dealers_df[~dealers_df["ee_number"].isin(already_scheduled)]

    weekday_abbr = pd.to_datetime(tournament_date).strftime("%a").upper()
    avail_col = f"avail-{weekday_abbr}"

    if avail_col not in unscheduled.columns:
        st.warning(f"⚠️ Missing availability column: '{avail_col}'. Skipping tournament.")
        return pd.DataFrame(columns=dealers_df.columns)

    available = unscheduled[unscheduled[avail_col] == "Y"]

    if "mixed" in game_type:
        available = available.sort_values(by="shift_type", key=lambda x: x != "mixed")

    return available.sort_values("ee_number")

# ---- Core Assignment Logic ----
def build_daily_schedule(dealers_df, tournaments_df):
    scheduled_dealers = {}

    # Replace null times with default for sorting
    tournaments_df_sorted = tournaments_df.copy()
    tournaments_df_sorted["time"] = tournaments_df_sorted["time"].fillna(pd.Timestamp("12:00"))

    for _, tournament in tournaments_df_sorted.sort_values("time").iterrows():
        tournament_id = tournament["event_number"]

        try:
            demand = int(tournament["projection"])
        except (ValueError, TypeError):
            st.warning(f"⚠️ Invalid projection for event {tournament_id}. Skipping.")
            continue

        time_value = tournament["time"]

        if pd.isnull(time_value):
            eligible = get_flexible_dealers(dealers_df, tournament, scheduled_dealers)
        else:
            eligible = get_eligible_dealers(dealers_df, tournament, scheduled_dealers)

        assigned = eligible.head(demand)["ee_number"].tolist()
        scheduled_dealers[tournament_id] = assigned

    return scheduled_dealers

# ---- Streamlit UI ----
def run_schedule_builder():
    st.title("🗓 Schedule Builder")
    st.markdown("Assign dealers to tournaments based on shift, availability, and game type.")

    dealers_df = st.session_state.get("dealer_df")
    tournaments_df = st.session_state.get("tournament_df")

    if dealers_df is None or tournaments_df is None:
        st.warning("Missing dealer or tournament data. Please upload files on the Import page.")
        return

    # Normalize tournament column names
    tournaments_df.columns = tournaments_df.columns.str.strip().str.lower()

    # Convert time column to datetime, ignore TBD
    if "time" in tournaments_df.columns:
        def parse_time(val):
            if isinstance(val, str) and "TBD" not in val.upper():
                try:
                    return pd.to_datetime(val, format="%I:%M %p")
                except Exception:
                    return pd.NaT
            elif isinstance(val, datetime.time):
                return pd.Timestamp.combine(pd.Timestamp("1900-01-01"), val)
            elif isinstance(val, pd.Timestamp):
                return val
            else:
                return pd.NaT

        tournaments_df["time"] = tournaments_df["time"].apply(parse_time)
    else:
        st.warning("⏰ 'time' column not found. All tournaments will be treated as TBD.")
        tournaments_df["time"] = pd.NaT

    schedule = build_daily_schedule(dealers_df, tournaments_df)

    st.success("✅ Schedule built successfully!")
    for tid, assigned in schedule.items():
        tournament = tournaments_df[tournaments_df["event_number"] == tid].iloc[0]
        time_display = tournament["time"].strftime("%I:%M %p") if pd.notnull(tournament["time"]) else "TBD"
        st.markdown(f"### Event {tid} — {time_display} ({tournament['event_name']})")
        st.write(f"Assigned Dealers ({len(assigned)}): {assigned}")