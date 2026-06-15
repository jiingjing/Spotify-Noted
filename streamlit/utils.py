_ = """
utils.py
--------------
Helper functions for streamlit app

- load_data
- build_df
- filter_period
"""

import streamlit as st
import pandas as pd

_ = """
Data loading 
- select data from tracks_metadata
- select data from listening_history
- cache the data
"""


@st.cache_data
def load_data():
    conn = st.connection("mysql", type="sql")
    tracks = conn.query(
        "SELECT track_id, track_name, artist_name, album_name, in_library FROM tracks_metadata;",
        ttl=0,
    )
    history = conn.query("SELECT * FROM listening_history;", ttl=0)
    return tracks, history


_ = """
Merge data
- merge tracks_metadata and listening_history to one dataframe df
- time_stamp data to datetime
- create columns: year, hour, dow (date of week)
"""


@st.cache_data
def build_df() -> pd.DataFrame:
    tracks, history = load_data()
    df = history.merge(
        tracks[["track_id", "track_name", "artist_name", "album_name", "in_library"]],
        on="track_id",
        how="left",
    )
    df["time_stamp"] = pd.to_datetime(df["time_stamp"])
    df["year"] = df["time_stamp"].dt.year
    df["month"] = df["time_stamp"].dt.month
    df["hour"] = df["time_stamp"].dt.hour
    df["dow"] = df["time_stamp"].dt.day_name()

    df["in_library"] = df["in_library"].astype(bool)
    df["shuffle"] = df["shuffle"].astype(bool)
    df["skipped"] = df["skipped"].astype(bool)
    return df


_ = """
Period filter helper 
- filter df for the inputted time period 
- options: This year, Last 90d, All time
"""


def filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    now = df["time_stamp"].max()
    if period == "This year":
        return df[df["time_stamp"].dt.year == now.year]
    if period == "Last 90d":
        return df[df["time_stamp"] >= now - pd.Timedelta(days=90)]
    if period == "This month":
        return df[
            (df["time_stamp"].dt.month == now.month)
            & (df["time_stamp"].dt.year == now.year)
        ]
    if period == "Last 7d":
        return df[df["time_stamp"] >= now - pd.Timedelta(days=7)]
    return df  # all time


PERIOD_OPTIONS = ["All time", "This year", "Last 90d", "This month", "Last 7d"]
