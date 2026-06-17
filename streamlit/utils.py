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


@st.cache_data
def load_display_name():
    conn = st.connection("mysql", type="sql")
    display_name = conn.query(
        "SELECT name FROM display_name;",
        ttl=0,
    )
    return display_name.iloc[0]["name"]


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

_ = """
Footer navigation
"""

PAGES = [
    "0_cover.py",
    "1_toc.py",
    "2_prologue.py",
    "3_top_artists.py",
    "4_top_albums.py",
    "5_top_tracks.py",
    "6_habits.py",
    "7_timeline.py",
    "8_epilogue.py",
    "9_appendix.py",
]


def footer_nav(current):
    if current not in PAGES:
        return

    idx = PAGES.index(current)

    prev_page = PAGES[idx - 1] if idx > 0 else None
    next_page = PAGES[idx + 1] if idx < len(PAGES) - 1 else None
    toc_page = "1_toc.py"

    st.markdown("<hr style='margin-top:3rem;'>", unsafe_allow_html=True)

    if prev_page is None:
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Table of Contents", use_container_width=True):
                st.switch_page(toc_page)

        with col2:
            if next_page:
                if st.button("Next →", use_container_width=True):
                    st.switch_page(next_page)

    elif next_page is None:
        col1, col2 = st.columns([1, 1])

        with col1:
            if prev_page:
                if st.button("← Previous", use_container_width=True):
                    st.switch_page(prev_page)

        with col2:
            if st.button("Table of Contents", use_container_width=True):
                st.switch_page(toc_page)

    else:
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Previous", use_container_width=True):
                st.switch_page(prev_page)

        with col2:
            if st.button("Table of Contents", use_container_width=True):
                st.switch_page(toc_page)

        with col3:
            if st.button("Next →", use_container_width=True):
                st.switch_page(next_page)


_ = """
Time formatter helper 
- Format datetime 
- e.g. Wednesday 3rd May 2020 at 19:04
"""


def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    last = n % 10
    if last == 1:
        return f"{n}st"
    if last == 2:
        return f"{n}nd"
    if last == 3:
        return f"{n}rd"
    return f"{n}th"


def format_full_time(ts):
    day_name = ts.strftime("%A")
    day = ordinal(ts.day)
    month = ts.strftime("%B")
    year = ts.year

    time = ts.strftime("%I:%M%p").lstrip("0").lower()

    return f"{day_name} {day} {month} {year} at {time}"


def format_full_date(ts):
    day_name = ts.strftime("%A")
    day = ordinal(ts.day)
    month = ts.strftime("%B")
    year = ts.year

    return f"{day_name} {day} {month} {year}"
